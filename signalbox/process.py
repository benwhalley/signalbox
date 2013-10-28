"""Adapted from Satchless: https://raw.github.com/mirumee/satchless/master/satchless/process/__init__.py

Copyright (c) 2010-2012, Mirumee Software
All rights reserved.
"""


class InvalidData(Exception):
    """
    Raised for by step validation process
    """
    pass


class Step(object):
    """
    A single step in a multistep process
    """

    def index(self):
        raise NotImplementedError()  # pragma: no cover

    def validate(self):
        raise NotImplementedError()  # pragma: no cover


class ProcessManager(object):
    """
    A multistep process handler
    """
    def __iter__(self):
        raise NotImplementedError()  # pragma: no cover

    def __getitem__(self, key):
        return list(self)[key]

    def progress(self):
        """Return tuples for each step with second element indicating validity."""
        return [(i, i.validate(self), i.all_questions_complete(self)) for i in self]

    def step_availability(self):
        """Return whether a step should be available or not, and whether all questions have non-null responses."""
        if not self.asker.steps_are_sequential:
            return [(i, True) for i in self]
        steps, isvalids, iscompletes = zip(*self.progress())
        seqs = [((True,) + isvalids[0:i]) for i in range(1, len(isvalids) + 1)]
        isvalids = [bool(min((i[0:-1]))) for i in seqs]
        return zip(steps, isvalids, iscompletes)

    def validate_step(self, step, *args, **kwargs):
        try:
            step.validate(*args, **kwargs)
        except InvalidData:
            return False
        return True

    def get_next_step(self, *args, **kwargs):
        for step in self:
            if not step.validate(*args, **kwargs):
                return step

    def get_errors(self, *args, **kwargs):
        errors = {}
        for step in self:
            try:
                step.validate(*args, **kwargs)
            except InvalidData as error:
                errors[str(step)] = error
        return errors

    def is_complete(self, *args, **kwargs):
        steps, done, _ = zip(*self.progress())
        return bool(min(done))
