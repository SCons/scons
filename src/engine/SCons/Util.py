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
import cStringIO

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

_cv = re.compile(r'\$([_a-zA-Z]\w*|{[^}]*})')
_space_sep = re.compile(r'[\t ]+(?![^{]*})')

def scons_subst_list(strSubst, locals, globals):
    """
    This function is similar to scons_subst(), but with
    one important difference.  Instead of returning a single
    string, this function returns a list of lists.
    The first (outer) list is a list of lines, where the
    substituted stirng has been broken along newline characters.
    The inner lists are lists of command line arguments, i.e.,
    the argv array that should be passed to a spawn or exec
    function.

    One important thing this guy does is preserve environment
    variables that are lists.  For instance, if you have
    an environment variable that is a Python list (or UserList-
    derived class) that contains path names with spaces in them,
    then the entire path will be returned as a single argument.
    This is the only way to know where the 'split' between arguments
    is for executing a command line."""

    def repl(m, locals=locals, globals=globals):
        key = m.group(1)
        if key[:1] == '{' and key[-1:] == '}':
            key = key[1:-1]
	try:
            e = eval(key, locals, globals)
            if not e:
                s = ''
            elif type(e) is types.ListType or \
                 isinstance(e, UserList):
                s = string.join(map(str, e), '\0')
            else:
                s = _space_sep.sub('\0', str(e))
	except NameError:
	    s = ''
	return s
    n = 1

    # Tokenize the original string...
    strSubst = _space_sep.sub('\0', strSubst)
    
    # Now, do the substitution
    while n != 0:
        strSubst, n = _cv.subn(repl, strSubst)
    # Now parse the whole list into tokens.
    listLines = string.split(strSubst, '\n')
    return map(lambda x: filter(lambda y: y, string.split(x, '\0')),
               listLines)

def scons_subst(strSubst, locals, globals):
    """Recursively interpolates dictionary variables into
    the specified string, returning the expanded result.
    Variables are specified by a $ prefix in the string and
    begin with an initial underscore or alphabetic character
    followed by any number of underscores or alphanumeric
    characters.  The construction variable names may be
    surrounded by curly braces to separate the name from
    trailing characters.
    """
    cmd_list = scons_subst_list(strSubst, locals, globals)
    return string.join(map(string.join, cmd_list), '\n')

def find_files(filenames, paths,
               node_factory = SCons.Node.FS.default_fs.File):
    """
    find_files([str], [str]) -> [nodes]

    filenames - a list of filenames to find
    paths - a list of paths to search in

    returns - the nodes created from the found files.

    Finds nodes corresponding to either derived files or files
    that exist already.

    Only the first fullname found is returned for each filename, and any
    file that aren't found are ignored.
    """
    nodes = []
    for filename in filenames:
        for path in paths:
            fullname = os.path.join(path, filename)
            try:
                node = node_factory(fullname)
                # Return true of the node exists or is a derived node.
                if node.builder or \
                   (isinstance(node, SCons.Node.FS.Entry) and node.exists()):
                    nodes.append(node)
                    break
            except TypeError:
                # If we find a directory instead of a file, we
                # don't care
                pass

    return nodes
