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
import os
import os.path
import re
import stat
import string
import sys
import types
import UserDict
import UserList

try:
    from UserString import UserString
except ImportError:
    class UserString:
        pass

_altsep = os.altsep
if _altsep is None and sys.platform == 'win32':
    # My ActivePython 2.0.1 doesn't set os.altsep!  What gives?
    _altsep = '/'

def splitext(path):
    "Same as os.path.splitext() but faster."
    if _altsep:
        sep = max(string.rfind(path, os.sep), string.rfind(path, _altsep))
    else:
        sep = string.rfind(path, os.sep)
    dot = string.rfind(path, '.')
    if dot > sep:
        return path[:dot],path[dot:]
    else:
        return path,""

def updrive(path):
    """
    Make the drive letter (if any) upper case.
    This is useful because Windows is inconsitent on the case
    of the drive letter, which can cause inconsistencies when
    calculating command signatures.
    """
    drive, rest = os.path.splitdrive(path)
    if drive:
        path = string.upper(drive) + rest
    return path

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
        return self.__splitPath(splitext)[0]

    def __getSuffix(self):
        """Return the file's suffix."""
        return self.__splitPath(splitext)[1]

    def __getFileName(self):
        """Return the file's name without the path."""
        return self.__splitPath()[1]

    def __getDir(self):
        """Return the file's path."""
        return self.__splitPath()[0]

    def __getBase(self):
        """Return the file name with path and suffix stripped."""
        return self.__getFileName().__splitPath(splitext)[0]

    def __getAbsPath(self):
        """Return the absolute path"""
        return map(lambda x: updrive(os.path.abspath(x)), self.data)

    dictSpecialAttrs = { "file" : __getFileName,
                         "base" : __getBasePath,
                         "filebase" : __getBase,
                         "dir" : __getDir,
                         "suffix" : __getSuffix,
                         "abspath" : __getAbsPath}
    
    def __str__(self):
        return string.join(self.data)

    def __repr__(self):
        return repr(string.join(self.data))

    def __getitem__(self, item):
        # We must do this to ensure that single items returned
        # by index access have the special attributes such as
        # suffix and basepath.
        return self.__class__([ UserList.UserList.__getitem__(self, item), ])

_env_var = re.compile(r'^\$([_a-zA-Z]\w*|{[^}]*})$')

def get_environment_var(varstr):
    """Given a string, first determine if it looks like a reference
    to a single environment variable, like "$FOO" or "${FOO}".
    If so, return that variable with no decorations ("FOO").
    If not, return None."""
    mo=_env_var.match(to_String(varstr))
    if mo:
        var = mo.group(1)
        if var[0] == '{':
            return var[1:-1]
        else:
            return var
    else:
        return None

def quote_spaces(arg):
    if ' ' in arg or '\t' in arg:
        return '"%s"' % arg
    else:
        return arg

_cv = re.compile(r'\$([_a-zA-Z]\w*|{[^}]*})')
_space_sep = re.compile(r'[\t ]+(?![^{]*})')

