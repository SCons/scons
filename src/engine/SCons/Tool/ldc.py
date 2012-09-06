"""SCons.Tool.ldc

Tool-specific initialization for the LDC compiler.
(http://www.dsource.org/projects/ldc)

Coded by Russel Winder (russel@winder.org.uk)
2012-05-09, 2012-09-06

Compiler variables:
    DC - The name of the D compiler to use.  Defaults to ldc2.
    DPATH - List of paths to search for import modules.
    DVERSIONS - List of version tags to enable when compiling.
    DDEBUG - List of debug tags to enable when compiling.

Linker related variables:
    LIBS - List of library files to link in.
    DLINK - Name of the linker to use.  Defaults to gcc.
    DLINKFLAGS - List of linker flags.

Lib tool variables:
    DLIB - Name of the lib tool to use.  Defaults to lib.
    DLIBFLAGS - List of flags to pass to the lib tool.
    LIBS - Same as for the linker. (libraries to pull into the .lib)
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
import subprocess

import SCons.Action
import SCons.Builder
import SCons.Defaults
import SCons.Scanner.D
import SCons.Tool

import SCons.Tool.DCommon

smart_link = {}
smart_lib = {}

def generate(env):
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    DAction = SCons.Action.Action('$DCOM', '$DCOMSTR')

    static_obj.add_action('.d', DAction)
    shared_obj.add_action('.d', DAction)
    static_obj.add_emitter('.d', SCons.Defaults.StaticObjectEmitter)
    shared_obj.add_emitter('.d', SCons.Defaults.SharedObjectEmitter)

    dc = env.Detect('ldc2')
    env['DC'] = dc
    env['DCOM'] = '$DC $_DINCFLAGS $_DVERFLAGS $_DDEBUGFLAGS $_DFLAGS -c -of=$TARGET $SOURCES'
    env['_DINCFLAGS'] = '$( ${_concat(DINCPREFIX, DPATH, DINCSUFFIX, __env__, RDirs, TARGET, SOURCE)}  $)'
    env['_DVERFLAGS'] = '$( ${_concat(DVERPREFIX, DVERSIONS, DVERSUFFIX, __env__)}  $)'
    env['_DDEBUGFLAGS'] = '$( ${_concat(DDEBUGPREFIX, DDEBUG, DDEBUGSUFFIX, __env__)} $)'
    env['_DFLAGS'] = '$( ${_concat(DFLAGPREFIX, DFLAGS, DFLAGSUFFIX, __env__)} $)'

    env['DPATH'] = ['#/']
    env['DFLAGS'] = []
    env['DVERSIONS'] = []
    env['DDEBUG'] = []

    if dc:
        SCons.Tool.DCommon.addDPATHToEnv(env, dc)

    env['DINCPREFIX'] = '-I='
    env['DINCSUFFIX'] = ''
    env['DVERPREFIX'] = '-version='
    env['DVERSUFFIX'] = ''
    env['DDEBUGPREFIX'] = '-debug='
    env['DDEBUGSUFFIX'] = ''
    env['DFLAGPREFIX'] = '-'
    env['DFLAGSUFFIX'] = ''
    env['DFILESUFFIX'] = '.d'

    env['DLINK'] = '$DC'
    env['DLINKCOM'] = '$DLINK -of$TARGET $SOURCES $DFLAGS $DLINKFLAGS $_DLINKLIBFLAGS'
    env['DLIB'] = 'lib'
    env['DLIBCOM'] = '$DLIB $_DLIBFLAGS -c $TARGET $SOURCES $_DLINKLIBFLAGS'

    env['_DLINKLIBFLAGS'] = '$( ${_concat(DLIBLINKPREFIX, LIBS, DLIBLINKSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['_DLIBFLAGS'] = '$( ${_concat(DLIBFLAGPREFIX, DLIBFLAGS, DLIBFLAGSUFFIX, __env__)} $)'
    env['DLINKFLAGS'] = []
    env['DLIBLINKPREFIX'] = '' if env['PLATFORM'] == 'win32' else '-L-l'
    env['DLIBLINKSUFFIX'] = '.lib' if env['PLATFORM'] == 'win32' else ''
    env['DLIBFLAGPREFIX'] = '-'
    env['DLIBFLAGSUFFIX'] = ''
    env['DLINKFLAGPREFIX'] = '-'
    env['DLINKFLAGSUFFIX'] = ''

    SCons.Tool.createStaticLibBuilder(env)

    # Basically, we hijack the link and ar builders with our own.
    # these builders check for the presence of D source, and swap out
    # the system's defaults for the Digital Mars tools.  If there's no D
    # source, then we silently return the previous settings.
    SCons.Tool.DCommon.setSmartLink(env, smart_link, smart_lib)

    # It is worth noting that the final space in these strings is
    # absolutely pivotal.  SCons sees these as actions and not generators
    # if it is not there. (very bad)
    env['ARCOM'] = '$SMART_ARCOM '
    env['LINKCOM'] = '$SMART_LINKCOM '


def exists(env):
    return env.Detect('ldc2')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
