from datetime import date, datetime, timedelta, time
import dateutil
from dateutil.relativedelta import *
import dateutil.parser as dateparser
from pyparsing import *
import calendar



NOW =  datetime.now()


CL = CaselessLiteral
plural = lambda s : Combine(CL(s) + Optional(CL("s")))

# grammar definitions
year, month, week, day, hour, minute, second = [plural(i) for
    i in "year month week day hour minute second".split()]

at_ = Suppress(oneOf(["at", "in the"], caseless=True))

year.setParseAction(replaceWith(relativedelta(years=1)))
month.setParseAction(replaceWith(relativedelta(months=1)))
week.setParseAction(replaceWith(relativedelta(weeks=1)))
day.setParseAction(replaceWith(relativedelta(days=1)))
hour.setParseAction(replaceWith(relativedelta(hours=1)))
minute.setParseAction(replaceWith(relativedelta(minutes=1)))
second.setParseAction(replaceWith(relativedelta(seconds=1)))

# Quantifiers
integer = Word(nums).setParseAction(lambda t: int(t[0]))
a_qty = CL("a").setParseAction(replaceWith(1))
next_ = CL("next").setParseAction(replaceWith(1))
last_ = CL("last").setParseAction(replaceWith(-1))
in_ = CL("in").setParseAction(replaceWith(1))('in')
ago_ = CL("ago").setParseAction(replaceWith(-1))
after_ = CL("after").setParseAction(replaceWith(1))
qty = MatchFirst(integer | a_qty | next_ | last_ )


quantified_offset = ( Optional(in_ | after_) + qty('qty') +
        (year | month | week | day | hour | minute | second )('unit') +
        Optional(ago_, default=1)('futureorpast')
        )
quantified_offset.setParseAction(lambda x: x.unit * x.qty * x.futureorpast)


WEEKDAYNAMES = "MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY SUNDAY".split()
RELATIVE_DAYS = [MO, TU, WE, TH, FR, SA, SU]
weekday = MatchFirst(
    [( CL(i) | CL(i[:3]) | CL(i[:4]) ).setParseAction(replaceWith(j))
        for i, j in zip(WEEKDAYNAMES, RELATIVE_DAYS)]
    )

weekdayoffset = ( (next_ | last_)('multiplier') + weekday('dayofweek') )

def _process_day_of_week_offset_with_sameday_correction(toks):
    """If we specifiy next Thur, and today is Thur, we mean in 7 days.

    That is, not today, which the the dateutil default.
    """
    samedaymultiplier = (toks.dayofweek == RELATIVE_DAYS[NOW.weekday()]) and 2 or 1
    actual_multiplier = samedaymultiplier * toks.multiplier
    return relativedelta(weekday=toks.dayofweek(actual_multiplier))

weekdayoffset.setParseAction(_process_day_of_week_offset_with_sameday_correction)


# set some colloquial timedeltas
today = CL('today').setParseAction(replaceWith(relativedelta(days=0)))
tomorrow = CL('tomorrow').setParseAction(replaceWith(relativedelta(days=1)))
yesterday = CL('yesterday').setParseAction(relativedelta(days=-1))

whenjunk = Suppress(ZeroOrMore((CL('on') | CL('a'))))

relativeweekday = whenjunk + weekday('dayofweek') + Optional(quantified_offset('quantified_offset'), default=relativedelta())
relativeweekday.addParseAction(lambda x: relativedelta(weekday=x.dayofweek) + x.quantified_offset )
relative_specific_day = today | tomorrow | yesterday

relative_date = ( relative_specific_day | weekdayoffset | quantified_offset | relativeweekday )
relative_date.setParseAction( lambda x: NOW + x[0] )


# parse a calendar date if we find one instead...
month_matches_ = [MatchFirst([CL(j), CL(j[:3])]).setParseAction(replaceWith(i))
    for i, j in list(enumerate(calendar.month_name))[1:]]
monthname = MatchFirst(month_matches_).setResultsName('month')
nth_ = Suppress(oneOf(['st', 'nd', 'rd','th' ]))
day_matches_ = [(CL(str(i))  + nth_ ).setParseAction(lambda t:int(t[0]))
    for i in reversed(range(1,32))]
monthday = (MatchFirst(day_matches_)).setResultsName('day')
year = Word(nums,exact=4).setResultsName('year').setParseAction(lambda y: int(y[0]) )


