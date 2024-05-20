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

"""Variable type for List Variables.

A list variable may given as 'all', 'none' or a list of names
separated by comma. After the variable has been processed, the variable
value holds either the named list elements, all list elements or no
list elements at all.

Usage example::

    list_of_libs = Split('x11 gl qt ical')

    opts = Variables()
    opts.Add(
        ListVariable(
            'shared',
            help='libraries to build as shared libraries',
            default='all',
            elems=list_of_libs,
        )
    )
    env = Environment(variables=opts)
    for lib in list_of_libs:
        if lib in env['shared']:
            env.SharedObject(...)
        else:
            env.Object(...)
"""

# Known Bug: This should behave like a Set-Type, but does not really,
# since elements can occur twice.

import collections
from typing import Callable, List, Optional, Tuple, Union

import SCons.Util

__all__ = ['ListVariable',]


class _ListVariable(collections.UserList):
    """Internal class holding the data for a List Variable.

    The initializer accepts two arguments, the list of actual values
    given, and the list of allowable values. Not normally instantiated
    by hand, but rather by the ListVariable converter function.
    """

    def __init__(self, initlist=None, allowedElems=None) -> None:
        if initlist is None:
            initlist = []
        if allowedElems is None:
            allowedElems = []
        super().__init__([_f for _f in initlist if _f])
        self.allowedElems = sorted(allowedElems)

    def __cmp__(self, other):
        return NotImplemented

    def __eq__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

    def __gt__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented

    def __lt__(self, other):
        return NotImplemented

    def __str__(self) -> str:
        if not self.data:
            return 'none'
        self.data.sort()
        if self.data == self.allowedElems:
            return 'all'
        return ','.join(self)

    def prepare_to_store(self):
        return str(self)

def _converter(val, allowedElems, mapdict) -> _ListVariable:
    """Convert list variables."""
    if val == 'none':
        val = []
    elif val == 'all':
        val = allowedElems
    else:
        val = [_f for _f in val.split(',') if _f]
        val = [mapdict.get(v, v) for v in val]
        notAllowed = [v for v in val if v not in allowedElems]
        if notAllowed:
            raise ValueError(
                f"Invalid value(s) for option: {','.join(notAllowed)}"
            )
    return _ListVariable(val, allowedElems)


# def _validator(key, val, env) -> None:
#     """ """
#     # TODO: write validator for list variable
#     pass


# lint: W0622: Redefining built-in 'help' (redefined-builtin)
# lint: W0622: Redefining built-in 'map' (redefined-builtin)
def ListVariable(
    key,
    help: str,
    default: Union[str, List[str]],
    names: List[str],
    map: Optional[dict] = None,
) -> Tuple[str, str, str, None, Callable]:
    """Return a tuple describing a list variable.

    The input parameters describe a list variable, where the values
    can be one or more from *names* plus the special values ``all``
    and ``none``.

    Arguments:
       key: the name of the list variable.
       help: the basic help message.  Will have text appended indicating
          the allowable values (not including any extra names from *map*).
       default: the default value(s) for the list variable. Can be
          given as string (possibly comma-separated), or as a list of strings.
          ``all`` or ``none`` are allowed as *default*.
       names: the allowable values. Must be a list of strings.
       map: optional dictionary to map alternative names to the ones in
          *names*, providing a form of alias. The converter will make
          the replacement, names from *map* are not stored and will
          not appear in the help message.

    Returns:
       A tuple including the correct converter and validator.  The
       result is usable as input to :meth:`~SCons.Variables.Variables.Add`.
    """
    if map is None:
        map = {}
    names_str = f"allowed names: {' '.join(names)}"
    if SCons.Util.is_List(default):
        default = ','.join(default)
    help = '\n    '.join(
        (help, '(all|none|comma-separated list of names)', names_str))
    return key, help, default, None, lambda val: _converter(val, names, map)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
