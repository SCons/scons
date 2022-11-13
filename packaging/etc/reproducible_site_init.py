"""
Use this file as your ~/.site_scons/scons_init.py to enable reprodicble builds as described at
https://reproducible-builds.org/specs/source-date-epoch/
"""

import os
import SCons.Environment

old_init = SCons.Environment.Base.__init__


def new_init(self, **kw):
    """
    This logic will add SOURCE_DATE_EPOCH to the execution environment used to run
    all the build commands.
    """
    print("In my custom init")
    old_init(self, **kw)
    if 'SOURCE_DATE_EPOCH' in os.environ:
        self._dict['ENV']['SOURCE_DATE_EPOCH'] = os.environ['SOURCE_DATE_EPOCH']


SCons.Environment.Base.__init__ = new_init
