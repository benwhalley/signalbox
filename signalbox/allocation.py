"""Functions to allocate Memberships to a StudyCondition"""
from __future__ import division
from statlib import stats
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


def weighted_randomisation(membership):
    """Weighted randomisation of Membership to StudyCondition.

    Accepts a membership; returns a StudyCondition.
    """

    choices = [(i, i.weight) for i in membership.study.studycondition_set.all()]
    return weighted_choice(choices)


def balanced_groups_adaptive_randomisation(membership):
    """Simple adaptive randomisation, balancing across study conditions, respects Condition weights.

    The algorithm either:
        - performs weighted randomisation as normal (probability determined by randomisation_probability
          field on study model)
        - allocates to the group with the fewest participants

    However, when determining which is the smallest group we do respect the weighting property on
    Study conditions, so relative weights between groups should be preserved.
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
        counted = conditions.annotate(x=Count('membership')).order_by('?').order_by('x')
        weighted = [(min([1, i.x]) / min([1, i.weight]), i) for i in counted]
        has_fewest = [k for _, k in sorted(weighted)][0]
        return has_fewest


ALLOCATION_FUNCS = {
    'random': weighted_randomisation,
    'balanced_groups_adaptive_randomisation': balanced_groups_adaptive_randomisation,
}


def allocate(membership):
    """Accepts a Membership and a function used to randomise to a StudyCondition. Returns a tuple

    Return tuple is includes a success value (bool) and an optional error message.
    """""

    try:
        allocation_function = ALLOCATION_FUNCS[membership.study.allocation_method]
    except KeyError:
        allocation_function = weighted_randomisation

    if membership.condition:
        return (False, "Already allocated to a condition")

    if not membership.study.studycondition_set.all():
        return (False, "Study does not contain any conditions")

    membership.condition = allocation_function(membership)
    membership.date_randomised = membership.date_randomised or datetime.now()
    membership.save()
    return (True, "Added user to {}".format(membership.condition))
