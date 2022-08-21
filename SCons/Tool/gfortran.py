# MIT License
#
# Copyright The SCons Foundation
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

"""
Tool-specific initialization for gfortran, the GNU Fortran compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import SCons.Util

from . import fortran


def generate(env):
    """Add Builders and construction variables for gfortran to an
    Environment."""
    fortran.generate(env)

    for dialect in ['F77', 'F90', 'FORTRAN', 'F95', 'F03', 'F08']:
        env[f'{dialect}'] = 'gfortran'
        env[f'SH{dialect}'] = f'${dialect}'
        if env['PLATFORM'] in ['cygwin', 'win32']:
            env[f'SH{dialect}FLAGS'] = SCons.Util.CLVar(f'${dialect}FLAGS')
        else:
            env[f'SH{dialect}FLAGS'] = SCons.Util.CLVar(f'${dialect}FLAGS -fPIC')

        env[f'INC{dialect}PREFIX'] = "-I"
        env[f'INC{dialect}SUFFIX'] = ""

    env['FORTRANMODDIRPREFIX'] = "-J"


def exists(env):
    return env.Detect('gfortran')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
