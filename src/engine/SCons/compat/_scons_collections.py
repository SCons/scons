#
# __COPYRIGHT__
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
#

__doc__ = """
collections compatibility module for older (pre-2.4) Python versions

This does not not NOT (repeat, *NOT*) provide complete collections
functionality.  It only wraps the portions of collections functionality
used by SCons, in an interface that looks enough like collections for
our purposes.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

# Use the "imp" module to protect the imports below from fixers.
import imp

_UserDict = imp.load_module('UserDict', *imp.find_module('UserDict'))
_UserList = imp.load_module('UserList', *imp.find_module('UserList'))
_UserString = imp.load_module('UserString', *imp.find_module('UserString'))

UserDict = _UserDict.UserDict
UserList = _UserList.UserList
UserString = _UserString.UserString

del _UserDict
del _UserList
del _UserString

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