calendardate = Optional(Suppress(CL('on'))) + OneOrMore(~at_ + Word(nums+alphas+"/\:.,") )('datestring')
calendardate.setParseAction(lambda x: dateparser.parse(" ".join(x.datestring)))

# calculate time now
TIMSEP = Suppress(oneOf([':', '.']))

# 24 hour clock parsing
timepart = Word(nums, max=2).setParseAction(lambda a: int(a[0]))
timepart.parseString("22")
miltime = timepart('hour') + Optional(TIMSEP) + timepart('minute')
miltime.setParseAction(lambda a: time(hour=a.hour, minute=a.minute))

# twelve hour clock parsing
ampm = (CL("am").setParseAction(replaceWith(0)) | CL("pm").setParseAction(replaceWith(1)))("pm")
twelvehour = timepart('hour') + Optional(TIMSEP) + Optional(timepart('minute'), default=0) + ampm
twelvehour.setParseAction(lambda x: time(hour=x.hour + 12*x.pm , minute=x.minute))
twelvehour.parseString("12am")


# name some specific times
noon = oneOf(["Noon", "midday", "mid day"], caseless=True).setParseAction(replaceWith( time(hour=12, minute=0) ))
# midnight is 23:59 to - for reasons, see _process_date_time() and offset calculation
midnight = CL("Midnight").setParseAction(replaceWith( time(hour=23, minute=59) ))
morn = CL("morning").setParseAction(replaceWith( time(hour=10, minute=0) ))
afternoon = CL("afternoon").setParseAction(replaceWith( time(hour=15, minute=0) ))
eve = oneOf(["eve", "evening"], caseless=True).setParseAction(replaceWith( time(hour=19, minute=0) ))
now_ = oneOf(["now", "immediate", "immediately"], caseless=True).setParseAction(replaceWith( time(hour=NOW.hour, minute=NOW.minute, second=NOW.second) ))
specific_times = now_ | noon | midnight | morn | eve | afternoon

timespec = ( Optional(Suppress(at_)) + (specific_times | twelvehour | miltime  ) )('time')

date_ = calendardate('date')
time_ = timespec('time')
defaulttime = Optional(time_, default=[time(NOW.hour, NOW.minute, NOW.second, NOW.microsecond)])


def get_offset(t):
    n = NOW
    if (t.hour < n.hour):
        return relativedelta(hours=24)
    return relativedelta(hours=0)


def _process_date_time(toks):
    if toks.time and toks.date:
        t = toks.time[0]
        # correct to avoid times which have already passed
        offset = toks.date and toks.date <= NOW and get_offset(t) or relativedelta(hours=0)
        toks['datetime'] = toks.date.replace(
            hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond) + offset
    else:
        toks['datetime'] = toks.date


def _proc_time_only(toks):
    t = toks.time[0]
    # correct to avoid times which have already passed
    offset = get_offset(t)
    toks['datetime'] = NOW.replace(hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond) + offset


# create the main expressions
absolute = date_ + defaulttime | defaulttime + date_
absolute.setParseAction(_process_date_time)

relative = relative_date('date') | relative_date('date') + time_
relative.setParseAction(_process_date_time)

timeonly = time_ + StringEnd()
timeonly.setParseAction(_proc_time_only)


# The combined expression
singledate = timeonly | relative | absolute


every_ = oneOf(["every", "each"], caseless=True).setParseAction(replaceWith(True))('repeat')
from_ = oneOf(['from', 'in'], caseless=True).setParseAction(replaceWith(True))('from')


from dateutil.rrule import *
monthly_ = month.setParseAction(replaceWith(MONTHLY))('monthly')
weekly_ = week.setParseAction(replaceWith(WEEKLY))('weekly')
for_ = oneOf(['for', "*"])
count_ =  ~from_ + for_ + integer('qty') + (monthly_ | weekly_ )('unit')

repeating = every_ + (weekday('weekday') | monthly_  | weekly_ ) + Optional(count_)('count') + Optional(from_ + relative_date)('fromdate') | singledate('singledate')

def _proc_repeats(toks):
    if not toks.singledate:
        interval = toks.weekly_ or toks.monthly or WEEKLY
        kwargs = {}
        kwargs['byweekday'] = toks.weekday or None
        kwargs['dtstart'] = toks.dtstart or NOW
        kwargs['count'] = 3 #toks.qty or 3
        return list(rrule(interval, **kwargs))

repeating.setParseAction(_proc_repeats)


print repeating.parseString("now")
print repeating.parseString("every monday from thursday")
print repeating.parseString("every monday for 2 weeks from 1 jun 2014")
