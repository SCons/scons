"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

The code that reads the registry to find MSVC components was borrowed
from distutils.msvccompiler.

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



import os
import string
import os.path

import SCons.Action
import SCons.Builder
import SCons.Node.Alias
import SCons.Node.FS
import SCons.Scanner.C
import SCons.Scanner.Fortran
import SCons.Scanner.Prog

def alias_builder(env, target, source):
    pass

Alias = SCons.Builder.Builder(action = alias_builder,
                              target_factory = SCons.Node.Alias.default_ans.Alias,
                              source_factory = SCons.Node.FS.default_fs.Entry,
                              multi = 1)

CScan = SCons.Scanner.C.CScan()

FortranScan = SCons.Scanner.Fortran.FortranScan()

def yaccEmitter(target, source, env, **kw):
    # Yacc can be configured to emit a .h file as well
    # as a .c file, if -d is specified on the command line.
    if len(source) and \
       os.path.splitext(SCons.Util.to_String(source[0]))[1] in \
       [ '.y', '.yy'] and \
       '-d' in string.split(env.subst("$YACCFLAGS")):
        target.append(os.path.splitext(SCons.Util.to_String(target[0]))[0] + \
                      '.h')
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

        for src in source:
            if hasattr(src.attributes, 'shared'):
                if self.shared and not src.attributes.shared:
                    raise SCons.Errors.UserError, "Source file: %s is static and is not compatible with shared target: %s" % (src, target[0])
                elif not self.shared and src.attributes.shared:
                    raise SCons.Errors.UserError, "Source file: %s is shared and is not compatible with static target: %s" % (src, target[0])

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

def _concat(prefix, list, suffix, locals, globals, f=lambda x: x):
    """Creates a new list from 'list' by first interpolating each element
    in the list using 'locals' and 'globals' and then calling f on the list, and
    finally concatinating 'prefix' and 'suffix' onto each element of the
    list. A trailing space on 'prefix' or leading space on 'suffix' will
    cause them to be put into seperate list elements rather than being
    concatinated."""

    if not list:
        return list

    if not SCons.Util.is_List(list):
        list = [list]

    def subst(x, locals=locals, globals=globals):
        if SCons.Util.is_String(x):
            return SCons.Util.scons_subst(x, locals, globals)
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
    '_concat'     : _concat,
    '_LIBFLAGS'    : '${_concat(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, locals(), globals())}',
    '_LIBDIRFLAGS' : '$( ${_concat(LIBDIRPREFIX, LIBPATH, LIBDIRSUFFIX, locals(), globals(), RDirs)} $)',
    '_CPPINCFLAGS' : '$( ${_concat(INCPREFIX, CPPPATH, INCSUFFIX, locals(), globals(), RDirs)} $)',
    '_F77INCFLAGS' : '$( ${_concat(INCPREFIX, F77PATH, INCSUFFIX, locals(), globals(), RDirs)} $)'
    }
