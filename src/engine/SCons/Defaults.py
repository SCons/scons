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

import SCons.Action
import SCons.Builder
import SCons.Node.Alias
import SCons.Node.FS
import SCons.Scanner.C
import SCons.Scanner.Fortran
import SCons.Scanner.Prog

# A placeholder for a default Environment (for fetching source files
# from source code management systems and the like).  This must be
# initialized later, after the top-level directory is set by the calling
# interface.
_default_env = None

def alias_builder(env, target, source):
    pass

Alias = SCons.Builder.Builder(action = alias_builder,
                              target_factory = SCons.Node.Alias.default_ans.Alias,
                              source_factory = SCons.Node.FS.default_fs.Entry,
                              multi = 1)

CScan = SCons.Scanner.C.CScan()

FortranScan = SCons.Scanner.Fortran.FortranScan()

def yaccEmitter(target, source, env, **kw):
    # If -d is specified on the command line, yacc will emit a .h
    # or .hpp file as well as a .c or .cpp file, depending on whether
    # the input file is a .y or .yy, respectively.
    if len(source) and '-d' in string.split(env.subst("$YACCFLAGS")):
        suff = os.path.splitext(SCons.Util.to_String(source[0]))[1]
        h = None
        if suff == '.y':
            h = '.h'
        elif suff == '.yy':
            h = '.hpp'
        if h:
            base = os.path.splitext(SCons.Util.to_String(target[0]))[0]
            target.append(base + h)
    return (target, source)

def CFile():
    """Common function to generate a C file Builder."""
    return SCons.Builder.Builder(action = {},
                                 emitter = yaccEmitter,
                                 suffix = '$CFILESUFFIX')

def CXXFile():
    """Common function to generate a C++ file Builder."""
    return SCons.Builder.Builder(action = {},
                                 emitter = yaccEmitter,
                                 suffix = '$CXXFILESUFFIX')

class SharedFlagChecker:
    """This is a callable class that is used as
    a build action for all objects, libraries, and programs.
    Its job is to run before the "real" action that builds the
    file, to make sure we aren't trying to link shared objects
    into a static library/program, or static objects into a
    shared library."""

    def __init__(self, shared, set_target_flag):
        self.shared = shared
        self.set_target_flag = set_target_flag

    def __call__(self, source, target, env, **kw):
        if kw.has_key('shared'):
            raise SCons.Errors.UserError, "The shared= parameter to Library() or Object() no longer works.\nUse SharedObject() or SharedLibrary() instead."
        if self.set_target_flag:
            for tgt in target:
                tgt.attributes.shared = self.shared

        same = env.subst('$STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME')
        if same == '0' or same == '' or same == 'False':
            for src in source:
                if hasattr(src.attributes, 'shared'):
                    if self.shared and not src.attributes.shared:
                        raise SCons.Errors.UserError, "Source file: %s is static and is not compatible with shared target: %s" % (src, target[0])

SharedCheck = SCons.Action.Action(SharedFlagChecker(1, 0), None)
StaticCheck = SCons.Action.Action(SharedFlagChecker(0, 0), None)
SharedCheckSet = SCons.Action.Action(SharedFlagChecker(1, 1), None)
StaticCheckSet = SCons.Action.Action(SharedFlagChecker(0, 1), None)

CAction = SCons.Action.Action([ StaticCheckSet, "$CCCOM" ])
ShCAction = SCons.Action.Action([ SharedCheckSet, "$SHCCCOM" ])
CXXAction = SCons.Action.Action([ StaticCheckSet, "$CXXCOM" ])
ShCXXAction = SCons.Action.Action([ SharedCheckSet, "$SHCXXCOM" ])

F77Action = SCons.Action.Action([ StaticCheckSet, "$F77COM" ])
ShF77Action = SCons.Action.Action([ SharedCheckSet, "$SHF77COM" ])
F77PPAction = SCons.Action.Action([ StaticCheckSet, "$F77PPCOM" ])
ShF77PPAction = SCons.Action.Action([ SharedCheckSet, "$SHF77PPCOM" ])

ASAction = SCons.Action.Action([ StaticCheckSet, "$ASCOM" ])
ASPPAction = SCons.Action.Action([ StaticCheckSet, "$ASPPCOM" ])


