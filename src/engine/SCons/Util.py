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
import SCons.Node

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

class Literal:
    """A wrapper for a string.  If you use this object wrapped
    around a string, then it will be interpreted as literal.
    When passed to the command interpreter, all special
    characters will be escaped."""
    def __init__(self, lstr):
        self.lstr = lstr

    def __str__(self):
        return self.lstr

    def is_literal(self):
        return 1

class SpecialAttrWrapper(Literal):
    """This is a wrapper for what we call a 'Node special attribute.'
    This is any of the attributes of a Node that we can reference from
    Environment variable substitution, such as $TARGET.abspath or
    $SOURCES[1].filebase.  We inherit from Literal so we can handle
    special characters, plus we implement a for_signature method,
    such that we can return some canonical string during signatutre
    calculation to avoid unnecessary rebuilds."""

    def __init__(self, lstr, for_signature=None):
        """The for_signature parameter, if supplied, will be the
        canonical string we return from for_signature().  Else
        we will simply return lstr."""
        Literal.__init__(self, lstr)
        if for_signature:
            self.forsig = for_signature
        else:
            self.forsig = lstr

    def for_signature(self):
        return self.forsig

class CallableComposite(UserList.UserList):
    """A simple composite callable class that, when called, will invoke all
    of its contained callables with the same arguments."""
    def __init__(self, seq = []):
        UserList.UserList.__init__(self, seq)

    def __call__(self, *args, **kwargs):
        retvals = map(lambda x, args=args, kwargs=kwargs: apply(x,
                                                                args,
                                                                kwargs),
                      self.data)
        if self.data and (len(self.data) == len(filter(callable, retvals))):
            return self.__class__(retvals)
        return NodeList(retvals)

class NodeList(UserList.UserList):
    """This class is almost exactly like a regular list of Nodes
    (actually it can hold any object), with one important difference.
    If you try to get an attribute from this list, it will return that
    attribute from every item in the list.  For example:

    >>> someList = NodeList([ '  foo  ', '  bar  ' ])
    >>> someList.strip()
    [ 'foo', 'bar' ]
    """
    def __init__(self, seq = []):
        UserList.UserList.__init__(self, seq)

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

    def is_literal(self):
        return 1

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

def quote_spaces(arg):
    if ' ' in arg or '\t' in arg:
        return '"%s"' % arg
    else:
        return str(arg)

# Several functions below deal with Environment variable
# substitution.  Part of this process involves inserting
# a bunch of special escape sequences into the string
# so that when we are all done, we know things like
# where to split command line args, what strings to
# interpret literally, etc.  A dictionary of these
# sequences follows:
#
# \0\1          signifies a division between arguments in
#               a command line.
#
# \0\2          signifies a division between multiple distinct
#               commands, i.e., a newline
#
# \0\3          This string should be interpreted literally.
#               This code occurring anywhere in the string means
#               the whole string should have all special characters
#               escaped.
#
# \0\4          A literal dollar sign '$'
#
# \0\5          Placed before and after interpolated variables
#               so that we do not accidentally smush two variables
#               together during the recursive interpolation process.

_cv = re.compile(r'\$([_a-zA-Z][\.\w]*|{[^}]*})')
_space_sep = re.compile(r'[\t ]+(?![^{]*})')
_newline = re.compile(r'[\r\n]+')

def _convertArg(x, strconv=to_String):
    """This function converts an individual argument.  If the
    argument is to be interpreted literally, with all special
    characters escaped, then we insert a special code in front
    of it, so that the command interpreter will know this."""
    literal = 0

    try:
        if x.is_literal():
            literal = 1
    except AttributeError:
        pass
    
    if not literal:
        # escape newlines as '\0\2', '\0\1' denotes an argument split
        # Also escape double-dollar signs to mean the literal dollar sign.
        return string.replace(_newline.sub('\0\2', strconv(x)), '$$', '\0\4')
    else:
        # Interpret non-string args as literals.
        # The special \0\3 code will tell us to encase this string
        # in a Literal instance when we are all done
        # Also escape out any $ signs because we don't want
        # to continue interpolating a literal.
        return '\0\3' + string.replace(strconv(x), '$', '\0\4')

def _convert(x, strconv = to_String):
    """This function is used to convert construction variable
    values or the value of strSubst to a string for interpolation.
    This function follows the rules outlined in the documentaion
    for scons_subst_list()"""
    if x is None:
        return ''
    elif is_String(x):
        # escape newlines as '\0\2', '\0\1' denotes an argument split
        return _convertArg(_space_sep.sub('\0\1', x), strconv)
    elif is_List(x):
        # '\0\1' denotes an argument split
        return string.join(map(lambda x, s=strconv: _convertArg(x, s), x),
                           '\0\1')
    else:
        return _convertArg(x, strconv)

