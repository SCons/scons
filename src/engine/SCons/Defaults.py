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
import stat
import string
import sys
import os.path

import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Node.Alias
import SCons.Node.FS
import SCons.Scanner.C
import SCons.Scanner.Prog
import SCons.Util

class SharedCmdGenerator:
    """A callable class that acts as a command generator.
    It is designed to hold on to 2 actions, and return
    one if the shared=1 keyword arg is supplied to the
    Builder method, and the other if not.

    Also, all target nodes will have the shared attribute
    set to match the vaue of the shared keyword argument,
    zero by default."""
    def __init__(self, static, shared):
        self.action_static = static
        self.action_shared = shared
        
    def __call__(self, target, source, env, shared=0):
        for src in source:
            try:
                if src.attributes.shared != shared:
                    raise UserError("Source file: %s must be built with shared=%s in order to be compatible with the selected target." % (src, str(shared)))
            except AttributeError:
                pass
        for t in target:
            t.attributes.shared = shared
        if shared:
            return self.action_shared
        else:
            return self.action_static

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

CFile = SCons.Builder.Builder(name = 'CFile',
                              action = { '.l'    : '$LEXCOM',
                                         '.y'    : '$YACCCOM',
                                       },
                              emitter = yaccEmitter,
                              suffix = '$CFILESUFFIX')

CXXFile = SCons.Builder.Builder(name = 'CXXFile',
                                action = { '.ll' : '$LEXCOM',
                                           '.yy' : '$YACCCOM',
                                         },
                                emitter = yaccEmitter,
                                suffix = '$CXXFILESUFFIX')

CAction = SCons.Action.Action("$CCCOM")
ShCAction = SCons.Action.Action("$SHCCCOM")
CXXAction = SCons.Action.Action("$CXXCOM")
ShCXXAction = SCons.Action.Action("$SHCXXCOM")
F77Action = SCons.Action.Action("$F77COM")
ShF77Action = SCons.Action.Action("$SHF77COM")
F77PPAction = SCons.Action.Action("$F77PPCOM")
ShF77PPAction = SCons.Action.Action("$SHF77PPCOM")

if os.path.normcase('.c') == os.path.normcase('.C'):
    # We're on a case-insensitive system, so .[CF] (upper case)
    # files should be treated like .[cf] (lower case) files.
    C_static = CAction
    C_shared = ShCAction
    F_static = F77Action
    F_shared = ShF77Action
else:
    # We're on a case-sensitive system, so .C (upper case) files
    # are C++, and .F (upper case) files get run through the C
    # preprocessor.
    C_static = CXXAction
    C_shared = ShCXXAction
    F_static = F77PPAction
    F_shared = ShF77PPAction

shared_obj = SCons.Builder.DictCmdGenerator({ ".C"   : C_shared,
                                              ".cc"  : ShCXXAction,
                                              ".cpp" : ShCXXAction,
                                              ".cxx" : ShCXXAction,
                                              ".c++" : ShCXXAction,
                                              ".C++" : ShCXXAction,
                                              ".c"   : ShCAction,
                                              ".f"   : ShF77Action,
                                              ".for" : ShF77Action,
                                              ".FOR" : ShF77Action,
                                              ".F"   : F_shared,
                                              ".fpp" : ShF77PPAction,
                                              ".FPP" : ShF77PPAction })

static_obj = SCons.Builder.DictCmdGenerator({ ".C"   : C_static,
                                              ".cc"  : CXXAction,
                                              ".cpp" : CXXAction,
                                              ".cxx" : CXXAction,
                                              ".c++" : CXXAction,
                                              ".C++" : CXXAction,
                                              ".c"   : CAction,
                                              ".f"   : F77Action,
                                              ".for" : F77Action,
                                              ".F"   : F_static,
                                              ".FOR" : F77Action,
                                              ".fpp" : F77PPAction,
                                              ".FPP" : F77PPAction })
                                                     
Object = SCons.Builder.Builder(name = 'Object',
                               generator = \
                               SharedCmdGenerator(static=SCons.Action.CommandGeneratorAction(static_obj),
                                                  shared=SCons.Action.CommandGeneratorAction(shared_obj)),
                               prefix = '$OBJPREFIX',
                               suffix = '$OBJSUFFIX',
                               src_suffix = static_obj.src_suffixes(),
                               src_builder = [CFile, CXXFile])

