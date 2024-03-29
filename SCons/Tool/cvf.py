"""SCons.Tool.cvf

Tool-specific initialization for the Compaq Visual Fortran compiler.

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

from . import fortran

compilers = ['f90']

def generate(env) -> None:
    """Add Builders and construction variables for compaq visual fortran to an Environment."""

    fortran.generate(env)

    env['FORTRAN']        = 'f90'
    env['FORTRANCOM']     = '$FORTRAN $FORTRANFLAGS $_FORTRANMODFLAG $_FORTRANINCFLAGS /compile_only ${SOURCES.windows} /object:${TARGET.windows}'
    env['FORTRANPPCOM']   = '$FORTRAN $FORTRANFLAGS $CPPFLAGS $_CPPDEFFLAGS $_FORTRANMODFLAG $_FORTRANINCFLAGS /compile_only ${SOURCES.windows} /object:${TARGET.windows}'
    env['SHFORTRANCOM']   = '$SHFORTRAN $SHFORTRANFLAGS $_FORTRANMODFLAG $_FORTRANINCFLAGS /compile_only ${SOURCES.windows} /object:${TARGET.windows}'
    env['SHFORTRANPPCOM'] = '$SHFORTRAN $SHFORTRANFLAGS $CPPFLAGS $_CPPDEFFLAGS $_FORTRANMODFLAG $_FORTRANINCFLAGS /compile_only ${SOURCES.windows} /object:${TARGET.windows}'
    env['OBJSUFFIX']      = '.obj'
    env['FORTRANMODDIR'] = '${TARGET.dir}'
    env['FORTRANMODDIRPREFIX'] = '/module:'
    env['FORTRANMODDIRSUFFIX'] = ''

def exists(env):
    return env.Detect(compilers)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