class CmdStringHolder:
    """This is a special class used to hold strings generated
    by scons_subst_list().  It defines a special method escape().
    When passed a function with an escape algorithm for a
    particular platform, it will return the contained string
    with the proper escape sequences inserted."""

    def __init__(self, cmd):
        """This constructor receives a string.  The string
        can contain the escape sequence \0\3.
        If it does, then we will escape all special characters
        in the string before passing it to the command interpreter."""
        self.data = cmd
        
        # Populate flatdata (the thing returned by str()) with the
        # non-escaped string
        self.escape(lambda x: x, lambda x: x)

    def __str__(self):
        """Return the string in its current state."""
        return self.flatdata

    def __len__(self):
        """Return the length of the string in its current state."""
        return len(self.flatdata)

    def __getitem__(self, index):
        """Return the index'th element of the string in its current state."""
        return self.flatdata[index]

    def escape(self, escape_func, quote_func=quote_spaces):
        """Escape the string with the supplied function.  The
        function is expected to take an arbitrary string, then
        return it with all special characters escaped and ready
        for passing to the command interpreter.

        After calling this function, the next call to str() will
        return the escaped string.
        """

        if string.find(self.data, '\0\3') >= 0:
            self.flatdata = escape_func(string.replace(self.data, '\0\3', ''))
        elif ' ' in self.data or '\t' in self.data:
            self.flatdata = quote_func(self.data)
        else:
            self.flatdata = self.data

    def __cmp__(self, rhs):
        return cmp(self.flatdata, str(rhs))
        
class DisplayEngine:
    def __init__(self):
        self.__call__ = self.print_it

    def print_it(self, text):
        print text

    def dont_print(self, text):
        pass

    def set_mode(self, mode):
        if mode:
            self.__call__ = self.print_it
        else:
            self.__call__ = self.dont_print

def target_prep(target):
    if target and not isinstance(target, NodeList):
        if not is_List(target):
            target = [target]
        target = NodeList(map(lambda x: x.get_subst_proxy(), target))
    return target

def source_prep(source):
    if source and not isinstance(source, NodeList):
        if not is_List(source):
            source = [source]
        source = NodeList(map(lambda x: x.rfile().get_subst_proxy(), source))
    return source

def subst_dict(target, source, env):
    """Create a dictionary for substitution of special
    construction variables.

    This translates the following special arguments:

    target - the target (object or array of objects),
             used to generate the TARGET and TARGETS
             construction variables

    source - the source (object or array of objects),
             used to generate the SOURCES and SOURCE
             construction variables

    env    - the construction Environment used for this
             build, which is made available as the __env__
             construction variable
    """
    dict = { '__env__' : env }

    target = target_prep(target)
    dict['TARGETS'] = target
    if dict['TARGETS']:
        dict['TARGET'] = dict['TARGETS'][0]

    source = source_prep(source)
    dict['SOURCES'] = source
    if dict['SOURCES']:
        dict['SOURCE'] = dict['SOURCES'][0]

    return dict

# Constants for the "mode" parameter to scons_subst_list() and
# scons_subst().  SUBST_RAW gives the raw command line.  SUBST_CMD
# gives a command line suitable for passing to a shell.  SUBST_SIG
# gives a command line appropriate for calculating the signature
# of a command line...if this changes, we should rebuild.
SUBST_RAW = 0
SUBST_CMD = 1
SUBST_SIG = 2

_rm = re.compile(r'\$[()]')
_remove = re.compile(r'\$\(([^\$]|\$[^\(])*?\$\)')

def _canonicalize(obj):
    """Attempt to call the object's for_signature method,
    which is expected to return a string suitable for use in calculating
    a command line signature (i.e., it only changes when we should
    rebuild the target).  For instance, file Nodes will report only
    their file name (with no path), so changing Repository settings
    will not cause a rebuild."""
    try:
        return obj.for_signature()
    except AttributeError:
        return to_String(obj)

# Indexed by the SUBST_* constants above.
_regex_remove = [ None, _rm, _remove ]
_strconv = [ to_String, to_String, _canonicalize ]

