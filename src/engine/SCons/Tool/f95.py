"""engine.SCons.Tool.f95

Tool-specific initialization for the generic Posix f95 Fortran compiler.

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

import SCons.Defaults
import SCons.Tool
import SCons.Util
import fortran

compilers = ['f95']

#
F95Action = SCons.Action.Action("$F95COM")
ShF95Action = SCons.Action.Action("$SHF95COM")
F95PPAction = SCons.Action.Action("$F95PPCOM")
ShF95PPAction = SCons.Action.Action("$SHF95PPCOM")

#
F95Suffixes = ['.f95']
F95PPSuffixes = []
if SCons.Util.case_sensitive_suffixes('.f95', '.F95'):
    F95PPSuffixes.append('.F95')
else:
    F95Suffixes.append('.F95')

#
F95Scan = SCons.Scanner.Fortran.FortranScan("F95PATH")

for suffix in F95Suffixes + F95PPSuffixes:
    SCons.Defaults.ObjSourceScan.add_scanner(suffix, F95Scan)

#
F95Generator = fortran.VariableListGenerator('F95', 'FORTRAN', '_FORTRAND')
F95FlagsGenerator = fortran.VariableListGenerator('F95FLAGS', 'FORTRANFLAGS')
ShF95Generator = fortran.VariableListGenerator('SHF95', 'SHFORTRAN', 'F95', 'FORTRAN', '_FORTRAND')
ShF95FlagsGenerator = fortran.VariableListGenerator('SHF95FLAGS', 'SHFORTRANFLAGS')

def add_to_env(env):
    """Add Builders and construction variables for f95 to an Environment."""
    env.AppendUnique(FORTRANSUFFIXES = F95Suffixes + F95PPSuffixes)

    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in F95Suffixes:
        static_obj.add_action(suffix, F95Action)
        shared_obj.add_action(suffix, ShF95Action)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)

    for suffix in F95PPSuffixes:
        static_obj.add_action(suffix, F95PPAction)
        shared_obj.add_action(suffix, ShF95PPAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)

    env['_F95G']      = F95Generator
    env['_F95FLAGSG'] = F95FlagsGenerator
    env['F95COM']     = '$_F95G $_F95FLAGSG $_F95INCFLAGS $_FORTRANMODFLAG -c -o $TARGET $SOURCES'
    env['F95PPCOM']   = '$_F95G $_F95FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F95INCFLAGS $_FORTRANMODFLAG -c -o $TARGET $SOURCES'

    env['_SHF95G']      = ShF95Generator
    env['_SHF95FLAGSG'] = ShF95FlagsGenerator
    env['SHF95COM']   = '$_SHF95G $_SHF95FLAGSG $_F95INCFLAGS $_FORTRANMODFLAG -c -o $TARGET $SOURCES'
    env['SHF95PPCOM'] = '$_SHF95G $_SHF95FLAGSG $CPPFLAGS $_CPPDEFFLAGS $_F95INCFLAGS $_FORTRANMODFLAG -c -o $TARGET $SOURCES'

    env['_F95INCFLAGS'] = '$( ${_concat(INCPREFIX, F95PATH, INCSUFFIX, __env__, RDirs)} $)'

def generate(env):
    fortran.add_to_env(env)
    add_to_env(env)

    env['_FORTRAND'] = env.Detect(compilers) or 'f95'

def exists(env):
    return env.Detect(compilers)
