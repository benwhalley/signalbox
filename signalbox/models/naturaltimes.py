from signalbox.utilities.delta_time import NTime


def parse_natural_date(date_str):
    """Date/time as a str -> (datetime or None, error string or None)"""

    ntime = NTime().parser
    try:
        return (ntime.parseString(date_str).datetime, None)
    except Exception as e:
        return (None, date_str + ": " + unicode(e))
