"""
Parser to convert a conversational time reference such as "in a minute" or
"tomorrow at midnight" and convert it to a Python datetime.  The returned
ParseResults object contains the results name "timeOffset" containing
the timedelta, and "calculatedTime" containing the computed time relative
to datetime.now().

Inspired by Paul McGuire's example, but simplified for a simpler mind and
now using python-dateutils The original work is at

http://pyparsing.wikispaces.com/file/detail/deltaTime.py

This work also released under a CC license:
http://creativecommons.org/licenses/by-sa/2.5/


Some examples:

>>> test_NTime('now')
{'dt': datetime.datetime(2005, 6, 17, 19, 30), 'delta': relativedelta()}

>>> test_NTime('11am')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('11am')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('in the morning')
{'dt': datetime.datetime(2005, 6, 18, 10, 0), 'delta': relativedelta(hours=+14, minutes=+30)}

>>> test_NTime('in the evening')
{'dt': datetime.datetime(2005, 6, 17, 19, 0), 'delta': relativedelta(minutes=-30)}

>>> test_NTime('in the afternoon')
{'dt': datetime.datetime(2005, 6, 18, 15, 0), 'delta': relativedelta(hours=+19, minutes=+30)}

>>> test_NTime('midnight')
{'dt': datetime.datetime(2005, 6, 17, 23, 59), 'delta': relativedelta(hours=+4, minutes=+29)}

>>> test_NTime('tomorrow at midnight')
{'dt': datetime.datetime(2005, 6, 18, 23, 59), 'delta': relativedelta(days=+1, hours=+4, minutes=+29)}

>>> test_NTime('tomorrow at 23:00')
{'dt': datetime.datetime(2005, 6, 18, 23, 0), 'delta': relativedelta(days=+1, hours=+3, minutes=+30)}

>>> test_NTime('in 10 seconds')
{'dt': datetime.datetime(2005, 6, 17, 19, 30, 10), 'delta': relativedelta(seconds=+10)}

>>> test_NTime('in 10 minutes')
{'dt': datetime.datetime(2005, 6, 17, 19, 40), 'delta': relativedelta(minutes=+10)}

>>> test_NTime('in 2 days')
{'dt': datetime.datetime(2005, 6, 19, 19, 30), 'delta': relativedelta(days=+2)}

>>> test_NTime('10 minutes ago')
{'dt': datetime.datetime(2005, 6, 17, 19, 20), 'delta': relativedelta(minutes=-10)}

>>> test_NTime('10 weeks ago')
{'dt': datetime.datetime(2005, 4, 8, 19, 30), 'delta': relativedelta(months=-2, days=-9)}

>>> test_NTime('tomorrow at 6am')
{'dt': datetime.datetime(2005, 6, 18, 6, 0), 'delta': relativedelta(hours=+10, minutes=+30)}

>>> test_NTime('in 2 days at 11am')
{'dt': datetime.datetime(2005, 6, 19, 11, 0), 'delta': relativedelta(days=+1, hours=+15, minutes=+30)}

>>> test_NTime('1/12/2012')
{'dt': datetime.datetime(2012, 1, 12, 19, 30), 'delta': relativedelta(years=+6, months=+6, days=+26)}

>>> test_NTime('on June 29th 2013 in the morning')
{'dt': datetime.datetime(2013, 6, 29, 10, 0), 'delta': relativedelta(years=+8, days=+11, hours=+14, minutes=+30)}

>>> test_NTime('June 29th 2013 at 11am')
{'dt': datetime.datetime(2013, 6, 29, 11, 0), 'delta': relativedelta(years=+8, days=+11, hours=+15, minutes=+30)}

>>> test_NTime('tomorrow at 11:00')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('today at 11:00')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('today at 11:00am')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('today at 11:00pm')
{'dt': datetime.datetime(2005, 6, 17, 23, 0), 'delta': relativedelta(hours=+3, minutes=+30)}

>>> test_NTime('today at 11am')
{'dt': datetime.datetime(2005, 6, 18, 11, 0), 'delta': relativedelta(hours=+15, minutes=+30)}

>>> test_NTime('today at 11pm')
{'dt': datetime.datetime(2005, 6, 17, 23, 0), 'delta': relativedelta(hours=+3, minutes=+30)}

>>> test_NTime('next monday at 11am')
{'dt': datetime.datetime(2005, 6, 20, 11, 0), 'delta': relativedelta(days=+2, hours=+15, minutes=+30)}

>>> test_NTime('next tuesday at 11am')
{'dt': datetime.datetime(2005, 6, 21, 11, 0), 'delta': relativedelta(days=+3, hours=+15, minutes=+30)}

>>> test_NTime('in 1 week at 15.00')
{'dt': datetime.datetime(2005, 6, 24, 15, 0), 'delta': relativedelta(days=+6, hours=+19, minutes=+30)}

>>> test_NTime('friday in 1 week at 11')
{'dt': datetime.datetime(2005, 6, 24, 19, 30), 'delta': relativedelta(days=+7)}

>>> test_NTime('wednesday in 3 weeks')
{'dt': datetime.datetime(2005, 7, 13, 19, 30), 'delta': relativedelta(days=+26)}

>>> test_NTime('a wed in 3 weeks')
{'dt': datetime.datetime(2005, 7, 13, 19, 30), 'delta': relativedelta(days=+26)}

>>> test_NTime('on a fri in 4 months at 02:00')
{'dt': datetime.datetime(2005, 10, 21, 2, 0), 'delta': relativedelta(months=+4, days=+3, hours=+6, minutes=+30)}

>>> test_NTime('next sunday at noon')
{'dt': datetime.datetime(2005, 6, 19, 12, 0), 'delta': relativedelta(days=+1, hours=+16, minutes=+30)}

>>> test_NTime('next sunday at mid day')
{'dt': datetime.datetime(2005, 6, 19, 12, 0), 'delta': relativedelta(days=+1, hours=+16, minutes=+30)}

>>> test_NTime('next sunday at midday')
{'dt': datetime.datetime(2005, 6, 19, 12, 0), 'delta': relativedelta(days=+1, hours=+16, minutes=+30)}

>>> test_NTime('next fri at midnight')
{'dt': datetime.datetime(2005, 6, 24, 23, 59), 'delta': relativedelta(days=+7, hours=+4, minutes=+29)}

>>> test_NTime('next fri morning')
{'dt': datetime.datetime(2005, 6, 24, 10, 0), 'delta': relativedelta(days=+6, hours=+14, minutes=+30)}

>>> test_NTime('next fri evening')
{'dt': datetime.datetime(2005, 6, 24, 19, 0), 'delta': relativedelta(days=+6, hours=+23, minutes=+30)}

>>> test_NTime('fri in 2 weeks in the evening')
{'dt': datetime.datetime(2005, 7, 1, 19, 0), 'delta': relativedelta(days=+13, hours=+23, minutes=+30)}

>>> test_NTime('a fri in 2 weeks in the evening')
{'dt': datetime.datetime(2005, 7, 1, 19, 0), 'delta': relativedelta(days=+13, hours=+23, minutes=+30)}



"""

from datetime import date, datetime, timedelta, time
import dateutil
from dateutil.relativedelta import *
import dateutil.parser as dateparser
from pyparsing import *
import calendar

__all__ = ["NTime"]


class NTime(object):
    """
    Wraps a pyparsing object, accessible via the 'parser' attribute.

    The reason for wrapping in a separate class is to allow passing in a
    reference datetime at the point of execution (these otherwise get
    bound into the pyparsing class when the module is first loaded).
    """

    def __init__(self, reftime=None):

        NOW = reftime or datetime.now()
        self.NOW = NOW

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

        relative = relative_date('date') + time_ | relative_date('date')
        relative.setParseAction(_process_date_time)

        timeonly = time_ + StringEnd()
        timeonly.setParseAction(_proc_time_only)


        # The combined expression
        self.parser = timeonly | relative | absolute




if __name__ == "__main__":
    import doctest

    def test_NTime(string, relativeto=None):
        n = datetime(2005, 6, 17, 19, 30, 0)
        ntime = NTime(reftime=n).parser
        x = ntime.parseString(string).datetime
        return {'dt': x, 'delta': relativedelta(x, n)}

    doctest.testmod()





