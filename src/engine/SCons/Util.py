"""SCons.Util

Various utility functions go here.

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


import os.path
import types
import string
import re
from UserList import UserList
import SCons.Node.FS

def scons_str2nodes(arg, node_factory=SCons.Node.FS.default_fs.File):
    """This function converts a string or list into a list of Node instances.
    It follows the rules outlined in the SCons design document by accepting
    any of the following inputs:
	- A single string containing names separated by spaces. These will be
	  split apart at the spaces.
	- A single Node instance,
	- A list containingg either strings or Node instances. Any strings
	  in the list are not split at spaces.
    In all cases, the function returns a list of Node instances."""

    narg = arg
    if type(arg) is types.StringType:
	narg = string.split(arg)
    elif type(arg) is not types.ListType:
	narg = [arg]

    nodes = []
    for v in narg:
	if type(v) is types.StringType:
	    nodes.append(node_factory(v))
	# Do we enforce the following restriction?  Maybe, but it
	# also restricts what we can do for allowing people to
	# use the engine with alternate Node implementations...
	# Perhaps this should be split in two, with the SCons.Node
	# logic in a wrapper somewhere under SCons.Node, and the
	# string-parsing logic here...?
	#elif not issubclass(v.__class__, SCons.Node.Node):
	#    raise TypeError
	else:
	    nodes.append(v)

    return nodes


class PathList(UserList):
    """This class emulates the behavior of a list, but also implements
    the special "path dissection" attributes we can use to find
    suffixes, base names, etc. of the paths in the list.

    One other special attribute of this class is that, by
    overriding the __str__ and __repr__ methods, this class
    represents itself as a space-concatenated string of
    the list elements, as in:

    >>> pl=PathList(["/foo/bar.txt", "/baz/foo.txt"])
    >>> pl
    '/foo/bar.txt /baz/foo.txt'
    >>> pl.base
    'bar foo'
    """
    def __init__(self, seq = []):
        UserList.__init__(self, seq)

    def __getattr__(self, name):
        # This is how we implement the "special" attributes
        # such as base, suffix, basepath, etc.
        try:
            return self.dictSpecialAttrs[name](self)
        except KeyError:
            raise AttributeError, 'PathList has no attribute: %s' % name

    def __splitPath(self, split_func=os.path.split):
        """This method calls the supplied split_func on each element
        in the contained list.  We expect split_func to return a
        2-tuple, usually representing two elements of a split file path,
        such as those returned by os.path.split().

        We return a 2-tuple of lists, each equal in length to the contained
        list.  The first list represents all the elements from the
        first part of the split operation, the second represents
        all elements from the second part."""
        list1 = []
        list2 = []
        for strPath in self.data:
            first_part, second_part = split_func(strPath)
            list1.append(first_part)
            list2.append(second_part)
        return (self.__class__(list1),
                self.__class__(list2))

    def __getBasePath(self):
        """Return the file's directory and file name, with the
        suffix stripped."""
        return self.__splitPath(os.path.splitext)[0]

    def __getSuffix(self):
        """Return the file's suffix."""
        return self.__splitPath(os.path.splitext)[1]

    def __getFileName(self):
        """Return the file's name without the path."""
        return self.__splitPath()[1]

    def __getDir(self):
        """Return the file's path."""
        return self.__splitPath()[0]

    def __getBase(self):
        """Return the file name with path and suffix stripped."""
        return self.__getFileName().__splitPath(os.path.splitext)[0]

    dictSpecialAttrs = { "file" : __getFileName,
                         "base" : __getBasePath,
                         "filebase" : __getBase,
                         "dir" : __getDir,
                         "suffix" : __getSuffix }
    
    def __str__(self):
        return string.join(self.data)

    def __repr__(self):
        return repr(string.join(self.data))

    def __getitem__(self, item):
        # We must do this to ensure that single items returned
        # by index access have the special attributes such as
        # suffix and basepath.
        return self.__class__([ UserList.__getitem__(self, item), ])


__tcv = re.compile(r'\$(\{?targets?(\[[0-9:]+\])?(\.[a-z]+)?\}?)')
__scv = re.compile(r'\$(\{?sources(\[[0-9:]+\])?(\.[a-z]+)?\}?)')
def scons_varrepl(command, targets, sources):
    """This routine handles variable interpolation for the $targets and
    $sources variables in the 'command' argument. The targets and sources
    given in the other arguements must be lists containing 'Node's."""

    def repl(m, targets=targets, sources=sources):
	globals = {}
        key = m.group(1)
        if key[0] == '{':
            if key[-1] == '}':
                key = key[1:-1]
            else:
                raise SyntaxError, "Bad regular expression"

        if key[:6] == 'target':
	    globals['targets'] = targets
	    globals['target'] = targets[0]
	if key[:7] == 'sources':
	    globals['sources'] = sources
	if globals:
            return str(eval(key, globals ))

    command = __tcv.sub(repl, command)
    command = __scv.sub(repl, command)
    return command


