"""A load of cruft to allow pipe literal strings for longer questions."""

import yaml
from yaml.emitter import *
from yaml.serializer import *
from yaml.representer import *
from yaml.resolver import *


class MySafeRepresenter(SafeRepresenter):
    pass
    def represent_scalar(self, tag, value, style=None):
        old = SafeRepresenter()

        if len(value.split("\n")) > 1:
            return old.represent_scalar('tag:yaml.org,2002:str', value, style='|')
        else:
            return old.represent_scalar('tag:yaml.org,2002:str', value)

class MyDumper(Emitter, Serializer, MySafeRepresenter, Resolver):

    def __init__(self, stream,
            default_style=None, default_flow_style=None,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=True,
            version=None, tags=None):
        Emitter.__init__(self, stream, canonical=canonical,
                indent=indent, width=width,
                allow_unicode=allow_unicode, line_break=line_break)
        Serializer.__init__(self, encoding=encoding,
                explicit_start=explicit_start, explicit_end=explicit_end,
                version=version, tags=tags)
        MySafeRepresenter.__init__(self, default_style=default_style,
                default_flow_style=default_flow_style)
        Resolver.__init__(self)




