"""SCons.Util

Various utility functions go here.

"""

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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import __builtin__
import copy
import os
import os.path
import re
import string
import sys
import stat
import types

from UserDict import UserDict
from UserList import UserList

try:
    from UserString import UserString
except ImportError:
    # "Borrowed" from the Python 2.2 UserString module
    # and modified slightly for use with SCons.
    class UserString:
        def __init__(self, seq):
            if is_String(seq):
                self.data = seq
            elif isinstance(seq, UserString):
                self.data = seq.data[:]
            else:
                self.data = str(seq)
        def __str__(self): return str(self.data)
        def __repr__(self): return repr(self.data)
        def __int__(self): return int(self.data)
        def __long__(self): return long(self.data)
        def __float__(self): return float(self.data)
        def __complex__(self): return complex(self.data)
        def __hash__(self): return hash(self.data)

        def __cmp__(self, string):
            if isinstance(string, UserString):
                return cmp(self.data, string.data)
            else:
                return cmp(self.data, string)
        def __contains__(self, char):
            return char in self.data

        def __len__(self): return len(self.data)
        def __getitem__(self, index): return self.__class__(self.data[index])
        def __getslice__(self, start, end):
            start = max(start, 0); end = max(end, 0)
            return self.__class__(self.data[start:end])

        def __add__(self, other):
            if isinstance(other, UserString):
                return self.__class__(self.data + other.data)
            elif is_String(other):
                return self.__class__(self.data + other)
            else:
                return self.__class__(self.data + str(other))
        def __radd__(self, other):
            if is_String(other):
                return self.__class__(other + self.data)
            else:
                return self.__class__(str(other) + self.data)
        def __mul__(self, n):
            return self.__class__(self.data*n)
        __rmul__ = __mul__

#
try:
    __builtin__.zip
except AttributeError:
    def zip(*lists):
        result = []
        for i in xrange(len(lists[0])):
            result.append(tuple(map(lambda l, i=i: l[i], lists)))
        return result
    __builtin__.zip = zip

_altsep = os.altsep
if _altsep is None and sys.platform == 'win32':
    # My ActivePython 2.0.1 doesn't set os.altsep!  What gives?
    _altsep = '/'
if _altsep:
    def rightmost_separator(path, sep, _altsep=_altsep):
        rfind = string.rfind
        return max(rfind(path, sep), rfind(path, _altsep))
else:
    rightmost_separator = string.rfind

# First two from the Python Cookbook, just for completeness.
# (Yeah, yeah, YAGNI...)
def containsAny(str, set):
    """Check whether sequence str contains ANY of the items in set."""
    for c in set:
        if c in str: return 1
    return 0

def containsAll(str, set):
    """Check whether sequence str contains ALL of the items in set."""
    for c in set:
        if c not in str: return 0
    return 1

def containsOnly(str, set):
    """Check whether sequence str contains ONLY items in set."""
    for c in str:
        if c not in set: return 0
    return 1

def splitext(path):
    "Same as os.path.splitext() but faster."
    sep = rightmost_separator(path, os.sep)
    dot = string.rfind(path, '.')
    # An ext is only real if it has at least one non-digit char
    if dot > sep and not containsOnly(path[dot:], "0123456789."):
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

#
# Generic convert-to-string functions that abstract away whether or
# not the Python we're executing has Unicode support.  The wrapper
# to_String_for_signature() will use a for_signature() method if the
# specified object has one.
#
if hasattr(types, 'UnicodeType'):
    def to_String(s):
        if isinstance(s, UserString):
            t = type(s.data)
        else:
            t = type(s)
        if t is types.UnicodeType:
            return unicode(s)
        else:
            return str(s)
else:
    to_String = str

def to_String_for_signature(obj):
    try:
        f = obj.for_signature
    except AttributeError:
        return to_String(obj)
    else:
        return f()

class CallableComposite(UserList):
    """A simple composite callable class that, when called, will invoke all
    of its contained callables with the same arguments."""
    def __call__(self, *args, **kwargs):
        retvals = map(lambda x, args=args, kwargs=kwargs: apply(x,
                                                                args,
                                                                kwargs),
                      self.data)
        if self.data and (len(self.data) == len(filter(callable, retvals))):
            return self.__class__(retvals)
        return NodeList(retvals)