def win32TempFileMunge(env, cmd_list):
    """Given a list of command line arguments, see if it is too
    long to pass to the win32 command line interpreter.  If so,
    create a temp file, then pass "@tempfile" as the sole argument
    to the supplied command (which is the first element of cmd_list).
    Otherwise, just return [cmd_list]."""
    cmd = env.subst_list(cmd_list)[0]
    cmdlen = reduce(lambda x, y: x + len(y), cmd, 0) + len(cmd)
    if cmdlen <= 2048:
        return [cmd_list]
    else:
        import tempfile
        # We do a normpath because mktemp() has what appears to be
        # a bug in Win32 that will use a forward slash as a path
        # delimiter.  Win32's link mistakes that for a command line
        # switch and barfs.
        tmp = os.path.normpath(tempfile.mktemp())
        args = map(SCons.Util.quote_spaces, cmd[1:])
        open(tmp, 'w').write(string.join(args, " ") + "\n")
        return [ [cmd[0], '@' + tmp],
                 ['del', tmp] ]
    
def win32LinkGenerator(env, target, source, **kw):
    args = [ '$LINK', '$LINKFLAGS', '/OUT:%s' % target[0],
             '$(', '$_LIBDIRFLAGS', '$)', '$_LIBFLAGS' ]
    args.extend(map(SCons.Util.to_String, source))
    return win32TempFileMunge(env, args)

Program = SCons.Builder.Builder(name='Program',
                                action='$LINKCOM',
                                prefix='$PROGPREFIX',
                                suffix='$PROGSUFFIX',
                                src_suffix='$OBJSUFFIX',
                                src_builder=Object,
                                scanner = SCons.Scanner.Prog.ProgScan())

class LibAffixGenerator:
    def __init__(self, static, shared):
        self.static_affix = static
        self.shared_affix = shared

    def __call__(self, shared=0, win32=0):
        if shared:
            return self.shared_affix
        return self.static_affix

def win32LibGenerator(target, source, env, shared=1):
    listCmd = [ "$SHLINK", "$SHLINKFLAGS" ]

    for tgt in target:
        ext = os.path.splitext(str(tgt))[1]
        if ext == env.subst("$LIBSUFFIX"):
            # Put it on the command line as an import library.
            listCmd.append("${WIN32IMPLIBPREFIX}%s" % tgt)
        else:
            listCmd.append("${WIN32DLLPREFIX}%s" % tgt)

    listCmd.extend([ '$_LIBDIRFLAGS', '$_LIBFLAGS' ])
    for src in source:
        ext = os.path.splitext(str(src))[1]
        if ext == env.subst("$WIN32DEFSUFFIX"):
            # Treat this source as a .def file.
            listCmd.append("${WIN32DEFPREFIX}%s" % src)
        else:
            # Just treat it as a generic source file.
            listCmd.append(str(src))
    return win32TempFileMunge(env, listCmd)

def win32LibEmitter(target, source, env, shared=0):
    if shared:
        dll = None
        for tgt in target:
            ext = os.path.splitext(str(tgt))[1]
            if ext == env.subst("$SHLIBSUFFIX"):
                dll = tgt
                break
        if not dll:
            raise UserError("A shared library should have exactly one target with the suffix: %s" % env.subst("$SHLIBSUFFIX"))
        
        if env.has_key("WIN32_INSERT_DEF") and \
           env["WIN32_INSERT_DEF"] and \
           not '.def' in map(lambda x: os.path.split(str(x))[1],
                             source):

            # append a def file to the list of sources
            source.append("%s%s" % (os.path.splitext(str(dll))[0],
                                    env.subst("$WIN32DEFSUFFIX")))
        if not env.subst("$LIBSUFFIX") in \
           map(lambda x: os.path.split(str(x))[1], target):
            # Append an import library to the list of targets.
            target.append("%s%s%s" % (env.subst("$LIBPREFIX"),
                                      os.path.splitext(str(dll))[0],
                                      env.subst("$LIBSUFFIX")))
    return (target, source)

