"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

The code that reads the registry to find MSVC components was borrowed
from distutils.msvccompiler.

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



import os
import os.path
import shutil
import stat
import string
import types

import SCons.Action
import SCons.Builder
import SCons.Environment
import SCons.Scanner.C
import SCons.Scanner.D
import SCons.Scanner.Fortran
import SCons.Scanner.Prog
import SCons.Sig

# A placeholder for a default Environment (for fetching source files
# from source code management systems and the like).  This must be
# initialized later, after the top-level directory is set by the calling
# interface.
_default_env = None

# Lazily instantiate the default environment so the overhead of creating
# it doesn't apply when it's not needed.
def DefaultEnvironment(*args, **kw):
    global _default_env
    if not _default_env:
        _default_env = apply(SCons.Environment.Environment, args, kw)
        _default_env._build_signature = 1
        _default_env._calc_module = SCons.Sig.default_module
    return _default_env

# Emitters for setting the shared attribute on object files,
# and an action for checking that all of the source files
# going into a shared library are, in fact, shared.
def StaticObjectEmitter(target, source, env):
    for tgt in target:
        tgt.attributes.shared = None
    return (target, source)

def SharedObjectEmitter(target, source, env):
    for tgt in target:
        tgt.attributes.shared = 1
    return (target, source)

def SharedFlagChecker(source, target, env):
    same = env.subst('$STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME')
    if same == '0' or same == '' or same == 'False':
        for src in source:
            try:
                shared = src.attributes.shared
            except AttributeError:
                shared = None
            if not shared:
                raise SCons.Errors.UserError, "Source file: %s is static and is not compatible with shared target: %s" % (src, target[0])

SharedCheck = SCons.Action.Action(SharedFlagChecker, None)

# Scanners and suffixes for common languages.
CScan = SCons.Scanner.C.CScan()

CSuffixes = [".c", ".C", ".cxx", ".cpp", ".c++", ".cc",
             ".h", ".H", ".hxx", ".hpp", ".hh",
             ".F", ".fpp", ".FPP",
             ".S", ".spp", ".SPP"]

DScan = SCons.Scanner.D.DScan()

DSuffixes = ['.d']

FortranScan = SCons.Scanner.Fortran.FortranScan()

FortranSuffixes = [".f", ".F", ".for", ".FOR"]

IDLSuffixes = [".idl", ".IDL"]

# Actions for common languages.
CAction = SCons.Action.Action("$CCCOM")
DAction = SCons.Action.Action("$DCOM")
ShCAction = SCons.Action.Action("$SHCCCOM")
CXXAction = SCons.Action.Action("$CXXCOM")
ShCXXAction = SCons.Action.Action("$SHCXXCOM")

F77Action = SCons.Action.Action("$F77COM")
ShF77Action = SCons.Action.Action("$SHF77COM")
F77PPAction = SCons.Action.Action("$F77PPCOM")
ShF77PPAction = SCons.Action.Action("$SHF77PPCOM")

ASAction = SCons.Action.Action("$ASCOM")
ASPPAction = SCons.Action.Action("$ASPPCOM")

ProgScan = SCons.Scanner.Prog.ProgScan()

def DVI():
    """Common function to generate a DVI file Builder."""
    return SCons.Builder.Builder(action = {},
                                 # The suffix is not configurable via a
                                 # construction variable like $DVISUFFIX
                                 # because the output file name is
                                 # hard-coded within TeX.
                                 suffix = '.dvi')

def PDF():
    """A function for generating the PDF Builder."""
    return SCons.Builder.Builder(action = { },
                                 prefix = '$PDFPREFIX',
                                 suffix = '$PDFSUFFIX')