class NodeList(UserList):
    """This class is almost exactly like a regular list of Nodes
    (actually it can hold any object), with one important difference.
    If you try to get an attribute from this list, it will return that
    attribute from every item in the list.  For example:

    >>> someList = NodeList([ '  foo  ', '  bar  ' ])
    >>> someList.strip()
    [ 'foo', 'bar' ]
    """
    def __nonzero__(self):
        return len(self.data) != 0

    def __str__(self):
        return string.join(map(str, self.data))

    def __getattr__(self, name):
        if not self.data:
            # If there is nothing in the list, then we have no attributes to
            # pass through, so raise AttributeError for everything.
            raise AttributeError, "NodeList has no attribute: %s" % name

        # Return a list of the attribute, gotten from every element
        # in the list
        attrList = map(lambda x, n=name: getattr(x, n), self.data)

        # Special case.  If the attribute is callable, we do not want
        # to return a list of callables.  Rather, we want to return a
        # single callable that, when called, will invoke the function on
        # all elements of this list.
        if self.data and (len(self.data) == len(filter(callable, attrList))):
            return CallableComposite(attrList)
        return self.__class__(attrList)

_valid_var = re.compile(r'[_a-zA-Z]\w*$')
_get_env_var = re.compile(r'^\$([_a-zA-Z]\w*|{[_a-zA-Z]\w*})$')

def is_valid_construction_var(varstr):
    """Return if the specified string is a legitimate construction
    variable.
    """
    return _valid_var.match(varstr)

def get_environment_var(varstr):
    """Given a string, first determine if it looks like a reference
    to a single environment variable, like "$FOO" or "${FOO}".
    If so, return that variable with no decorations ("FOO").
    If not, return None."""
    mo=_get_env_var.match(to_String(varstr))
    if mo:
        var = mo.group(1)
        if var[0] == '{':
            return var[1:-1]
        else:
            return var
    else:
        return None

class DisplayEngine:
    def __init__(self):
        self.__call__ = self.print_it

    def print_it(self, text, append_newline=1):
        if append_newline: text = text + '\n'
        sys.stdout.write(text)

    def dont_print(self, text, append_newline=1):
        pass

    def set_mode(self, mode):
        if mode:
            self.__call__ = self.print_it
        else:
            self.__call__ = self.dont_print

def render_tree(root, child_func, prune=0, margin=[0], visited={}):
    """
    Render a tree of nodes into an ASCII tree view.
    root - the root node of the tree
    child_func - the function called to get the children of a node
    prune - don't visit the same node twice
    margin - the format of the left margin to use for children of root.
       1 results in a pipe, and 0 results in no pipe.
    visited - a dictionary of visited nodes in the current branch if not prune,
       or in the whole tree if prune.
    """

    rname = str(root)

    if visited.has_key(rname):
        return ""

    children = child_func(root)
    retval = ""
    for pipe in margin[:-1]:
        if pipe:
            retval = retval + "| "
        else:
            retval = retval + "  "

    retval = retval + "+-" + rname + "\n"
    if not prune:
        visited = copy.copy(visited)
    visited[rname] = 1

    for i in range(len(children)):
        margin.append(i<len(children)-1)
        retval = retval + render_tree(children[i], child_func, prune, margin, visited
)
        margin.pop()

    return retval

IDX = lambda N: N and 1 or 0