Library = SCons.Builder.Builder(name = 'Library',
                                generator = \
                                SharedCmdGenerator(shared="$SHLINKCOM",
                                                   static="$ARCOM"),
                                emitter="$LIBEMITTER",
                                prefix = \
                                LibAffixGenerator(static='$LIBPREFIX',
                                                  shared='$SHLIBPREFIX'),
                                suffix = \
                                LibAffixGenerator(static='$LIBSUFFIX',
                                                  shared='$SHLIBSUFFIX'),
                                src_suffix = '$OBJSUFFIX',
                                src_builder = Object)

LaTeXAction = SCons.Action.Action('$LATEXCOM')

DVI = SCons.Builder.Builder(name = 'DVI',
                            action = { '.tex'   : '$TEXCOM',
                                       '.ltx'   : LaTeXAction,
                                       '.latex' : LaTeXAction,
                                     },
			    # The suffix is not configurable via a
			    # construction variable like $DVISUFFIX
			    # because the output file name is
			    # hard-coded within TeX.
                            suffix = '.dvi')

PDFLaTeXAction = SCons.Action.Action('$PDFLATEXCOM')

PDF = SCons.Builder.Builder(name = 'PDF',
                            action = { '.dvi'   : '$PDFCOM',
                                       '.tex'   : '$PDFTEXCOM',
                                       '.ltx'   : PDFLaTeXAction,
                                       '.latex' : PDFLaTeXAction,
                                     },
                            prefix = '$PDFPREFIX',
                            suffix = '$PDFSUFFIX')

PostScript = SCons.Builder.Builder(name = 'PostScript',
                                   action = '$PSCOM',
                                   prefix = '$PSPREFIX',
                                   suffix = '$PSSUFFIX',
                                   src_suffix = '.dvi',
                                   src_builder = DVI)

CScan = SCons.Scanner.C.CScan()

def alias_builder(env, target, source):
    pass

Alias = SCons.Builder.Builder(name = 'Alias',
                              action = alias_builder,
                              target_factory = SCons.Node.Alias.default_ans.Alias,
                              source_factory = SCons.Node.FS.default_fs.Entry)

def get_devstudio_versions ():
    """
    Get list of devstudio versions from the Windows registry.  Return a
    list of strings containing version numbers; an exception will be raised
    if we were unable to access the registry (eg. couldn't import
    a registry-access module) or the appropriate registry keys weren't
    found.
    """

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    K = 'Software\\Microsoft\\Devstudio'
    L = []
    for base in (SCons.Util.HKEY_CLASSES_ROOT,
                 SCons.Util.HKEY_LOCAL_MACHINE,
                 SCons.Util.HKEY_CURRENT_USER,
                 SCons.Util.HKEY_USERS):
        try:
            k = SCons.Util.RegOpenKeyEx(base,K)
            i = 0
            while 1:
                try:
                    p = SCons.Util.RegEnumKey(k,i)
                    if p[0] in '123456789' and p not in L:
                        L.append(p)
                except SCons.Util.RegError:
                    break
                i = i + 1
        except SCons.Util.RegError:
            pass

    if not L:
        raise SCons.Errors.InternalError, "DevStudio was not found."

    L.sort()
    L.reverse()
    return L

def get_msvc_path (path, version, platform='x86'):
    """
    Get a list of devstudio directories (include, lib or path).  Return
    a string delimited by ';'. An exception will be raised if unable to
    access the registry or appropriate registry keys not found.
    """

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    if path=='lib':
        path= 'Library'
    path = string.upper(path + ' Dirs')
    K = ('Software\\Microsoft\\Devstudio\\%s\\' +
         'Build System\\Components\\Platforms\\Win32 (%s)\\Directories') % \
        (version,platform)
    for base in (SCons.Util.HKEY_CLASSES_ROOT,
                 SCons.Util.HKEY_LOCAL_MACHINE,
                 SCons.Util.HKEY_CURRENT_USER,
                 SCons.Util.HKEY_USERS):
        try:
            k = SCons.Util.RegOpenKeyEx(base,K)
            i = 0
            while 1:
                try:
                    (p,v,t) = SCons.Util.RegEnumValue(k,i)
                    if string.upper(p) == path:
                        return v
                    i = i + 1
                except SCons.Util.RegError:
                    break
        except SCons.Util.RegError:
            pass

    # if we got here, then we didn't find the registry entries:
    raise SCons.Errors.InternalError, "%s was not found in the registry."%path

