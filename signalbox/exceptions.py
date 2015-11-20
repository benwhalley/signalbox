class SignalBoxMultipleErrorsException(Exception):
    def __init__(self, errors):
        self.errors = errors
    def __str__(self):
        return repr(self.errors)

class SignalBoxException(Exception):
    pass

class DataProtectionException(SignalBoxException):
    pass

class CategoryErrorException(SignalBoxException):
    pass

class SuspiciousActivityException(SignalBoxException):
    pass