def scons_subst_list(strSubst, env, mode=SUBST_RAW, target=None, source=None):
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
    determine how to parse strSubst and construction variables into lines
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

    remove = _regex_remove[mode]
    strconv = _strconv[mode]

    def repl(m,
             target=target,
             source=source,
             env=env,
             local_vars = subst_dict(target, source, env),
             global_vars = env.Dictionary(),
             strconv=strconv,
             sig=(mode != SUBST_CMD)):
        key = m.group(1)
        if key[0] == '{':
            key = key[1:-1]
        try:
            e = eval(key, global_vars, local_vars)
        except (IndexError, NameError, TypeError):
            return '\0\5'
        if callable(e):
            # We wait to evaluate callables until the end of everything
            # else.  For now, we instert a special escape sequence
            # that we will look for later.
            return '\0\5' + _convert(e(target=target,
                                       source=source,
                                       env=env,
                                       for_signature=sig),
                                     strconv) + '\0\5'
        else:
            # The \0\5 escape code keeps us from smushing two or more
            # variables together during recusrive substitution, i.e.
            # foo=$bar bar=baz barbaz=blat => $foo$bar->blat (bad)
            return "\0\5" + _convert(e, strconv) + "\0\5"

    # Convert the argument to a string:
    strSubst = _convert(strSubst, strconv)

    # Do the interpolation:
    n = 1
    while n != 0:
        strSubst, n = _cv.subn(repl, strSubst)
        
    # Convert the interpolated string to a list of lines:
    listLines = string.split(strSubst, '\0\2')

    # Remove the patterns that match the remove argument: 
    if remove:
        listLines = map(lambda x,re=remove: re.sub('', x), listLines)

    # Process escaped $'s and remove placeholder \0\5's
    listLines = map(lambda x: string.replace(string.replace(x, '\0\4', '$'), '\0\5', ''), listLines)

    # Finally split each line up into a list of arguments:
    return map(lambda x: map(CmdStringHolder, filter(lambda y:y, string.split(x, '\0\1'))),
               listLines)

def scons_subst(strSubst, env, mode=SUBST_RAW, target=None, source=None):
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

    remove = _regex_remove[mode]
    strconv = _strconv[mode]

    def repl(m,
             target=target,
             source=source,
             env=env,
             local_vars = subst_dict(target, source, env),
             global_vars = env.Dictionary(),
             strconv=strconv,
             sig=(mode != SUBST_CMD)):
        key = m.group(1)
        if key[0] == '{':
            key = key[1:-1]
        try:
            e = eval(key, global_vars, local_vars)
        except (IndexError, NameError, TypeError):
            return '\0\5'
        if callable(e):
            e = e(target=target, source=source, env=env,
                  for_signature = sig)

        def conv(arg, strconv=strconv):
            literal = 0
            try:
                if arg.is_literal():
                    literal = 1
            except AttributeError:
                pass
            ret = strconv(arg)
            if literal:
                # Escape dollar signs to prevent further
                # substitution on literals.
                ret = string.replace(ret, '$', '\0\4')
            return ret
        if e is None:
            s = ''
        elif is_List(e):
            s = string.join(map(conv, e), ' ')
        else:
            s = conv(e)
        # Insert placeholders to avoid accidentally smushing
        # separate variables together.
        return "\0\5" + s + "\0\5"

    # Now, do the substitution
    n = 1
    while n != 0:
        # escape double dollar signs
        strSubst = string.replace(strSubst, '$$', '\0\4')
        strSubst,n = _cv.subn(repl, strSubst)

    # remove the remove regex
    if remove:
        strSubst = remove.sub('', strSubst)

    # Un-escape the string
    strSubst = string.replace(string.replace(strSubst, '\0\4', '$'),
                              '\0\5', '')
    # strip out redundant white-space
    return string.strip(_space_sep.sub(' ', strSubst))

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
    if not prune:
        visited = copy.copy(visited)
    visited[root] = 1

    for i in range(len(children)):
        margin.append(i<len(children)-1)
        retval = retval + render_tree(children[i], child_func, prune, margin, visited
)
        margin.pop()

    return retval

def is_Dict(e):
    return type(e) is types.DictType or isinstance(e, UserDict.UserDict)

def is_List(e):
    return type(e) is types.ListType or isinstance(e, UserList.UserList)

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