def print_tree(root, child_func, prune=0, showtags=0, margin=[0], visited={}):
    """
    Print a tree of nodes.  This is like render_tree, except it prints
    lines directly instead of creating a string representation in memory,
    so that huge trees can be printed.

    root - the root node of the tree
    child_func - the function called to get the children of a node
    prune - don't visit the same node twice
    showtags - print status information to the left of each node line
    margin - the format of the left margin to use for children of root.
       1 results in a pipe, and 0 results in no pipe.
    visited - a dictionary of visited nodes in the current branch if not prune,
       or in the whole tree if prune.
    """

    rname = str(root)

    if visited.has_key(rname):
        return

    if showtags:

        if showtags == 2:
            print ' E       = exists'
            print '  R      = exists in repository only'
            print '   b     = implicit builder'
            print '   B     = explicit builder'
            print '    S    = side effect'
            print '     P   = precious'
            print '      A  = always build'
            print '       C = current'
            print ''

        tags = ['[']
        tags.append(' E'[IDX(root.exists())])
        tags.append(' R'[IDX(root.rexists() and not root.exists())])
        tags.append(' BbB'[[0,1][IDX(root.has_explicit_builder())] +
                           [0,2][IDX(root.has_builder())]])
        tags.append(' S'[IDX(root.side_effect)])
        tags.append(' P'[IDX(root.precious)])
        tags.append(' A'[IDX(root.always_build)])
        tags.append(' C'[IDX(root.current())])
        tags.append(']')

    else:
        tags = []

    def MMM(m):
        return ["  ","| "][m]
    margins = map(MMM, margin[:-1])

    print string.join(tags + margins + ['+-', rname], '')

    if prune:
        visited[rname] = 1

    children = child_func(root)
    if children:
        margin.append(1)
        map(lambda C, cf=child_func, p=prune, i=IDX(showtags), m=margin, v=visited:
                   print_tree(C, cf, p, i, m, v),
            children[:-1])
        margin[-1] = 0
        print_tree(children[-1], child_func, prune, IDX(showtags), margin, visited)
        margin.pop()

def is_Dict(e):
    return type(e) is types.DictType or isinstance(e, UserDict)

def is_List(e):
    return type(e) is types.ListType or isinstance(e, UserList)

if hasattr(types, 'UnicodeType'):
    def is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or isinstance(e, UserString)
else:
    def is_String(e):
        return type(e) is types.StringType or isinstance(e, UserString)

def is_Scalar(e):
    return is_String(e) or not is_List(e)

def flatten(sequence, scalarp=is_Scalar, result=None):
    if result is None:
        result = []
    for item in sequence:
        if scalarp(item):
            result.append(item)
        else:
            flatten(item, scalarp, result)
    return result

class Proxy:
    """A simple generic Proxy class, forwarding all calls to
    subject.  So, for the benefit of the python newbie, what does
    this really mean?  Well, it means that you can take an object, let's
    call it 'objA', and wrap it in this Proxy class, with a statement
    like this

                 proxyObj = Proxy(objA),

    Then, if in the future, you do something like this

                 x = proxyObj.var1,

    since Proxy does not have a 'var1' attribute (but presumably objA does),
    the request actually is equivalent to saying

                 x = objA.var1

    Inherit from this class to create a Proxy."""

    def __init__(self, subject):
        """Wrap an object as a Proxy object"""
        self.__subject = subject

    def __getattr__(self, name):
        """Retrieve an attribute from the wrapped object.  If the named
           attribute doesn't exist, AttributeError is raised"""
        return getattr(self.__subject, name)

    def get(self):
        """Retrieve the entire wrapped object"""
        return self.__subject

    def __cmp__(self, other):
        if issubclass(other.__class__, self.__subject.__class__):
            return cmp(self.__subject, other)
        return cmp(self.__dict__, other.__dict__)

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
        class _NoError(Exception):
            pass
        RegError = _NoError

if can_read_reg:
    HKEY_CLASSES_ROOT = hkey_mod.HKEY_CLASSES_ROOT
    HKEY_LOCAL_MACHINE = hkey_mod.HKEY_LOCAL_MACHINE
    HKEY_CURRENT_USER = hkey_mod.HKEY_CURRENT_USER
    HKEY_USERS = hkey_mod.HKEY_USERS

    def RegGetValue(root, key):
        """This utility function returns a value in the registry
        without having to open the key first.  Only available on
        Windows platforms with a version of Python that can read the
        registry.  Returns the same thing as
        SCons.Util.RegQueryValueEx, except you just specify the entire
        path to the value, and don't have to bother opening the key
        first.  So:

        Instead of:
          k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion')
          out = SCons.Util.RegQueryValueEx(k,
                'ProgramFilesDir')

        You can write:
          out = SCons.Util.RegGetValue(SCons.Util.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\ProgramFilesDir')
        """
        # I would use os.path.split here, but it's not a filesystem
        # path...
        p = key.rfind('\\') + 1
        keyp = key[:p]
        val = key[p:]
        k = SCons.Util.RegOpenKeyEx(root, keyp)
        return SCons.Util.RegQueryValueEx(k,val)

