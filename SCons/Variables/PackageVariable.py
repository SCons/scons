# MIT License
#
# Copyright The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Variable type for package Variables.

To be used whenever a 'package' may be enabled/disabled and the
package path may be specified.

Given these options ::

   x11=no   (disables X11 support)
   x11=yes  (will search for the package installation dir)
   x11=/usr/local/X11 (will check this path for existence)

Can be used as a replacement for autoconf's ``--with-xxx=yyy`` ::

    opts = Variables()
    opts.Add(
        PackageVariable(
            key='x11',
            help='use X11 installed here (yes = search some places)',
            default='yes'
        )
    )
    env = Environment(variables=opts)
    if env['x11'] is True:
        dir = ...  # search X11 in some standard places ...
        env['x11'] = dir
    if env['x11']:
        ...  # build with x11 ...
"""

import os
from typing import Callable, Optional, Tuple

import SCons.Errors

__all__ = ['PackageVariable',]

ENABLE_STRINGS = ('1', 'yes', 'true',  'on', 'enable', 'search')
DISABLE_STRINGS = ('0', 'no',  'false', 'off', 'disable')

def _converter(val):
    """Convert package variables.

    Returns True or False if one of the recognized truthy or falsy
    values is seen, else return the value unchanged (expected to
    be a path string).
    """
    lval = val.lower()
    if lval in ENABLE_STRINGS:
        return True
    if lval in DISABLE_STRINGS:
        return False
    return val


def _validator(key, val, env, searchfunc) -> None:
    """Validate package variable for valid path.

    Checks that if a path is given as the value, that pathname actually exists.
    """
    # NOTE: searchfunc is currently undocumented and unsupported
    if env[key] is True:
        if searchfunc:
            env[key] = searchfunc(key, val)
            # TODO: need to check path, or be sure searchfunc raises.
    elif env[key] and not os.path.exists(val):
        msg = f'Path does not exist for variable {key!r}: {val!r}'
        raise SCons.Errors.UserError(msg) from None


# lint: W0622: Redefining built-in 'help' (redefined-builtin)
def PackageVariable(
    key: str, help: str, default, searchfunc: Optional[Callable] = None
) -> Tuple[str, str, str, Callable, Callable]:
    """Return a tuple describing a package list SCons Variable.

    The input parameters describe a 'package list' variable. Returns
    a tuple with the correct converter and validator appended.
    The result is usable as input to :meth:`~SCons.Variables.Variables.Add`.

    A 'package list' variable may either be a truthy string from
    :const:`ENABLE_STRINGS`, a falsy string from
    :const:`DISABLE_STRINGS`, or a pathname string.
    This information is appended to *help* using only one string
    each for truthy/falsy.
    """
    # NB: searchfunc is currently undocumented and unsupported
    help = '\n    '.join((help, f'( yes | no | /path/to/{key} )'))
    return (
        key,
        help,
        default,
        lambda k, v, e: _validator(k, v, e, searchfunc),
        _converter,
    )

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
