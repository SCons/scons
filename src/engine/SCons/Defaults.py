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



if os.name == 'posix':

    object_suffix = '.o'
    program_suffix = None
    library_prefix = 'lib'
    library_suffix = '.a'

elif os.name == 'nt':

    object_suffix = '.obj'
    program_suffix = '.exe'
    library_prefix = None
    library_suffix = '.lib'



Object = SCons.Builder.Builder(name = 'Object',
                               action = '$CCCOM',
                               suffix = object_suffix,
                               src_suffix = '.c')

Program = SCons.Builder.Builder(name = 'Program',
                                action = '$LINKCOM',
                                suffix = program_suffix,
                                builders = [ Object ])

Library = SCons.Builder.Builder(name = 'Library',
                                action = 'ar r $target $sources\nranlib $target',
                                prefix = library_prefix,
                                suffix = library_suffix,
                                builders = [ Object ])



if os.name == 'posix':

    ConstructionEnvironment = {
        'CC'        : 'cc',
        'CCFLAGS'   : '',
        'CCCOM'     : '$CC $CCFLAGS -c -o $target $sources',
        'LINK'      : '$CC',
        'LINKFLAGS' : '',
        'LINKCOM'   : '$LINK $LINKFLAGS -o $target $sources',
        'BUILDERS'  : [Object, Program, Library],
        'ENV'       : { 'PATH' : '/usr/local/bin:/bin:/usr/bin' },
    }

elif os.name == 'nt':

    ConstructionEnvironment = {
        'CC'        : 'cl',
        'CCFLAGS'   : '/nologo',
        'CCCOM'     : '$CC $CCFLAGS /c $sources /Fo$target',
        'LINK'      : 'link',
        'LINKFLAGS' : '',
        'LINKCOM'   : '$LINK $LINKFLAGS /out:$target $sources',
        'BUILDERS'  : [Object, Program, Library],
        'ENV'       : {
                        'PATH'    : r'C:\Python20;C:\WINNT\system32;C:\WINNT;C:\Program Files\Microsoft Visual Studio\VC98\Bin\;',
                        'PATHEXT' : '.COM;.EXE;.BAT;.CMD'
                      },
    }
