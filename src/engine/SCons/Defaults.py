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

import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Node.Alias
import SCons.Node.FS
import SCons.Scanner.C
import SCons.Scanner.Prog
import SCons.Util



CFile = SCons.Builder.Builder(name = 'CFile',
                              action = { '.l'    : '$LEXCOM',
                                         '.y'    : '$YACCCOM',
                                       },
                              suffix = '$CFILESUFFIX')

CXXFile = SCons.Builder.Builder(name = 'CXXFile',
                                action = { '.ll' : '$LEXCOM',
                                           '.yy' : '$YACCCOM',
                                         },
                                suffix = '$CXXFILESUFFIX')

CPlusPlusAction = SCons.Action.Action('$CXXCOM')

Object = SCons.Builder.Builder(name = 'Object',
                               action = { '.c'   : '$CCCOM',
                                          '.C'   : CPlusPlusAction,
                                          '.cc'  : CPlusPlusAction,
                                          '.cpp' : CPlusPlusAction,
                                          '.cxx' : CPlusPlusAction,
                                          '.c++' : CPlusPlusAction,
                                          '.C++' : CPlusPlusAction,
                                        },
                               prefix = '$OBJPREFIX',
                               suffix = '$OBJSUFFIX',
                               src_builder = [CFile, CXXFile])

Program = SCons.Builder.Builder(name = 'Program',
                                action = '$LINKCOM',
                                prefix = '$PROGPREFIX',
                                suffix = '$PROGSUFFIX',
                                src_suffix = '$OBJSUFFIX',
                                src_builder = Object,
                                scanner = SCons.Scanner.Prog.ProgScan())

Library = SCons.Builder.Builder(name = 'Library',
                                action = '$ARCOM',
                                prefix = '$LIBPREFIX',
                                suffix = '$LIBSUFFIX',
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
        'CCCOM'      : '$CC $CCFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'CFILESUFFIX' : '.c',
        'CXX'        : '$CC',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'CXXFILESUFFIX' : '.cc',
        'LINK'       : 'link',
        'LINKFLAGS'  : '/nologo',
        'LINKCOM'    : '$LINK $LINKFLAGS /OUT:$TARGET $_LIBDIRFLAGS $_LIBFLAGS $SOURCES',
        'AR'         : 'lib',
        'ARFLAGS'    : '/nologo',
        'ARCOM'      : '$AR $ARFLAGS /OUT:$TARGET $SOURCES',
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
        'DVISUFFIX'  : '.dvi',
        'BUILDERS'   : [Alias, CFile, CXXFile, DVI, Object, Program, Library],
        'SCANNERS'   : [CScan],
        'OBJPREFIX'  : '',
        'OBJSUFFIX'  : '.obj',
        'PROGPREFIX' : '',
        'PROGSUFFIX' : '.exe',
        'LIBPREFIX'  : '',
        'LIBSUFFIX'  : '.lib',
        'LIBDIRPREFIX'          : '/LIBPATH:',
        'LIBDIRSUFFIX'          : '',
        'LIBLINKPREFIX'         : '',
        'LIBLINKSUFFIX'         : '$LIBSUFFIX',
        'INCPREFIX'             : '/I',
        'INCSUFFIX'             : '',
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
        'CCCOM'      : '$CC $CCFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'CFILESUFFIX' : '.c',
        'CXX'        : 'c++',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'CXXFILESUFFIX' : '.cc',
        'LINK'       : '$CXX',
        'LINKFLAGS'  : '',
        'LINKCOM'    : '$LINK $LINKFLAGS -o $TARGET $SOURCES $_LIBDIRFLAGS $_LIBFLAGS',
        'AR'         : 'ar',
        'ARFLAGS'    : 'r',
        'RANLIB'     : ranlib,
        'RANLIBFLAGS' : '',
        'ARCOM'      : arcom,
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
        'DVISUFFIX'  : '.dvi',
        'BUILDERS'   : [Alias, CFile, CXXFile, DVI, Object, Program, Library],
        'SCANNERS'   : [CScan],
        'OBJPREFIX'  : '',
        'OBJSUFFIX'  : '.o',
        'PROGPREFIX' : '',
        'PROGSUFFIX' : (sys.platform == 'cygwin') and '.exe' or '',
        'LIBPREFIX'  : 'lib',
        'LIBSUFFIX'  : '.a',
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

