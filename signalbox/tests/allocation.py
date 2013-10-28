"Commented out because this test is so slow to run in routine work."
from __future__ import division
import random
from itertools import permutations
from uuid import uuid4
from operator import gt, mul
import itertools
import random
from statlib import stats
from collections import Counter

from django.test import TestCase
from django.contrib.auth.models import User

from signalbox.models import Study, Membership
from signalbox.allocation import allocate
from signalbox.tests.helpers import make_user


def _get_p_for_allocation(study, users, ratio):
    SAMPLESIZE = len(users)
    groups = list(study.studycondition_set.all())
    study.membership_set.all().delete()

    [setattr(i, 'weight', w) for i, w in zip(groups, ratio)]
    [i.save() for i in groups]

    normalisedweights = [i / sum(ratio) for i in ratio]
    expected = dict([(j, int(SAMPLESIZE * i)) for i, j in zip(normalisedweights, ratio)])

    mems = [Membership(study=study, user=user) for user in users]
    [allocate(i) for i in mems]

    # make each group min = 1 because otherwise chisq can blow up
    observed = {i.weight: min([1, i.membership_set.all().count()]) for i in groups}
    ex_ob = [(expected[i], observed[i]) for i in observed.keys()]

    chi, p = stats.lchisquare(*zip(*ex_ob))

    return p


class Test_Allocation(TestCase):
    """Various tests of randomising Memberships to StudyConditions."""

    fixtures = ['test.json', ]

    def test_allocation(self):
        """Simulate studies and check we have sane allocation ratios at N=30."""

    def test_allocation(self):
        study = Study.objects.get(slug='test-allocation-study')
        study.auto_randomise = False
        # note - we just test this, because it uses weighted_ranomisation too

        User.objects.filter(username__startswith="0").delete()
        users = [make_user({'username': i, 'email': i + "@TEST.COM", 'password': i})
            for i in [str(random.random()) for i in range(30)]]

        # repeat the test with different group weightings
        ratios = list(permutations([1, 2, 3, 4], 3))
        # [(1, 2, 3), (1, 2, 4), (1, 3, 2), (1, 3, 4) ... etc]

        study.allocation_method = "balanced_groups_adaptive_randomisation"
        study.randomisation_probability = .5

        study.save()



        meanp = stats.lmean([.00001] + [_get_p_for_allocation(study, users, i) for i in ratios])
        assert meanp > .05

        study.allocation_method = "random"
        study.save()
        meanp = stats.lmean([.00001] + [_get_p_for_allocation(study, users, i) for i in ratios])
        assert meanp > .05