if sys.platform == 'win32':

    def WhereIs(file, path=None, pathext=None, reject=[]):
        if path is None:
            try:
                path = os.environ['PATH']
            except KeyError:
                return None
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
        if not is_List(reject):
            reject = [reject]
        for dir in path:
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    try:
                        reject.index(fext)
                    except ValueError:
                        return os.path.normpath(fext)
                    continue
        return None

elif os.name == 'os2':

    def WhereIs(file, path=None, pathext=None, reject=[]):
        if path is None:
            try:
                path = os.environ['PATH']
            except KeyError:
                return None
        if is_String(path):
            path = string.split(path, os.pathsep)
        if pathext is None:
            pathext = ['.exe', '.cmd']
        for ext in pathext:
            if string.lower(ext) == string.lower(file[-len(ext):]):
                pathext = ['']
                break
        if not is_List(reject):
            reject = [reject]
        for dir in path:
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    try:
                        reject.index(fext)
                    except ValueError:
                        return os.path.normpath(fext)
                    continue
        return None

else:

    def WhereIs(file, path=None, pathext=None, reject=[]):
        if path is None:
            try:
                path = os.environ['PATH']
            except KeyError:
                return None
        if is_String(path):
            path = string.split(path, os.pathsep)
        if not is_List(reject):
            reject = [reject]
        for d in path:
            f = os.path.join(d, file)
            if os.path.isfile(f):
                try:
                    st = os.stat(f)
                except OSError:
                    # os.stat() raises OSError, not IOError if the file
                    # doesn't exist, so in this case we let IOError get
                    # raised so as to not mask possibly serious disk or
                    # network issues.
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                    try:
                        reject.index(f)
                    except ValueError:
                        return os.path.normpath(f)
                    continue
        return None

def PrependPath(oldpath, newpath, sep = os.pathsep):
    """This prepends newpath elements to the given oldpath.  Will only
    add any particular path once (leaving the first one it encounters
    and ignoring the rest, to preserve path order), and will
    os.path.normpath and os.path.normcase all paths to help assure
    this.  This can also handle the case where the given old path
    variable is a list instead of a string, in which case a list will
    be returned instead of a string.

    Example:
      Old Path: "/foo/bar:/foo"
      New Path: "/biz/boom:/foo"
      Result:   "/biz/boom:/foo:/foo/bar"
    """

    orig = oldpath
    is_list = 1
    paths = orig
    if not is_List(orig):
        paths = string.split(paths, sep)
        is_list = 0

    if is_List(newpath):
        newpaths = newpath
    else:
        newpaths = string.split(newpath, sep)

    newpaths = newpaths + paths # prepend new paths

    normpaths = []
    paths = []
    # now we add them only if they are unique
    for path in newpaths:
        normpath = os.path.normpath(os.path.normcase(path))
        if path and not normpath in normpaths:
            paths.append(path)
            normpaths.append(normpath)

    if is_list:
        return paths
    else:
        return string.join(paths, sep)

def AppendPath(oldpath, newpath, sep = os.pathsep):
    """This appends new path elements to the given old path.  Will
    only add any particular path once (leaving the last one it
    encounters and ignoring the rest, to preserve path order), and
    will os.path.normpath and os.path.normcase all paths to help
    assure this.  This can also handle the case where the given old
    path variable is a list instead of a string, in which case a list
    will be returned instead of a string.

    Example:
      Old Path: "/foo/bar:/foo"
      New Path: "/biz/boom:/foo"
      Result:   "/foo/bar:/biz/boom:/foo"
    """

    orig = oldpath
    is_list = 1
    paths = orig
    if not is_List(orig):
        paths = string.split(paths, sep)
        is_list = 0

    if is_List(newpath):
        newpaths = newpath
    else:
        newpaths = string.split(newpath, sep)

    newpaths = paths + newpaths # append new paths
    newpaths.reverse()

    normpaths = []
    paths = []
    # now we add them only of they are unique
    for path in newpaths:
        normpath = os.path.normpath(os.path.normcase(path))
        if path and not normpath in normpaths:
            paths.append(path)
            normpaths.append(normpath)

    paths.reverse()

    if is_list:
        return paths
    else:
        return string.join(paths, sep)

