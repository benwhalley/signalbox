#!/usr/bin/env python
# -*- coding: utf-8 -*-

import markdown
from django.utils.safestring import mark_safe
from django.template import Context, Template
from fnmatch import fnmatch
from django.http import Http404
import os
import sys
from django.core.exceptions import ImproperlyConfigured
import collections


safe_help = lambda x: mark_safe(markdown.markdown(x))

dict_map = lambda f, d: {k: f(v) for k, v in d.items()}




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

