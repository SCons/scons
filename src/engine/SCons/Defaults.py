"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

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
import SCons.Builder
import SCons.Scanner.C
import SCons.Scanner.Prog

Object = SCons.Builder.Builder(name = 'Object',
                               action = { '.c'   : '$CCCOM',
                                          '.C'   : '$CXXCOM',
                                          '.cc'  : '$CXXCOM',
                                          '.cpp' : '$CXXCOM',
                                          '.cxx' : '$CXXCOM',
                                          '.c++' : '$CXXCOM',
                                          '.C++' : '$CXXCOM',
                                        },
                               prefix = '$OBJPREFIX',
                               suffix = '$OBJSUFFIX')

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
        'BUILDERS'   : [Object, Program, Library],
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

    MVSdir = r'C:\Program Files\Microsoft Visual Studio'
    MVSVCdir = r'%s\VC98' % MVSdir
    MVSCommondir = r'%s\Common' % MVSdir

    ConstructionEnvironment = {
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
        'BUILDERS'   : [Object, Program, Library],
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
                        'INCLUDE'  : r'%s\atl\include;%s\mfc\include;%s\include'
                                     % (MVSVCdir, MVSVCdir, MVSVCdir),
                        'LIB'      : r'%s\mvc\lib;%s\lib'
                                     % (MVSVCdir, MVSVCdir),
			'MSDEVDIR' : r'%s\MSDev98' % MVSCommondir,
                        'PATH'     : r'C:\Python20;C:\WINNT\system32;C:\WINNT;%s\Tools\WinNT;%s\MSDev98\Bin;%s\Tools;%s\Bin;'
                                     % (MVSCommondir, MVSCommondir,
                                        MVSCommondir, MVSVCdir),
                        'PATHEXT' : '.COM;.EXE;.BAT;.CMD',
                      },
    }