def get_msdev_dir(version):
    """Returns the root directory of the MSDev installation from the
    registry if it can be found, otherwise we guess."""
    if SCons.Util.can_read_reg:
        K = ('Software\\Microsoft\\Devstudio\\%s\\' +
             'Products\\Microsoft Visual C++') % \
             version
        for base in (SCons.Util.HKEY_LOCAL_MACHINE,
                     SCons.Util.HKEY_CURRENT_USER):
            try:
                k = SCons.Util.RegOpenKeyEx(base,K)
                val, tok = SCons.Util.RegQueryValueEx(k, 'ProductDir')
                return os.path.split(val)[0]
            except SCons.Util.RegError:
                pass

def make_win32_env_from_paths(include, lib, path):
    """
    Build a dictionary of construction variables for a win32 platform.
    include - include path
    lib - library path
    path - executable path
    """
    return {
        'CC'         : 'cl',
        'CCFLAGS'    : '/nologo',
        'CCCOM'      : '$CC $CCFLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'SHCC'      : '$CC',
        'SHCCFLAGS' : '$CCFLAGS',
        'SHCCCOM'    : '$SHCC $SHCCFLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'CFILESUFFIX' : '.c',
        'CXX'        : '$CC',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'SHCXX'      : '$CXX',
        'SHCXXFLAGS' : '$CXXFLAGS',
        'SHCXXCOM'   : '$SHCXX $SHCXXFLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'CXXFILESUFFIX' : '.cc',
        'F77'        : 'g77',
        'F77FLAGS'   : '',
        'F77COM'     : '$F77 $F77FLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'F77PPCOM'   : '$F77 $F77FLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'SHF77'      : '$F77',
        'SHF77FLAGS' : '$F77FLAGS',
        'SHF77COM'   : '$SHF77 $SHF77FLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'SHF77PPCOM' : '$SHF77 $SHF77FLAGS $CPPFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'LINK'       : 'link',
        'LINKFLAGS'  : '/nologo',
        'LINKCOM'    : SCons.Action.CommandGenerator(win32LinkGenerator),
        'SHLINK'     : '$LINK',
        'SHLINKFLAGS': '$LINKFLAGS /dll',
        'SHLINKCOM'  : SCons.Action.CommandGenerator(win32LibGenerator),
        'AR'         : 'lib',
        'ARFLAGS'    : '/nologo',
        'ARCOM'      : '$AR $ARFLAGS /OUT:$TARGET $SOURCES',
        'SHLIBPREFIX': '',
        'SHLIBSUFFIX': '.dll',
        'LEX'        : 'lex',
        'LEXFLAGS'   : '',
        'LEXCOM'     : '$LEX $LEXFLAGS -t $SOURCES > $TARGET',
        'YACC'       : 'yacc',
        'YACCFLAGS'  : '',
        'YACCCOM'    : '$YACC $YACCFLAGS -o $TARGET $SOURCES',
        'TEX'        : 'tex',
        'TEXFLAGS'   : '',
        'TEXCOM'     : '$TEX $TEXFLAGS $SOURCES',
        'LATEX'      : 'latex',
        'LATEXFLAGS' : '',
        'LATEXCOM'   : '$LATEX $LATEXFLAGS $SOURCES',
        'DVIPDF'     : 'dvipdf',
        'DVIPDFFLAGS' : '',
        'PDFCOM'     : '$DVIPDF $DVIPDFFLAGS $SOURCES $TARGET',
        'PDFPREFIX'  : '',
        'PDFSUFFIX'  : '.pdf',
        'PDFTEX'     : 'pdftex',
        'PDFTEXFLAGS' : '',
        'PDFTEXCOM'  : '$PDFTEX $PDFTEXFLAGS $SOURCES $TARGET',
        'PDFLATEX'   : 'pdflatex',
        'PDFLATEXFLAGS' : '',
        'PDFLATEXCOM' : '$PDFLATEX $PDFLATEXFLAGS $SOURCES $TARGET',
        'DVIPS'      : 'dvips',
        'DVIPSFLAGS' : '',
        'PSCOM'      : '$DVIPS $DVIPSFLAGS -o $TARGET $SOURCES',
        'PSPREFIX'   : '',
        'PSSUFFIX'   : '.ps',
        'BUILDERS'   : [Alias, CFile, CXXFile, DVI, Library, Object,
                        PDF, PostScript, Program],
        'SCANNERS'   : [CScan],
        'OBJPREFIX'  : '',
        'OBJSUFFIX'  : '.obj',
        'PROGPREFIX' : '',
        'PROGSUFFIX' : '.exe',
        'LIBPREFIX'  : '',
        'LIBPREFIXES': '$LIBPREFIX',
        'LIBSUFFIX'  : '.lib',
        'LIBSUFFIXES': '$LIBSUFFIX',
        'LIBDIRPREFIX'          : '/LIBPATH:',
        'LIBDIRSUFFIX'          : '',
        'LIBLINKPREFIX'         : '',
        'LIBLINKSUFFIX'         : '$LIBSUFFIX',
        'LIBEMITTER'            : win32LibEmitter,
        'INCPREFIX'             : '/I',
        'INCSUFFIX'             : '',
        'WIN32DEFPREFIX'        : '/def:',
        'WIN32DEFSUFFIX'        : '.def',
        'WIN32DLLPREFIX'        : '/out:',
        'WIN32IMPLIBPREFIX'     : '/implib:',
        'WIN32_INSERT_DEF'      : 0,
        'ENV'        : {
            'INCLUDE'  : include,
            'LIB'      : lib,
            'PATH'     : path,
                'PATHEXT' : '.COM;.EXE;.BAT;.CMD',
            },
        }

