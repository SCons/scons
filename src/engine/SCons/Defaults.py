"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

The code that reads the registry to find MSVC components was borrowed 
from distutils.msvccompiler.

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



import os
import SCons.Action
import SCons.Builder
import SCons.Scanner.C
import SCons.Scanner.Prog
import string
import SCons.Errors
import SCons.Util

CFile = SCons.Builder.Builder(name = 'CFile',
                              action = { '.l'    : '$LEXCOM',
                                         '.y'    : '$YACCCOM',
                                       },
                              suffix = '.c')

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
                               src_builder = CFile)

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

CScan = SCons.Scanner.C.CScan()

def get_devstudio_versions ():
    """
    Get list of devstudio versions from the Windows registry.  Return a
    list of strings containing version numbers; an exception will be raised
    if we were unable to access the registry (eg. couldn't import
    a registry-access module) or the appropriate registry keys weren't
    found.
    """

    if not SCons.Util.can_read_reg:
        raise InternalError, "No Windows registry module was found"

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
        raise InternalError, "DevStudio was not found."
    
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
        raise InternalError, "No Windows registry module was found"

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
    raise InternalError, "%s was not found in the registry."%path

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
        'CXX'        : '$CC',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $_INCFLAGS /c $SOURCES /Fo$TARGET',
        'LINK'       : 'link',
        'LINKFLAGS'  : '/nologo',
        'LINKCOM'    : '$LINK $LINKFLAGS /OUT:$TARGET $_LIBDIRFLAGS $_LIBFLAGS $SOURCES',
        'AR'         : 'lib',
        'ARFLAGS'    : '/nologo',
        'ARCOM'      : '$AR $ARFLAGS /OUT:$TARGET $SOURCES',
        'LEX'        : 'lex',
        'LEXFLAGS'   : '',
        'LEXCOM'     : '$LEX $LEXFLAGS -o$TARGET $SOURCES',
        'YACC'       : 'yacc',
        'YACCFLAGS'  : '',
        'YACCCOM'    : '$YACC $YACCFLAGS -o $TARGET $SOURCES',
        'BUILDERS'   : [CFile, Object, Program, Library],
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
                                     + ";" + os.environ[PATH])
    

if os.name == 'posix':

    ConstructionEnvironment = {
        'CC'         : 'cc',
        'CCFLAGS'    : '',
        'CCCOM'      : '$CC $CCFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'CXX'        : 'c++',
        'CXXFLAGS'   : '$CCFLAGS',
        'CXXCOM'     : '$CXX $CXXFLAGS $_INCFLAGS -c -o $TARGET $SOURCES',
        'LINK'       : '$CXX',
        'LINKFLAGS'  : '',
        'LINKCOM'    : '$LINK $LINKFLAGS -o $TARGET $SOURCES $_LIBDIRFLAGS $_LIBFLAGS',
        'AR'         : 'ar',
        'ARFLAGS'    : 'r',
        'ARCOM'      : '$AR $ARFLAGS $TARGET $SOURCES\nranlib $TARGET',
        'LEX'        : 'lex',
        'LEXFLAGS'   : '',
        'LEXCOM'     : '$LEX $LEXFLAGS -o$TARGET $SOURCES',
        'YACC'       : 'yacc',
        'YACCFLAGS'  : '',
        'YACCCOM'    : '$YACC $YACCFLAGS -o $TARGET $SOURCES',
        'BUILDERS'   : [CFile, Object, Program, Library],
        'SCANNERS'   : [CScan],
        'OBJPREFIX'  : '',
        'OBJSUFFIX'  : '.o',
        'PROGPREFIX' : '',
        'PROGSUFFIX' : '',
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
    
    try:
        versions = get_devstudio_versions()
        ConstructionEnvironment = make_win32_env(versions[0]) #use highest version
    except:
        try:
            # We failed to detect DevStudio, so fall back to the
            # DevStudio environment variables:
            ConstructionEnvironment = make_win32_env_from_paths(
                os.environ["INCLUDE"], os.environ["LIB"], os.environ["PATH"])
        except KeyError:
            # The DevStudio environment variables don't exists,
            # so fall back to a reasonable default:
            MVSdir = r'C:\Program Files\Microsoft Visual Studio'
            MVSVCdir = r'%s\VC98' % MVSdir
            MVSCommondir = r'%s\Common' % MVSdir
            ConstructionEnvironment = make_win32_env_from_paths(
                r'%s\atl\include;%s\mfc\include;%s\include' % (MVSVCdir, MVSVCdir, MVSVCdir),
                r'%s\mvc\lib;%s\lib' % (MVSVCdir, MVSVCdir),
                (r'%s\MSDev98\Bin' % MVSCommondir) + os.pathsep + os.environ["PATH"])

