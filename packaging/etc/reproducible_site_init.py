"""
Use this file as your site_init.py in a site directory,
to enable reprodicble builds as described at
https://reproducible-builds.org/specs/source-date-epoch/
"""

import os
import SCons.Environment

old_init = SCons.Environment.Base.__init__

print(
    "Adding logic to propagate SOURCE_DATE_EPOCH from the shell environment when building with SCons"
)


def new_init(self, **kw):
    """Replacement Environment initializer.

    When this is monkey-patched into :class:`SCons.Environment.Base` it adds
    ``SOURCE_DATE_EPOCH`` to the execution environment used to run
    all external build commands; the original iinitializer is called first.
    """
    old_init(self, **kw)
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is not None:
        self._dict["ENV"]["SOURCE_DATE_EPOCH"] = epoch


SCons.Environment.Base.__init__ = new_init