def make_win32_env(version):
    """
    Build a dictionary of construction variables for a win32 platform.
    ver - the version string of DevStudio to use (e.g. "6.0")
    """
    return make_win32_env_from_paths(get_msvc_path("include", version),
                                     get_msvc_path("lib", version),
                                     get_msvc_path("path", version)
                                     + ";" + os.environ['PATH'])


if os.name == 'posix':
    arcom = '$AR $ARFLAGS $TARGET $SOURCES'
    ranlib = 'ranlib'
    if SCons.Util.WhereIs(ranlib):
        arcom = arcom + '\n$RANLIB $RANLIBFLAGS $TARGET'

    ConstructionEnvironment = {
        'CC'         : 'cc',
        'CCFLAGS'    : '',
        'CCCOM'      : '$CC $CCFLAGS $CPPFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'SHCC'       : '$CC',
        'SHCCFLAGS'  : '$CCFLAGS -fPIC',
        'SHCCCOM'    : '$SHCC $SHCCFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'CFILESUFFIX' : '.c',
        'CXX'        : 'c++',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $CPPFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'CXXFILESUFFIX' : '.cc',
        'SHCXX'      : '$CXX',
        'SHCXXFLAGS' : '$CXXFLAGS -fPIC',
        'SHCXXCOM'   : '$SHCXX $SHCXXFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'F77'        : 'g77',
        'F77FLAGS'   : '',
        'F77COM'     : '$F77 $F77FLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'F77PPCOM'   : '$F77 $F77FLAGS $CPPFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'SHF77FLAGS' : '$F77FLAGS -fPIC',
        'SHF77COM'   : '$F77 $SHF77FLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'SHF77PPCOM' : '$F77 $SHF77FLAGS $CPPFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'SHF77'      : '$F77',
        'SHF77FLAGS' : '$F77FLAGS -fPIC',
        'SHF77COM'   : '$SHF77 $SHF77FLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'SHF77PPCOM' : '$SHF77 $SHF77FLAGS $CPPFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'LINK'       : '$CXX',
        'LINKFLAGS'  : '',
        'LINKCOM'    : '$LINK $LINKFLAGS -o $TARGET $SOURCES $_LIBDIRFLAGS $_LIBFLAGS',
        'SHLINK'     : '$LINK',
        'SHLINKFLAGS': '$LINKFLAGS -shared',
        'SHLINKCOM'  : '$SHLINK $SHLINKFLAGS -o $TARGET $SOURCES $_LIBDIRFLAGS $_LIBFLAGS',
        'AR'         : 'ar',
        'ARFLAGS'    : 'r',
        'RANLIB'     : ranlib,
        'RANLIBFLAGS' : '',
        'ARCOM'      : arcom,
        'SHLIBPREFIX': '$LIBPREFIX',
        'SHLIBSUFFIX': '.so',
        'LEX'        : 'lex',
        'LEXFLAGS'   : '',
        'LEXCOM'     : '$LEX $LEXFLAGS -t $SOURCES > $TARGET',
        'YACC'       : 'yacc',
        'YACCFLAGS'  : '',
        'YACCCOM'    : '$YACC $YACCFLAGS -o $TARGET $SOURCES',
        'TEX'        : 'tex',
        'TEXFLAGS'   : '',
        'TEXCOM'     : '$TEX $TEXFLAGS $SOURCES',
        'LATEX'      : 'latex',
        'LATEXFLAGS' : '',
        'LATEXCOM'   : '$LATEX $LATEXFLAGS $SOURCES',
        'DVIPDF'     : 'dvipdf',
        'PDFCOM'     : '$DVIPDF $DVIPDFFLAGS $SOURCES $TARGET',
        'PDFPREFIX'  : '',
        'PDFSUFFIX'  : '.pdf',
        'PDFTEX'     : 'pdftex',
        'PDFTEXFLAGS' : '',
        'PDFTEXCOM'  : '$PDFTEX $PDFTEXFLAGS $SOURCES $TARGET',
        'PDFLATEX'   : 'pdflatex',
        'PDFLATEXFLAGS' : '',
        'PDFLATEXCOM' : '$PDFLATEX $PDFLATEXFLAGS $SOURCES $TARGET',
        'DVIPS'      : 'dvips',
        'PSCOM'      : '$DVIPS $DVIPSFLAGS -o $TARGET $SOURCES',
        'PSPREFIX'   : '',
        'PSSUFFIX'   : '.ps',
        'BUILDERS'   : [Alias, CFile, CXXFile, DVI, Library, Object,
                        PDF, PostScript, Program],
        'SCANNERS'   : [CScan],
        'OBJPREFIX'  : '',
        'OBJSUFFIX'  : '.o',
        'PROGPREFIX' : '',
        'PROGSUFFIX' : (sys.platform == 'cygwin') and '.exe' or '',
        'LIBPREFIX'  : 'lib',
        'LIBPREFIXES': '$LIBPREFIX',
        'LIBSUFFIX'  : '.a',
        'LIBSUFFIXES': [ '$LIBSUFFIX', '$SHLIBSUFFIX' ],
        'LIBDIRPREFIX'          : '-L',
        'LIBDIRSUFFIX'          : '',
        'LIBLINKPREFIX'         : '-l',
        'LIBLINKSUFFIX'         : '',
        'INCPREFIX'             : '-I',
        'INCSUFFIX'             : '',
        'ENV'        : { 'PATH' : '/usr/local/bin:/bin:/usr/bin' },
    }

