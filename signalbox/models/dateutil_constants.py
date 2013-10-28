# # This is weird, but you need to pass an integer to represent the frequency of repeating
# # to rrule(). This is copied and pasted from the rrule function because I don't want to have
# # to remember the mapping.

(YEARLY,
 MONTHLY,
 WEEKLY,
 DAILY,
 HOURLY,
 MINUTELY,
 SECONDLY) = range(7)

FREQ_MAP = {"YEARLY": YEARLY,
             "MONTHLY": MONTHLY,
             "WEEKLY": WEEKLY,
             "DAILY": DAILY,
             "HOURLY": HOURLY,
             "MINUTELY": MINUTELY,
             "SECONDLY": SECONDLY}

MO, TU, WE, TH, FR, SA, SU = range(7)

WEEKDAY_MAP = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}
WEEKDAY_TUPLES = [(v,k) for k,v in WEEKDAY_MAP.items()]
WEEKDAY_TUPLES = sorted(WEEKDAY_TUPLES)
WEEKDAY_TUPLES = [(k,k) for j,k in WEEKDAY_TUPLES]

