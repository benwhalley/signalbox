#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contracts import contract
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.template import Context, Template
from django.utils.safestring import mark_safe
from fnmatch import fnmatch
import collections
import markdown
import os
import sys


safe_help = lambda x: mark_safe(markdown.markdown(x))
dict_map = lambda f, d: {k: f(v) for k, v in d.items()}





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

def walk(x, action, format, meta):
  """Walk a tree, applying an action to every object.
  Returns a modified tree.
  """
  if isinstance(x, list):
    array = []
    for item in x:
      if isinstance(item, dict):
        if item == {}:
          array.append(walk(item, action, format, meta))
        else:
          for k in item:
            res = action(k, item[k], format, meta)
            if res is None:
              array.append(walk(item, action, format, meta))
            elif isinstance(res, list):
              for z in res:
                array.append(walk(z, action, format, meta))
            else:
              array.append(walk(res, action, format, meta))
      else:
        array.append(walk(item, action, format, meta))
    return array
  elif isinstance(x, dict):
    obj = {}
    for k in x:
      obj[k] = walk(x[k], action, format, meta)
    return obj
  else:
    return x



def int_or_string(string):
    try:
        return int(string)
    except:
        return string


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def supergetattr(obj, field, default=None, required=False, call=True):
    """
    Pass an object and a string dotted path to the desired value within it.

    Return a default if not found, or raise an Exception if required=True
    and the object is not found.
    By default, also call the value if it is callable.

    """

    fields = field.split(".")
    try:
        for f in fields:
            obj = getattr(obj, f)
        if callable(obj):
            return obj()
        return obj
    except AttributeError:
        if not required:
            return default
        else:
            raise


def render_string_with_context(string, context=None):
    return Template(string).render(Context(context or {}))


class conditional_decorator(object):
    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            # Return the function unchanged, not decorated.
            return func
        return self.decorator(func)


def get_object_from_queryset_or_404(queryset, **kwargs):
    try:
        return queryset.get(**kwargs)
    except queryset.model.DoesNotExist:
        raise Http404

