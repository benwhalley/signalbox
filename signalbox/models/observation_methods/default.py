from datetime import datetime


def link(self):
    return False


def update(self, success_status):
    """Updates the Observation when do() is called.

    NOTE this gets overwritten by some Observation subclasses below"""

    self.touch()
    self.increment_attempts()
    return self.save()


def touch(self):
    """Set the last_attempt for the Observation to the current datetime."""

    self.last_attempted = datetime.now()
    return self.save()


def do(self):
    """By default, nothing should happen except recording that we tried."""

    self.touch()
    self.increment_attempts()
    return self.save()
