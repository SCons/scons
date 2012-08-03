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

args = prog + ' ' + variant_prog + ' ' + subdir_prog

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
env = Environment(F77 = '%s',
                  F77PATH = ['$FOO', '${TARGET.dir}', '${SOURCE.dir}'],
                  FOO='include',
                  F77FLAGS = '-x f77')
obj = env.Object(target='foobar/prog', source='subdir/prog.f77')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

VariantDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(F77 = '%s',
                  F77PATH=[include, '#foobar', '#subdir'],
                  F77FLAGS = '-x f77')
SConscript('variant/SConscript', "env")
""" % (fc, fc))

test.write(['subdir', 'SConscript'],
"""
Import("env")
env.Program(target='prog', source='prog.f77')
""")

test.write(['include', 'foo.f77'],
r"""
      PRINT *, 'include/foo.f77 1'
      INCLUDE 'bar.f77'
""")

test.write(['include', 'bar.f77'],
r"""
      PRINT *, 'include/bar.f77 1'
""")

test.write(['subdir', 'prog.f77'],
r"""
      PROGRAM PROG
      PRINT *, 'subdir/prog.f77'
      include 'foo.f77'
      include 'sss.f77'
      include 'ttt.f77'
      STOP
      END
""")

test.write(['subdir', 'include', 'foo.f77'],
r"""
      PRINT *, 'subdir/include/foo.f77 1'
      INCLUDE 'bar.f77'
""")

test.write(['subdir', 'include', 'bar.f77'],
r"""
      PRINT *, 'subdir/include/bar.f77 1'
""")

test.write(['subdir', 'sss.f77'],
r"""
      PRINT *, 'subdir/sss.f77'
""")

test.write(['subdir', 'ttt.f77'],
r"""
      PRINT *, 'subdir/ttt.f77'
""")



test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 1
 include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f77
 subdir/include/foo.f77 1
 subdir/include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 1
 include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f77'))

test.up_to_date(arguments = args)



test.write(['include', 'foo.f77'],
r"""
      PRINT *, 'include/foo.f77 2'
      INCLUDE 'bar.f77'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 2
 include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f77
 subdir/include/foo.f77 1
 subdir/include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 2
 include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f77'))

test.up_to_date(arguments = args)



#
test.write(['include', 'bar.f77'],
r"""
      PRINT *, 'include/bar.f77 2'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 2
 include/bar.f77 2
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f77
 subdir/include/foo.f77 1
 subdir/include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 2
 include/bar.f77 2
 subdir/sss.f77
 subdir/ttt.f77
""")

# Make sure we didn't duplicate the source file in the variant subdirectory.
test.must_not_exist(test.workpath('variant', 'prog.f77'))

test.up_to_date(arguments = args)



# Change F77PATH and make sure we don't rebuild because of it.
test.write('SConstruct', """
env = Environment(F77 = '%s',
                  F77PATH = Split('inc2 include ${TARGET.dir} ${SOURCE.dir}'),
                  F77FLAGS = '-x f77')
obj = env.Object(target='foobar/prog', source='subdir/prog.f77')
env.Program(target='prog', source=obj)
SConscript('subdir/SConscript', "env")

VariantDir('variant', 'subdir', 0)
include = Dir('include')
env = Environment(F77 = '%s',
                  F77PATH=['inc2', include, '#foobar', '#subdir'],
                  F77FLAGS = '-x f77')
SConscript('variant/SConscript', "env")
""" % (fc, fc))

test.up_to_date(arguments = args)

#
test.write(['inc2', 'foo.f77'],
r"""
      PRINT *, 'inc2/foo.f77 1'
      INCLUDE 'bar.f77'
""")

test.run(arguments = args)

test.run(program = test.workpath(prog),
         stdout = """\
 subdir/prog.f77
 inc2/foo.f77 1
 include/bar.f77 2
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(subdir_prog),
         stdout = """\
 subdir/prog.f77
 subdir/include/foo.f77 1
 subdir/include/bar.f77 1
 subdir/sss.f77
 subdir/ttt.f77
""")

test.run(program = test.workpath(variant_prog),
         stdout = """\
 subdir/prog.f77
 include/foo.f77 2
 include/bar.f77 2
 subdir/sss.f77
 subdir/ttt.f77
""")

test.up_to_date(arguments = args)



# Check that a null-string F77PATH doesn't blow up.
test.write('SConstruct', """
env = Environment(tools = ['f77'], F77PATH = '', F77FLAGS = '-x f77')
env.Object('foo', source = 'empty.f77')
""")

test.write('empty.f77', '')

test.run(arguments = '.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
