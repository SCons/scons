"""SCons.Scanner

The Scanner package for the SCons software construction utility.

"""

#
# Copyright (c) 2001 Steven Knight
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"


from SCons.Util import scons_str2nodes


class _Null:
    pass

# This is used instead of None as a default argument value so None can be
# used as an actual argument value.
_null = _Null

class Base:
    """
    The base class for dependency scanners.  This implements
    straightforward, single-pass scanning of a single file.
    """

    def __init__(self, function, argument=_null, skeys=[]):
        """
        Construct a new scanner object given a scanner function.

        'function' - a scanner function taking two or three arguments and
        returning a list of strings.

        'argument' - an optional argument that will be passed to the
        scanner function if it is given.

        'skeys; - an optional list argument that can be used to determine
        which scanner should be used for a given Node. In the case of File
        nodes, for example, the 'skeys' would be file suffixes.

        The scanner function's first argument will be the name of a file
        that should be scanned for dependencies, the second argument will
        be an Environment object, the third argument will be the value
        passed into 'argument', and the returned list should contain the
        Nodes for all the direct dependencies of the file.

        Examples:

        s = Scanner(my_scanner_function)
        
        s = Scanner(function = my_scanner_function)

        s = Scanner(function = my_scanner_function, argument = 'foo')

        """

        # Note: this class could easily work with scanner functions that take
        # something other than a filename as an argument (e.g. a database
        # node) and a dependencies list that aren't file names. All that
        # would need to be changed is the documentation.

        self.function = function
        self.argument = argument
        self.name = "NONE"
        self.skeys = skeys

    def scan(self, filename, env):
        """
        This method scans a single object. 'filename' is the filename
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. A list of
        direct dependency nodes for the specified filename will be returned.
        """

        if not self.argument is _null:
            return self.function(filename, env, self.argument)
        else:
            return self.function(filename, env)

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def __call__(self, sources=None):
        slist = scons_str2nodes(source, self.node_factory)
        for s in slist:
            s.scanner_set(self)

        if len(slist) == 1:
            slist = slist[0]
        return slist

class Recursive(Base):
    """
    The class for recursive dependency scanning.  This will
    re-scan any new files returned by each call to the
    underlying scanning function, and return the aggregate
    list of all dependencies.
    """

    def scan(self, filename, env):
        """
        This method does the actual scanning. 'filename' is the filename
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. An
        aggregate list of dependency nodes for the specified filename
        and any of its scanned dependencies will be returned.
        """

        files = [filename]
        seen = [filename]
        deps = []
        while files:
            f = files.pop(0)
            if not self.argument is _null:
                d = self.function(f, env, self.argument)
            else:
                d = self.function(f, env)
            d = filter(lambda x, seen=seen: str(x) not in seen, d)
            deps.extend(d)
            s = map(str, d)
	    seen.extend(s)
            files.extend(s)
        return deps