def StaticObject():
    """A function for generating the static object Builder."""
    return SCons.Builder.Builder(action = {},
                                 emitter="$OBJEMITTER",
                                 prefix = '$OBJPREFIX',
                                 suffix = '$OBJSUFFIX',
                                 src_builder = ['CFile', 'CXXFile'])

def SharedObject():
    """A function for generating the shared object Builder."""
    return SCons.Builder.Builder(action = {},
                                 prefix = '$SHOBJPREFIX',
                                 suffix = '$SHOBJSUFFIX',
                                 emitter="$OBJEMITTER",
                                 src_builder = ['CFile', 'CXXFile'])

ProgScan = SCons.Scanner.Prog.ProgScan()

StaticLibrary = SCons.Builder.Builder(action=[ StaticCheck, "$ARCOM" ],
                                      prefix = '$LIBPREFIX',
                                      suffix = '$LIBSUFFIX',
                                      src_suffix = '$OBJSUFFIX',
                                      src_builder = 'Object')

SharedLibrary = SCons.Builder.Builder(action=[ SharedCheck, "$SHLINKCOM" ],
                                      emitter="$SHLIBEMITTER",
                                      prefix = '$SHLIBPREFIX',
                                      suffix = '$SHLIBSUFFIX',
                                      scanner = ProgScan,
                                      src_suffix = '$SHOBJSUFFIX',
                                      src_builder = 'SharedObject')

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

Program = SCons.Builder.Builder(action=[ StaticCheck, '$LINKCOM' ],
                                emitter='$PROGEMITTER',
                                prefix='$PROGPREFIX',
                                suffix='$PROGSUFFIX',
                                src_suffix='$OBJSUFFIX',
                                src_builder='Object',
                                scanner = ProgScan)

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

    if not SCons.Util.is_List(list):
        list = [list]

    def subst(x, env = env):
        if SCons.Util.is_String(x):
            return SCons.Util.scons_subst(x, env)
        else:
            return x

    list = map(subst, list)

    list = f(list)

    ret = []

    # ensure that prefix and suffix are strings
    prefix = str(prefix)
    suffix = str(suffix)

    for x in list:
        x = str(x)

        if prefix and prefix[-1] == ' ':
            ret.append(prefix[:-1])
            ret.append(x)
        else:
            ret.append(prefix+x)

        if suffix and suffix[0] == ' ':
            ret.append(suffix[1:])
        else:
            ret[-1] = ret[-1]+suffix

    return ret

def _stripixes(prefix, list, suffix, stripprefix, stripsuffix, env, c=_concat):
    """This is a wrapper around _concat() that checks for the existence
    of prefixes or suffixes on list elements and strips them where it
    finds them.  This is used by tools (like the GNU linker) that need
    to turn something like 'libfoo.a' into '-lfoo'."""
    
    def f(list, sp=stripprefix, ss=stripsuffix):
        ret = []
        for l in list:
            if l[:len(sp)] == sp:
                l = l[len(sp):]
            if l[-len(ss):] == ss:
                l = l[:-len(ss)]
            ret.append(l)
        return ret
    return c(prefix, list, suffix, env, f)

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

    def __call__(self, target, source, env):
        return self.cmd

ConstructionEnvironment = {
    'BUILDERS'   : { 'SharedLibrary'  : SharedLibrary,
                     'Library'        : StaticLibrary,
                     'StaticLibrary'  : StaticLibrary,
                     'Alias'          : Alias,
                     'Program'        : Program },
    'SCANNERS'   : [CScan, FortranScan],
    'PDFPREFIX'  : '',
    'PDFSUFFIX'  : '.pdf',
    'PSPREFIX'   : '',
    'PSSUFFIX'   : '.ps',
    'ENV'        : {},
    'INSTALL'    : copyFunc,
    '_concat'     : _concat,
    '_stripixes'  : _stripixes,
    '_LIBFLAGS'    : '${_concat(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, __env__)}',
    '_LIBDIRFLAGS' : '$( ${_concat(LIBDIRPREFIX, LIBPATH, LIBDIRSUFFIX, __env__, RDirs)} $)',
    '_CPPINCFLAGS' : '$( ${_concat(INCPREFIX, CPPPATH, INCSUFFIX, __env__, RDirs)} $)',
    '_F77INCFLAGS' : '$( ${_concat(INCPREFIX, F77PATH, INCSUFFIX, __env__, RDirs)} $)',
    'TEMPFILE'     : NullCmdGenerator
    }
