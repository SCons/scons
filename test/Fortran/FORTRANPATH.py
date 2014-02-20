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

import TestSCons

_exe = TestSCons._exe
prog = 'prog' + _exe
subdir_prog = os.path.join('subdir', 'prog' + _exe)
variant_prog = os.path.join('variant', 'prog' + _exe)

args = prog + ' ' + subdir_prog + ' ' + variant_prog

test = TestSCons.TestSCons()

fc = 'f77'
if not test.detect_tool(fc):
    test.skip_test('Could not find a f77 tool; skipping test.\n')
    
test.subdir('include',
            'subdir',
            ['subdir', 'include'],
            'foobar',
            'inc2')



test.write('SConstruct', """
env = Environment(FORTRAN = '%s',
                  FORTRANPATH = ['$FOO', '${TARGET.dir}', '${SOURCE.dir}'],
                  FOO='include')
obj = env.Object(target='foobar/prog', source='subdir/prog.f')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

VariantDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(FORTRAN = '%s',
                  FORTRANPATH=[include, '#foobar', '#subdir'])
SConscript('variant/SConscript', "env")
""" % (fc, fc))

test.write(['subdir', 'SConscript'],
"""
Import("env")
env.Program(target='prog', source='prog.f')
""")

test.write(['include', 'foo.f'],
r"""
      PRINT *, 'include/foo.f 1'
      INCLUDE 'bar.f'
""")

test.write(['include', 'bar.f'],
r"""
      PRINT *, 'include/bar.f 1'
""")

test.write(['subdir', 'prog.f'],
r"""
      PROGRAM PROG
      PRINT *, 'subdir/prog.f'
      include 'foo.f'
      include 'sss.f'
      include 'ttt.f'
      STOP
      END
""")

test.write(['subdir', 'include', 'foo.f'],
r"""
      PRINT *, 'subdir/include/foo.f 1'
      INCLUDE 'bar.f'
""")

test.write(['subdir', 'include', 'bar.f'],
r"""
      PRINT *, 'subdir/include/bar.f 1'
""")

test.write(['subdir', 'sss.f'],
r"""
      PRINT *, 'subdir/sss.f'
""")

test.write(['subdir', 'ttt.f'],
r"""
      PRINT *, 'subdir/ttt.f'
""")


import sys
if sys.platform[:5] == 'sunos':
    # Sun f77 always put some junk in stderr
    test.run(arguments = args, stderr = None)
else:
    test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 1
 include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f
 subdir/include/foo.f 1
 subdir/include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 1
 include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f'))

test.up_to_date(arguments = args)



test.write(['include', 'foo.f'],
r"""
      PRINT *, 'include/foo.f 2'
      INCLUDE 'bar.f'
""")

if sys.platform[:5] == 'sunos':
    # Sun f77 always put some junk in stderr
    test.run(arguments = args, stderr = None)
else:
    test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 2
 include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f
 subdir/include/foo.f 1
 subdir/include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 2
 include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f'))

test.up_to_date(arguments = args)



#
test.write(['include', 'bar.f'],
r"""
      PRINT *, 'include/bar.f 2'
""")

if sys.platform[:5] == 'sunos':
    # Sun f77 always put some junk in stderr
    test.run(arguments = args, stderr = None)
else:
    test.run(arguments = args)


test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 2
 include/bar.f 2
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f
 subdir/include/foo.f 1
 subdir/include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 2
 include/bar.f 2
 subdir/sss.f
 subdir/ttt.f
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f'))

test.up_to_date(arguments = args)



# Change FORTRANPATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(FORTRAN = '%s',
                  FORTRANPATH = Split('inc2 include ${TARGET.dir} ${SOURCE.dir}'))
obj = env.Object(target='foobar/prog', source='subdir/prog.f')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

VariantDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(FORTRAN = '%s',
                  FORTRANPATH=['inc2', include, '#foobar', '#subdir'])
SConscript('variant/SConscript', "env")
""" % (fc, fc))

test.up_to_date(arguments = args)



#
test.write(['inc2', 'foo.f'],
r"""
      PRINT *, 'inc2/foo.f 1'
      INCLUDE 'bar.f'
""")

if sys.platform[:5] == 'sunos':
    # Sun f77 always put some junk in stderr
    test.run(arguments = args, stderr = None)
else:
    test.run(arguments = args)


test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f
 inc2/foo.f 1
 include/bar.f 2
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f
 subdir/include/foo.f 1
 subdir/include/bar.f 1
 subdir/sss.f
 subdir/ttt.f
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f
 include/foo.f 2
 include/bar.f 2
 subdir/sss.f
 subdir/ttt.f
""")

test.up_to_date(arguments = args)



# Check that a null-string FORTRANPATH doesn't blow up.
test.write('SConstruct', """
env = Environment(FORTRANPATH = '')
env.Object('foo', source = 'empty.f')
""")

test.write('empty.f', '')

if sys.platform[:5] == 'sunos':
    # Sun f77 always put some junk in stderr
    test.run(arguments = '.', stderr = None)
else:
    test.run(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
