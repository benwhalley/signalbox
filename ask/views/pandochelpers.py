import sys
import json


def get_meta_tuple(metaitem):
  # allow grabbing numbers XXX todo
  k, content = metaitem
  if "MetaString" in content:
      return (k, content['MetaString'])

  if "MetaInlines" in content:
      isuseful = lambda x: bool([i in x for i in ['Str', 'Space', 'Code']])
      fixspace = lambda x: 'Space' in x and " " or x.values()[0]
      return (k, "".join(map(fixspace, filter(isuseful, content['MetaInlines']))))

  if "MetaBool" in content:
      return (k, content['MetaBool'])




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


def stringify(x):
  """Walks the tree x and returns concatenated string content,
  leaving out all formatting.
  """
  result = []
  def go(key, val, format, meta):
    if key == 'Str':
      result.append(val)
    if key == 'MetaBool':
      result.append(val)
    elif key == 'Code':
      result.append(val[1])
    elif key == 'Math':
      result.append(val[1])
    elif key == 'LineBreak':
      result.append(" ")
    elif key == 'Space':
      result.append(" ")

  walk(x, go, "", {})
  return ''.join(result)