def copyFunc(dest, source, env):
    """Install a source file into a destination by copying it (and its
    permission/mode bits)."""
    shutil.copy2(source, dest)
    st = os.stat(source)
    os.chmod(dest, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
    return 0

def _concat(prefix, list, suffix, env, f=lambda x: x):
    """Creates a new list from 'list' by first interpolating each
    element in the list using the 'env' dictionary and then calling f
    on the list, and finally concatenating 'prefix' and 'suffix' onto
    each element of the list. A trailing space on 'prefix' or leading
    space on 'suffix' will cause them to be put into seperate list
    elements rather than being concatenated."""
    
    if not list:
        return list

    list = f(env.subst_path(list))

    ret = []

    # ensure that prefix and suffix are strings
    prefix = str(env.subst(prefix, SCons.Util.SUBST_RAW))
    suffix = str(env.subst(suffix, SCons.Util.SUBST_RAW))

    for x in list:
        x = str(x)
        if x:

            if prefix:
                if prefix[-1] == ' ':
                    ret.append(prefix[:-1])
                elif x[:len(prefix)] != prefix:
                    x = prefix + x

            ret.append(x)

            if suffix:
                if suffix[0] == ' ':
                    ret.append(suffix[1:])
                elif x[-len(suffix):] != suffix:
                    ret[-1] = ret[-1]+suffix

    return ret

def _stripixes(prefix, list, suffix, stripprefix, stripsuffix, env, c=None):
    """This is a wrapper around _concat() that checks for the existence
    of prefixes or suffixes on list elements and strips them where it
    finds them.  This is used by tools (like the GNU linker) that need
    to turn something like 'libfoo.a' into '-lfoo'."""
    
    if not callable(c):
        if callable(env["_concat"]):
            c = env["_concat"]
        else:
            c = _concat
    def f(list, sp=stripprefix, ss=stripsuffix):
        ret = []
        for l in list:
            if not SCons.Util.is_String(l):
                l = str(l)
            if l[:len(sp)] == sp:
                l = l[len(sp):]
            if l[-len(ss):] == ss:
                l = l[:-len(ss)]
            ret.append(l)
        return ret
    return c(prefix, list, suffix, env, f)

def _defines(prefix, defs, suffix, env, c=_concat):
    """A wrapper around _concat that turns a list or string
    into a list of C preprocessor command-line definitions.
    """
    if SCons.Util.is_List(defs):
        l = []
        for d in defs:
            if SCons.Util.is_List(d) or type(d) is types.TupleType:
                l.append(str(d[0]) + '=' + str(d[1]))
            else:
                l.append(str(d))
    elif SCons.Util.is_Dict(defs):
        # The items in a dictionary are stored in random order, but
        # if the order of the command-line options changes from
        # invocation to invocation, then the signature of the command
        # line will change and we'll get random unnecessary rebuilds.
        # Consequently, we have to sort the keys to ensure a
        # consistent order...
        l = []
        keys = defs.keys()
        keys.sort()
        for k in keys:
            v = defs[k]
            if v is None:
                l.append(str(k))
            else:
                l.append(str(k) + '=' + str(v))
    else:
        l = [str(defs)]
    return c(prefix, l, suffix, env)
    
class NullCmdGenerator:
    """This is a callable class that can be used in place of other
    command generators if you don't want them to do anything.

    The __call__ method for this class simply returns the thing
    you instantiated it with.

    Example usage:
    env["DO_NOTHING"] = NullCmdGenerator
    env["LINKCOM"] = "${DO_NOTHING('$LINK $SOURCES $TARGET')}"
    """

    def __init__(self, cmd):
        self.cmd = cmd

    def __call__(self, target, source, env, for_signature=None):
        return self.cmd

ConstructionEnvironment = {
    'BUILDERS'   : {},
    'SCANNERS'   : [CScan, FortranScan, DScan],
    'CPPSUFFIXES': CSuffixes,
    'DSUFFIXES'  : DSuffixes,
    'FORTRANSUFFIXES': FortranSuffixes,
    'IDLSUFFIXES': IDLSuffixes,
    'PDFPREFIX'  : '',
    'PDFSUFFIX'  : '.pdf',
    'PSPREFIX'   : '',
    'PSSUFFIX'   : '.ps',
    'ENV'        : {},
    'INSTALL'    : copyFunc,
    '_concat'     : _concat,
    '_defines'    : _defines,
    '_stripixes'  : _stripixes,
    '_LIBFLAGS'    : '${_concat(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, __env__)}',
    '_LIBDIRFLAGS' : '$( ${_concat(LIBDIRPREFIX, LIBPATH, LIBDIRSUFFIX, __env__, RDirs)} $)',
    '_CPPINCFLAGS' : '$( ${_concat(INCPREFIX, CPPPATH, INCSUFFIX, __env__, RDirs)} $)',
    '_F77INCFLAGS' : '$( ${_concat(INCPREFIX, F77PATH, INCSUFFIX, __env__, RDirs)} $)',
    '_CPPDEFFLAGS' : '${_defines(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}',
    'TEMPFILE'     : NullCmdGenerator
    }
