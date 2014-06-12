"""Functions to allocate Memberships to a StudyCondition"""
from __future__ import division
from stats import stats
from collections import Counter
from datetime import datetime
import random
from django.db.models import Count
from itertools import chain, repeat, permutations


def weighted_choice(items):
    """Returns 1 of items: a list of tuples in the form (item, weight)"""

    things, weights = zip(*items)
    pools = list(chain(*[list(repeat(i, w)) for i, w in items]))
    return random.choice(list(pools))

"""

>N = 30
>choices = ["A", "B", "C"]
>weight_list = list(permutations([1,2,3,4,5], len(choices)))
>pvals = []
>for weights in weight_list:
>    stweights = [i / (sum(weights)) for i in weights]
>
>    counts = Counter([weighted_choice(zip(choices, weights)) for i in xrange(N)])
>    expected = {c: int(N * w) for w, c in zip(stweights, choices)}
>
>    expected_observed = {i: (j, expected[i]) for i,j in counts.items()}
>    chi, p = stats.lchisquare(*zip(*expected_observed.values()))
>    pvals.append(p)
>
>assert stats.lmean(pvals) > .1

"""


def balanced_groups_adaptive_randomisation(membership):
    """Simple adaptive randomisation, balancing allocations but respecting Condition weights.

    The algorithm either:
        - performs weighted randomisation as normal (probability determined by randomisation_probability
          field on study model)
        - allocates to the group with the fewest participants (weighted by Condition weights)
    """

    p_randomise = membership.study.randomisation_probability
    conditions = membership.study.studycondition_set.all()

    if p_randomise > random.uniform(0, 1):
        # be random
        choices = [(i, i.weight) for i in conditions]
        choice = weighted_choice(choices)
        return choice
    else:
        # be deterministic
        total_weight = sum([i.weight for i in conditions])
        counted = [(cond, cond.membership_set.all().count()) for cond in conditions]
        weighted_counts = [(cond, count / (cond.weight/total_weight))
            for cond, count in counted]
        sorted_weighted = sorted(weighted_counts, key=lambda x: x[1])
        has_fewest = sorted_weighted[0][0]

        return has_fewest


def allocate(membership):
    """Accepts a Membership and a function used to randomise to a StudyCondition. Returns a tuple

    Return tuple is includes a success value (bool) and an optional error message.
    """""

    if membership.condition:
        return (False, "Already allocated to a condition")

    if not membership.study.studycondition_set.all():
        return (False, "Study does not contain any conditions")

    membership.condition = balanced_groups_adaptive_randomisation(membership)
    membership.date_randomised = membership.date_randomised or datetime.now()
    membership.save()
    return (True, "Added user to {}".format(membership.condition))
