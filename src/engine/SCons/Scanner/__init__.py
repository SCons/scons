"""SCons.Scanner

The Scanner package for the SCons software construction utility.

"""

#
# Copyright (c) 2001, 2002 Steven Knight
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


import SCons.Node.FS
import SCons.Util


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

    def __init__(self,
                 function,
                 name = "NONE",
                 argument = _null,
                 skeys = [],
                 node_factory = SCons.Node.FS.default_fs.File):
        """
        Construct a new scanner object given a scanner function.

        'function' - a scanner function taking two or three arguments and
        returning a list of strings.

        'name' - a name for identifying this scanner object.

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
        self.name = name
        self.argument = argument
        self.skeys = skeys
        self.node_factory = node_factory

    def scan(self, node, env):
        """
        This method scans a single object. 'node' is the node
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. A list of
        direct dependency nodes for the specified node will be returned.
        """

        if not self.argument is _null:
            list = self.function(node, env, self.argument)
        else:
            list = self.function(node, env)
        kw = {}
        if hasattr(node, 'dir'):
            kw['directory'] = node.dir
        nodes = []
        for l in list:
            if not isinstance(l, SCons.Node.FS.Entry):
                l = apply(self.node_factory, (l,), kw)
            nodes.append(l)
        return nodes

    def instance(self, env):
        """
        Return an instance of a Scanner object for use in scanning.

        In the base class, we just return the scanner itself.
        Other Scanner classes may use this to clone copies and/or
        return unique instances as needed.
        """
        return self

    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def __hash__(self):
        return hash(None)

class Recursive(Base):
    """
    The class for recursive dependency scanning.  This will
    re-scan any new files returned by each call to the
    underlying scanning function, and return the aggregate
    list of all dependencies.
    """

    def scan(self, node, env):
        """
        This method does the actual scanning. 'node' is the node
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. An
        aggregate list of dependency nodes for the specified filename
        and any of its scanned dependencies will be returned.
        """

        nodes = [node]
        seen = {node : 0}
        deps = []
        while nodes:
            n = nodes.pop(0)
            d = filter(lambda x, seen=seen: not seen.has_key(x),
                       Base.scan(self, n, env))
            if d:
                deps.extend(d)
                nodes.extend(d)
                for n in d:
                    seen[n] = 0
        return deps