if sys.platform == 'cygwin':
    def get_native_path(path):
        """Transforms an absolute path into a native path for the system.  In
        Cygwin, this converts from a Cygwin path to a Win32 one."""
        return string.replace(os.popen('cygpath -w ' + path).read(), '\n', '')
else:
    def get_native_path(path):
        """Transforms an absolute path into a native path for the system.
        Non-Cygwin version, just leave the path alone."""
        return path

display = DisplayEngine()

def Split(arg):
    if is_List(arg):
        return arg
    elif is_String(arg):
        return string.split(arg)
    else:
        return [arg]

class CLVar(UserList):
    """A class for command-line construction variables.

    This is a list that uses Split() to split an initial string along
    white-space arguments, and similarly to split any strings that get
    added.  This allows us to Do the Right Thing with Append() and
    Prepend() (as well as straight Python foo = env['VAR'] + 'arg1
    arg2') regardless of whether a user adds a list or a string to a
    command-line construction variable.
    """
    def __init__(self, seq = []):
        UserList.__init__(self, Split(seq))
    def __coerce__(self, other):
        return (self, CLVar(other))
    def __str__(self):
        return string.join(self.data)

# A dictionary that preserves the order in which items are added.
# Submitted by David Benjamin to ActiveState's Python Cookbook web site:
#     http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
# Including fixes/enhancements from the follow-on discussions.
class OrderedDict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = OrderedDict()
        dict.update(self)
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys[:]

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        for (key, val) in dict.items():
            self.__setitem__(key, val)

    def values(self):
        return map(self.get, self._keys)

class Selector(OrderedDict):
    """A callable ordered dictionary that maps file suffixes to
    dictionary values.  We preserve the order in which items are added
    so that get_suffix() calls always return the first suffix added."""
    def __call__(self, env, source):
        try:
            ext = splitext(str(source[0]))[1]
        except IndexError:
            ext = ""
        try:
            return self[ext]
        except KeyError:
            # Try to perform Environment substitution on the keys of
            # the dictionary before giving up.
            s_dict = {}
            for (k,v) in self.items():
                if not k is None:
                    s_k = env.subst(k)
                    if s_dict.has_key(s_k):
                        # We only raise an error when variables point
                        # to the same suffix.  If one suffix is literal
                        # and a variable suffix contains this literal,
                        # the literal wins and we don't raise an error.
                        raise KeyError, (s_dict[s_k][0], k, s_k)
                    s_dict[s_k] = (k,v)
            try:
                return s_dict[ext][1]
            except KeyError:
                try:
                    return self[None]
                except KeyError:
                    return None


if sys.platform == 'cygwin':
    # On Cygwin, os.path.normcase() lies, so just report back the
    # fact that the underlying Win32 OS is case-insensitive.
    def case_sensitive_suffixes(s1, s2):
        return 0
else:
    def case_sensitive_suffixes(s1, s2):
        return (os.path.normcase(s1) != os.path.normcase(s2))

def adjustixes(fname, pre, suf):
    if pre:
        path, fn = os.path.split(os.path.normpath(fname))
        if fn[:len(pre)] != pre:
            fname = os.path.join(path, pre + fn)
    # Only append a suffix if the file does not have one.
    if suf and not splitext(fname)[1] and fname[-len(suf):] != suf:
            fname = fname + suf
    return fname


def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti = lasti + 1
            i = i + 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

# Much of the logic here was originally based on recipe 4.9 from the
# Python CookBook, but we had to dumb it way down for Python 1.5.2.
class LogicalLines:

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def readline(self):
        result = []
        while 1:
            line = self.fileobj.readline()
            if not line:
                break
            if line[-2:] == '\\\n':
                result.append(line[:-2])
            else:
                result.append(line)
                break
        return string.join(result, '')

    def readlines(self):
        result = []
        while 1:
            line = self.readline()
            if not line:
                break
            result.append(line)
        return result
