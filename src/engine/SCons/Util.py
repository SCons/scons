"""SCons.Util

Various utility functions go here.

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


import copy
import os.path
import re
import string
import types
import UserDict
import UserList

try:
    from UserString import UserString
except ImportError:
    class UserString:
        pass

import SCons.Node
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
    if is_String(arg):
	narg = string.split(arg)
    elif not is_List(arg):
	narg = [arg]

    nodes = []
    for v in narg:
	if is_String(v):
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


class PathList(UserList.UserList):
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
        UserList.UserList.__init__(self, seq)

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
        return self.__class__([ UserList.UserList.__getitem__(self, item), ])

_cv = re.compile(r'\$([_a-zA-Z]\w*|{[^}]*})')
_space_sep = re.compile(r'[\t ]+(?![^{]*})')

def scons_subst_list(strSubst, globals, locals, remove=None):
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

    def repl(m, globals=globals, locals=locals):
        key = m.group(1)
        if key[:1] == '{' and key[-1:] == '}':
            key = key[1:-1]
	try:
            e = eval(key, globals, locals)
            if e is None:
                s = ''
            elif is_List(e):
                s = string.join(map(str, e), '\0')
            else:
                s = _space_sep.sub('\0', str(e))
	except NameError:
	    s = ''
	return s
    n = 1

    # Tokenize the original string...
    strSubst = _space_sep.sub('\0', str(strSubst))
    
    # Now, do the substitution
    while n != 0:
        strSubst, n = _cv.subn(repl, strSubst)
    # Now parse the whole list into tokens.
    listLines = string.split(strSubst, '\n')
    if remove:
        listLines = map(lambda x,re=remove: re.sub('', x), listLines)
    return map(lambda x: filter(lambda y: y, string.split(x, '\0')),
               listLines)

def scons_subst(strSubst, globals, locals, remove=None):
    """Recursively interpolates dictionary variables into
    the specified string, returning the expanded result.
    Variables are specified by a $ prefix in the string and
    begin with an initial underscore or alphabetic character
    followed by any number of underscores or alphanumeric
    characters.  The construction variable names may be
    surrounded by curly braces to separate the name from
    trailing characters.
    """
    cmd_list = scons_subst_list(strSubst, globals, locals, remove)
    return string.join(map(string.join, cmd_list), '\n')

class VarInterpolator:
    def __init__(self, dest, src, prefix, suffix):
        self.dest = dest
        self.src = src
        self.prefix = prefix
        self.suffix = suffix

    def prepareSrc(self, dict):
        src = dict[self.src]
        if is_String(src):
            src = string.split(src)
        elif not is_List(src):
            src = [ src ]

        def prepare(x, dict=dict):
            if isinstance(x, SCons.Node.Node):
                return x
            else:
                return scons_subst(x, {}, dict)

        return map(prepare, src)

    def generate(self, dict):
        if not dict.has_key(self.src):
            dict[self.dest] = ''
            return

        src = filter(lambda x: not x is None, self.prepareSrc(dict))

        if not src:
            dict[self.dest] = ''
            return

        try:
            prefix = str(dict[self.prefix])
        except KeyError:
            prefix=''

        try:
            suffix = str(dict[self.suffix])
        except KeyError:
            suffix =''

        def autogenFunc(x, suff=suffix, pref=prefix):
            """Generate the interpolated variable.  If the prefix
            ends in a space, or the suffix begins in a space,
            leave it as a separate element of the list."""
            ret = [ str(x) ]
            if pref and pref[-1] == ' ':
                ret.insert(0, pref[:-1])
            else:
                ret[0] = pref + ret[0]
            if suff and suff[0] == ' ':
                ret.append(suff[1:])
            else:
                ret[-1] = ret[-1] + suff
            return ret
        dict[self.dest] = reduce(lambda x, y: x+y,
                                 map(autogenFunc,
                                     src))

    def instance(self, dir, fs):
        return self

class DirVarInterp(VarInterpolator):
    def __init__(self, dest, src, prefix, suffix):
        VarInterpolator.__init__(self, dest, src, prefix, suffix)
        self.fs = None
        self.Dir = None
        self.dictInstCache = {}

    def prepareSrc(self, dict):
        src = VarInterpolator.prepareSrc(self, dict)

        def prepare(x, self=self):
            if isinstance(x, SCons.Node.Node):
                return x
            elif str(x):
                return self.fs.Dir(str(x), directory=self.dir)
            else:
                return None

        return map(prepare, src)

    def instance(self, dir, fs):
        try:
            ret = self.dictInstCache[(dir, fs)]
        except KeyError:
            ret = copy.copy(self)
            ret.fs = fs
            ret.dir = dir
            self.dictInstCache[(dir, fs)] = ret
        return ret

    def generate(self, dict):
        VarInterpolator.generate(self, dict)
        if dict[self.dest]:
            dict[self.dest] = ['$('] + dict[self.dest] + ['$)']

AUTO_GEN_VARS = ( VarInterpolator('_LIBFLAGS',
                                  'LIBS',
                                  'LIBLINKPREFIX',
                                  'LIBLINKSUFFIX'),
                  DirVarInterp('_LIBDIRFLAGS',
                               'LIBPATH',
                               'LIBDIRPREFIX',
                               'LIBDIRSUFFIX' ),
                  DirVarInterp('_INCFLAGS',
                               'CPPPATH',
                               'INCPREFIX',
                               'INCSUFFIX') )

def autogenerate(dict, fs = SCons.Node.FS.default_fs, dir = None):
    """Autogenerate the "interpolated" environment variables.
    We read a static structure that tells us how.  AUTO_GEN_VARS
    is a tuple of tuples.  Each inner tuple has four elements,
    each strings referring to an environment variable, and describing
    how to autogenerate a particular variable.  The elements are:

    0 - The variable to generate
    1 - The "source" variable, usually a list
    2 - The "prefix" variable
    3 - The "suffix" variable

    The autogenerated variable is a list, consisting of every
    element of the source list, or a single element if the source
    is a string, with the prefix and suffix
    concatenated."""

    for interp in AUTO_GEN_VARS:
        interp.instance(dir, fs).generate(dict)

def render_tree(root, child_func, margin=[0], visited={}):
    """
    Render a tree of nodes into an ASCII tree view.
    root - the root node of the tree
    child_func - the function called to get the children of a node
    margin - the format of the left margin to use for children of root.
       1 results in a pipe, and 0 results in no pipe.
    visited - a dictionart of visited nodes in the current branch
    """

    if visited.has_key(root):
        return ""

    children = child_func(root)
    retval = ""
    for pipe in margin[:-1]:
        if pipe:
            retval = retval + "| "
        else:
            retval = retval + "  "

    retval = retval + "+-" + str(root) + "\n"
    visited = copy.copy(visited)
    visited[root] = 1

    for i in range(len(children)):
        margin.append(i<len(children)-1)
        retval = retval + render_tree(children[i], child_func, margin, visited
)
        margin.pop()

    return retval

def is_Dict(e):
    return type(e) is types.DictType or isinstance(e, UserDict.UserDict)

def is_List(e):
    return type(e) is types.ListType or isinstance(e, UserList.UserList)

if hasattr(types, 'UnicodeType'):
    def is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or isinstance(e, UserString)
else:
    def is_String(e):
        return type(e) is types.StringType or isinstance(e, UserString)

# attempt to load the windows registry module:
can_read_reg = 0
try:
    import _winreg

    can_read_reg = 1
    hkey_mod = _winreg

    RegOpenKeyEx = _winreg.OpenKeyEx
    RegEnumKey = _winreg.EnumKey
    RegEnumValue = _winreg.EnumValue
    RegQueryValueEx = _winreg.QueryValueEx
    RegError = _winreg.error

except ImportError:
    try:
        import win32api
        import win32con
        can_read_reg = 1
        hkey_mod = win32con

        RegOpenKeyEx = win32api.RegOpenKeyEx
        RegEnumKey = win32api.RegEnumKey
        RegEnumValue = win32api.RegEnumValue
        RegQueryValueEx = win32api.RegQueryValueEx
        RegError = win32api.error

    except ImportError:
        pass

if can_read_reg:
    HKEY_CLASSES_ROOT = hkey_mod.HKEY_CLASSES_ROOT
    HKEY_LOCAL_MACHINE = hkey_mod.HKEY_LOCAL_MACHINE
    HKEY_CURRENT_USER = hkey_mod.HKEY_CURRENT_USER
    HKEY_USERS = hkey_mod.HKEY_USERS
