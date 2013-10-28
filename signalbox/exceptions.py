
class SignalBoxException(Exception):
    pass

class DataProtectionException(SignalBoxException):
    pass

class CategoryErrorException(SignalBoxException):
    pass

class SuspiciousActivityException(SignalBoxException):
    pass