def scons_subst_list(strSubst, globals, locals, remove=None):
    """
    This function serves the same purpose as scons_subst(), except
    this function returns the interpolated list as a list of lines, where
    each line is a list of command line arguments. In other words:
    The first (outer) list is a list of lines, where the
    substituted stirng has been broken along newline characters.
    The inner lists are lists of command line arguments, i.e.,
    the argv array that should be passed to a spawn or exec
    function.

    There are a few simple rules this function follows in order to
    determine how to parse strSubst and consruction variables into lines
    and arguments:

    1) A string is interpreted as a space delimited list of arguments.
    2) A list is interpreted as a list of arguments. This allows arguments
       with spaces in them to be expressed easily.
    4) Anything that is not a list or string (e.g. a Node instance) is
       interpreted as a single argument, and is converted to a string.
    3) Newline (\n) characters delimit lines. The newline parsing is done
       after all the other parsing, so it is not possible for arguments
       (e.g. file names) to contain embedded newline characters.
    """

    def convert(x):
        """This function is used to convert construction variable
        values or the value of strSubst to a string for interpolation.
        This function follows the rules outlined in the documentaion
        for scons_subst_list()"""
        if x is None:
            return ''
        elif is_String(x):
            return _space_sep.sub('\0', x)
        elif is_List(x):
            return string.join(map(to_String, x), '\0')
        else:
            return to_String(x)

    def repl(m, globals=globals, locals=locals, convert=convert):
        key = m.group(1)
        if key[0] == '{':
            key = key[1:-1]
        try:
            e = eval(key, globals, locals)
            return convert(e)
        except NameError:
            return ''

    # Convert the argument to a string:
    strSubst = convert(strSubst)

    # Do the interpolation:
    n = 1
    while n != 0:
        strSubst, n = _cv.subn(repl, strSubst)
        
    # Convert the interpolated string to a list of lines:
    listLines = string.split(strSubst, '\n')

    # Remove the patterns that match the remove argument: 
    if remove:
        listLines = map(lambda x,re=remove: re.sub('', x), listLines)

    # Finally split each line up into a list of arguments:
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

    # This function needs to be fast, so don't call scons_subst_list

    def repl(m, globals=globals, locals=locals):
        key = m.group(1)
        if key[0] == '{':
            key = key[1:-1]
        try:
            e = eval(key, globals, locals)
            if e is None:
                s = ''
            elif is_List(e):
                s = string.join(map(to_String, e), ' ')
            else:
                s = to_String(e)
        except NameError:
            s = ''
        return s

    # Now, do the substitution
    n = 1
    while n != 0:
        strSubst,n = _cv.subn(repl, strSubst)
    # and then remove remove
    if remove:
        strSubst = remove.sub('', strSubst)
    
    # strip out redundant white-space
    return string.strip(_space_sep.sub(' ', strSubst))

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

def to_String(s):
    """Better than str() because it will preserve a unicode
    object without converting it to ASCII."""
    if hasattr(types, 'UnicodeType') and \
       (type(s) is types.UnicodeType or \
        (isinstance(s, UserString) and type(s.data) is types.UnicodeType)):
        return unicode(s)
    else:
        return str(s)

def argmunge(arg):
    return Split(arg)

def Split(arg):
    """This function converts a string or list into a list of strings
    or Nodes.  This makes things easier for users by allowing files to
    be specified as a white-space separated list to be split.
    The input rules are:
        - A single string containing names separated by spaces. These will be
          split apart at the spaces.
        - A single Node instance
        - A list containing either strings or Node instances. Any strings
          in the list are not split at spaces.
    In all cases, the function returns a list of Nodes and strings."""
    if is_List(arg):
        return arg
    elif is_String(arg):
        return string.split(arg)
    else:
        return [arg]

if hasattr(types, 'UnicodeType'):
    def is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or isinstance(e, UserString)
else:
    def is_String(e):
        return type(e) is types.StringType or isinstance(e, UserString)

class Proxy:
    """A simple generic Proxy class, forwarding all calls to
    subject.  Inherit from this class to create a Proxy."""
    def __init__(self, subject):
        self.__subject = subject
        
    def __getattr__(self, name):
        return getattr(self.__subject, name)

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


if sys.platform == 'win32':

    def WhereIs(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = string.split(path, os.pathsep)
        if pathext is None:
            try:
                pathext = os.environ['PATHEXT']
            except KeyError:
                pathext = '.COM;.EXE;.BAT;.CMD'
        if is_String(pathext):
            pathext = string.split(pathext, os.pathsep)
        for ext in pathext:
            if string.lower(ext) == string.lower(file[-len(ext):]):
                pathext = ['']
                break
        for dir in path:
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

elif os.name == 'os2':

    def WhereIs(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = string.split(path, os.pathsep)
        if pathext is None:
            pathext = ['.exe', '.cmd']
        for ext in pathext:
            if string.lower(ext) == string.lower(file[-len(ext):]):
                pathext = ['']
                break
        for dir in path:
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

else:

    def WhereIs(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = string.split(path, os.pathsep)
        for dir in path:
            f = os.path.join(dir, file)
            if os.path.isfile(f):
                try:
                    st = os.stat(f)
                except:
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                    return f
        return None