elif os.name == 'nt':
    versions = None
    try:
        versions = get_devstudio_versions()
        ConstructionEnvironment = make_win32_env(versions[0]) #use highest version
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        # Could not get the configured directories from the registry.
        # However, the configured directories only appear if the user
        # changes them from the default.  Therefore, we'll see if
        # we can get the path to the MSDev base installation from
        # the registry and deduce the default directories.
        MVSdir = None
        if versions:
            MVSdir = get_msdev_dir(versions[0])
        if MVSdir:
            MVSVCdir = r'%s\VC98' % MVSdir
            MVSCommondir = r'%s\Common' % MVSdir
            try:
                extra_path = os.pathsep + os.environ['PATH']
            except KeyError:
                extra_path = ''
            ConstructionEnvironment = make_win32_env_from_paths(
                r'%s\atl\include;%s\mfc\include;%s\include' % (MVSVCdir, MVSVCdir, MVSVCdir),
                r'%s\mfc\lib;%s\lib' % (MVSVCdir, MVSVCdir),
                (r'%s\MSDev98\Bin;%s\Bin' % (MVSCommondir, MVSVCdir)) + extra_path)
        else:
            # The DevStudio environment variables don't exist,
            # so just use the variables from the source environment.
            MVSdir = r'C:\Program Files\Microsoft Visual Studio'
            MVSVCdir = r'%s\VC98' % MVSdir
            MVSCommondir = r'%s\Common' % MVSdir
            try:
                include_path = os.environ['INCLUDE']
            except KeyError:
                include_path = ''
            try:
                lib_path = os.environ['LIB']
            except KeyError:
                lib_path = ''
            try:
                exe_path = os.environ['PATH']
            except KeyError:
                exe_path = ''
            ConstructionEnvironment = make_win32_env_from_paths(
                include_path,
                lib_path,
                exe_path)

