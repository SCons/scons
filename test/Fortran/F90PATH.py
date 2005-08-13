#!/usr/bin/env python
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
import os.path
import sys
import TestSCons

_exe = TestSCons._exe
FTN_LIB = TestSCons.fortran_lib
prog = 'prog' + _exe
subdir_prog = os.path.join('subdir', 'prog' + _exe)
variant_prog = os.path.join('variant', 'prog' + _exe)

args = prog + ' ' + subdir_prog + ' ' + variant_prog

test = TestSCons.TestSCons()

baselist = [
    '/opt/intel_fc_80',
    '/opt/intel/fc/9.0',
]

F90 = None
for base in baselist:
    ifort = os.path.join(base, 'bin', 'ifort')
    if os.path.exists(ifort):
        F90 = ifort

if not F90:
    l = string.join(baselist, '\n\t')
    test.skip_test('No (hard-coded) F90 compiler under:' + l + '\n')

LIBPATH = os.path.join(base, 'lib')
LIBS = ['irc']
os.environ['LD_LIBRARY_PATH'] = LIBPATH
    
test.subdir('include', 'subdir', ['subdir', 'include'], 'inc2')

test.write('SConstruct', """
env = Environment(F90 = r'%s',
                  F90PATH = ['$FOO'],
                  LINK = '$F90',
                  LIBPATH = %s,
                  LIBS = %s,
                  FOO='include')
obj = env.Object(target='foobar/prog', source='subdir/prog.f90')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

BuildDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(F90 = r'%s',
                  F90PATH=[include],
                  LINK = '$F90',
                  LIBPATH = %s,
                  LIBS = %s)
SConscript('variant/SConscript', "env")
""" % (F90, repr(LIBPATH), LIBS, F90, repr(LIBPATH), LIBS))

test.write(['subdir', 'SConscript'],
"""
Import("env")
env.Program(target='prog', source='prog.f90')
""")

test.write(['include', 'foo.f90'],
r"""
      PRINT *, 'include/foo.f90 1'
      INCLUDE 'bar.f90'
""")

test.write(['include', 'bar.f90'],
r"""
      PRINT *, 'include/bar.f90 1'
""")

test.write(['subdir', 'prog.f90'],
r"""
      PROGRAM PROG
      PRINT *, 'subdir/prog.f90'
      include 'foo.f90'
      STOP
      END
""")

test.write(['subdir', 'include', 'foo.f90'],
r"""
      PRINT *, 'subdir/include/foo.f90 1'
      INCLUDE 'bar.f90'
""")

test.write(['subdir', 'include', 'bar.f90'],
r"""
      PRINT *, 'subdir/include/bar.f90 1'
""")



test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = " subdir/prog.f90\n include/foo.f90 1\n include/bar.f90 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = " subdir/prog.f90\n subdir/include/foo.f90 1\n subdir/include/bar.f90 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = " subdir/prog.f90\n include/foo.f90 1\n include/bar.f90 1\n")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f90'))

test.up_to_date(arguments = args)

test.write(['include', 'foo.f90'],
r"""
      PRINT *, 'include/foo.f90 2'
      INCLUDE 'bar.f90'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = " subdir/prog.f90\n include/foo.f90 2\n include/bar.f90 1\n")

test.run(program = test.workpath(subdir_prog),
         stdout = " subdir/prog.f90\n subdir/include/foo.f90 1\n subdir/include/bar.f90 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = " subdir/prog.f90\n include/foo.f90 2\n include/bar.f90 1\n")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f90'))

test.up_to_date(arguments = args)

#
test.write(['include', 'bar.f90'],
r"""
      PRINT *, 'include/bar.f90 2'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = " subdir/prog.f90\n include/foo.f90 2\n include/bar.f90 2\n")

test.run(program = test.workpath(subdir_prog),
         stdout = " subdir/prog.f90\n subdir/include/foo.f90 1\n subdir/include/bar.f90 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = " subdir/prog.f90\n include/foo.f90 2\n include/bar.f90 2\n")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f90'))

test.up_to_date(arguments = args)

# Change F90PATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(F90 = r'%s',
                  F90PATH = Split('inc2 include'),
                  LINK = '$F90',
                  LIBPATH = %s,
                  LIBS = %s)
obj = env.Object(target='foobar/prog', source='subdir/prog.f90')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

BuildDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(F90 = r'%s',
                  F90PATH=['inc2', include],
                  LINK = '$F90',
                  LIBPATH = %s,
                  LIBS = %s)
SConscript('variant/SConscript', "env")
""" % (F90, repr(LIBPATH), LIBS, F90, repr(LIBPATH), LIBS))

test.up_to_date(arguments = args)

#
test.write(['inc2', 'foo.f90'],
r"""
      PRINT *, 'inc2/foo.f90 1'
      INCLUDE 'bar.f90'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = " subdir/prog.f90\n inc2/foo.f90 1\n include/bar.f90 2\n")

test.run(program = test.workpath(subdir_prog),
         stdout = " subdir/prog.f90\n subdir/include/foo.f90 1\n subdir/include/bar.f90 1\n")

test.run(program = test.workpath(variant_prog),
         stdout = " subdir/prog.f90\n include/foo.f90 2\n include/bar.f90 2\n")

test.up_to_date(arguments = args)

test.pass_test()