def mapPaths(paths, dir, env=None):
    """Takes a single node or string, or a list of nodes and/or
    strings.  We leave the nodes untouched, but we put the strings
    under the supplied directory node dir, if they are not an absolute
    path.

    For instance, the following:

    n = SCons.Node.FS.default_fs.File('foo')
    mapPaths([ n, 'foo', '/bar' ],
             SCons.Node.FS.default_fs.Dir('baz'), env)

    ...would return:

    [ n, 'baz/foo', '/bar' ]

    The env argument, if given, is used to perform variable
    substitution on the source string(s).
    """

    def mapPathFunc(path, dir=dir, env=env):
        if is_String(path):
            if env:
                path = env.subst(path)
            if dir:
                if not path:
                    return str(dir)
                if os.path.isabs(path) or path[0] == '#':
                    return path
                return str(dir) + os.sep + path
        return path

    if not is_List(paths):
        paths = [ paths ]
    ret = map(mapPathFunc, paths)
    return ret
    

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

    def get(self):
        return self.__subject

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
        """Returns a value in the registry without
        having to open the key first."""
        # I would use os.path.split here, but it's not a filesystem
        # path...
        p = key.rfind('\\') + 1
        keyp = key[:p]
        val = key[p:]
        k = SCons.Util.RegOpenKeyEx(root, keyp)
        return SCons.Util.RegQueryValueEx(k,val)

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
                    return os.path.normpath(fext)
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
                    return os.path.normpath(fext)
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
                    return os.path.normpath(f)
        return None

def PrependPath(oldpath, newpath, sep = os.pathsep):
    """Prepend newpath elements to the given oldpath.  Will only add
    any particular path once (leaving the first one it encounters and
    ignoring the rest, to preserve path order), and will normpath and
    normcase all paths to help assure this.  This can also handle the
    case where the given oldpath variable is a list instead of a
    string, in which case a list will be returned instead of a string.
    """

    orig = oldpath
    is_list = 1
    paths = orig
    if not SCons.Util.is_List(orig):
        paths = string.split(paths, sep)
        is_list = 0

    if SCons.Util.is_List(newpath):
        newpaths = newpath
    else:
        newpaths = string.split(newpath, sep)

    newpaths = newpaths + paths # prepend new paths

    normpaths = []
    paths = []
    # now we add them only of they are unique
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
    """Append newpath elements to the given oldpath.  Will only add
    any particular path once (leaving the first one it encounters and
    ignoring the rest, to preserve path order), and will normpath and
    normcase all paths to help assure this.  This can also handle the
    case where the given oldpath variable is a list instead of a
    string, in which case a list will be returned instead of a string.
    """

    orig = oldpath
    is_list = 1
    paths = orig
    if not SCons.Util.is_List(orig):
        paths = string.split(paths, sep)
        is_list = 0

    if SCons.Util.is_List(newpath):
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


def ParseConfig(env, command, function=None):
    """Use the specified function to parse the output of the command in order
    to modify the specified environment. The 'command' can be a string or a
    list of strings representing a command and it's arguments. 'Function' is
    an optional argument that takes the environment and the output of the
    command. If no function is specified, the output will be treated as the
    output of a typical 'X-config' command (i.e. gtk-config) and used to set
    the CPPPATH, LIBPATH, LIBS, and CCFLAGS variables.
    """
    # the default parse function
    def parse_conf(env, output):
        env_dict = env.Dictionary()
        static_libs = []

        # setup all the dictionary options
        if not env_dict.has_key('CPPPATH'):
            env_dict['CPPPATH'] = []
        if not env_dict.has_key('LIBPATH'):
            env_dict['LIBPATH'] = []
        if not env_dict.has_key('LIBS'):
            env_dict['LIBS'] = []
        if not env_dict.has_key('CCFLAGS') or env_dict['CCFLAGS'] == "":
            env_dict['CCFLAGS'] = []

        params = string.split(output)
        for arg in params:
            switch = arg[0:1]
            opt = arg[1:2]
            if switch == '-':
                if opt == 'L':
                    env_dict['LIBPATH'].append(arg[2:])
                elif opt == 'l':
                    env_dict['LIBS'].append(arg[2:])
                elif opt == 'I':
                    env_dict['CPPPATH'].append(arg[2:])
                else:
                    env_dict['CCFLAGS'].append(arg)
            else:
                static_libs.append(arg)
        return static_libs

    if function is None:
        function = parse_conf
    if type(command) is type([]):
        command = string.join(command)
    return function(env, os.popen(command).read())

def dir_index(directory):
    files = []
    for file in os.listdir(directory):
        fullname = os.path.join(directory, file)
        files.append(fullname)

    # os.listdir() isn't guaranteed to return files in any specific order,
    # but some of the test code expects sorted output.
    files.sort()
    return files

def fs_delete(path, remove=1):
    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                if remove: os.unlink(path)
                display("Removed " + path)
            elif os.path.isdir(path) and not os.path.islink(path):
                # delete everything in the dir
                for p in dir_index(path):
                    if os.path.isfile(p):
                        if remove: os.unlink(p)
                        display("Removed " + p)
                    else:
                        fs_delete(p, remove)
                # then delete dir itself
                if remove: os.rmdir(path)
                display("Removed directory " + path)
    except OSError, e:
        print "scons: Could not remove '%s':" % str(path), e.strerror

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
