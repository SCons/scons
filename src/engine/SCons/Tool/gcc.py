"""SCons.Tool.gcc

Tool-specific initialization for gcc.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

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

import os.path

import SCons.Tool
import SCons.Defaults
import SCons.Util

compilers = ['cc', 'gcc']

CSuffixes = ['.c']
if os.path.normcase('.c') == os.path.normcase('.C'):
    CSuffixes.append('.C')

def generate(env):
    """Add Builders and construction variables for gcc to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)

    env['CC']        = env.Detect(compilers) or 'cc'
    env['CCFLAGS']   = ''
    env['CCCOM']     = '$CC $CCFLAGS $CPPFLAGS $_CPPINCFLAGS -c -o $TARGET $SOURCES'
    env['SHCC']      = '$CC'
    env['SHCCFLAGS'] = '$CCFLAGS -fPIC'
    env['SHCCCOM']   = '$SHCC $SHCCFLAGS $CPPFLAGS $_CPPINCFLAGS -c -o $TARGET $SOURCES'
    env['SHOBJSUFFIX'] = '.os'
    env['INCPREFIX']  = '-I'
    env['INCSUFFIX']  = ''
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 0

    env['CFILESUFFIX'] = '.c'

def exists(env):
    return env.Detect(compilers)
