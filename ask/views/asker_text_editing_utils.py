from contracts import contract
from ask.models import ChoiceSet
from signalbox.utils import supergetattr

@contract
def super_model_to_dict(modelinstance, fields=None):
    """
    # :param fields: [(key, lookup)] or [key]
    # :type fields: [tuple]|[str]
    :rtype: dict
    """
    if fields and isinstance(fields[0], basestring):
        fields = [(i, i) for i in fields]

    return {key: supergetattr(modelinstance, lookup) for key, lookup in fields}



@contract
def get_or_modify(klass, lookups, params):
    """
    :param klass: The django Class to use for lookup
    :type klass: a
    :param lookups: Key value pairs in a dictionary to use to lookup object
    :type lookups: dict
    :param params: Key value pairs in a dictionary to use to modify found object
    :type params: dict
    :rtype: tuple(b, bool)

    Returns
        - a new or modified instance of klass, with params set as specified.
        - boolean indicating whether object was modified
          (modified objects are automatically saved)
    """
    ob, created = klass.objects.get_or_create(**lookups)
    mods = []
    klassfields = map(lambda x: getattr(x, "name"), klass.__dict__['_meta'].fields)
    for k, v in params.iteritems():
        if k in klassfields:  # ignore extra fields by default
            mods.append(not getattr(ob, k) == v)
            setattr(ob, k, v)
    modified = bool(sum(mods))
    ob.save()

    return ob, modified


# helper to manipulate the dicts from yaml
@contract
def _find_choiceset(d):
    """
    :type d: dict
    :rtype: dict

    """
    if d.get('choiceset'):
        cs, _ = ChoiceSet.objects.get_or_create(name=d.get('choiceset'))
    else:
        cs = None
    d.update({'choiceset': cs})
    return d

