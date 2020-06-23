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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
_exe = TestSCons._exe

test.file_fixture('mylink.py')
test.file_fixture(['fixture', 'myfortran_flags.py'])

test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  LINKFLAGS = [],
                  F77 = r'%(_python_)s myfortran_flags.py g77',
                  F77FLAGS = '-x')
env.Program(target = 'test09', source = 'test09.f77')
env.Program(target = 'test10', source = 'test10.F77')
""" % locals())

test.write('test09.f77', "This is a .f77 file.\n#link\n#g77\n")
test.write('test10.F77', "This is a .F77 file.\n#link\n#g77\n")

test.run(arguments = '.', stderr = None)

test.must_match('test09' + _exe, " -c -x\nThis is a .f77 file.\n")
test.must_match('test10' + _exe, " -c -x\nThis is a .F77 file.\n")


fc = 'f77'
g77 = test.detect_tool(fc)

if g77:

    directory = 'x'
    test.subdir(directory)

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
foo = Environment(F77 = '%(fc)s', tools = ['default', 'f77'], F77FILESUFFIXES = [".f"])
f77 = foo.Dictionary('F77')
bar = foo.Clone(F77 = r'%(_python_)s wrapper.py ' + f77, F77FLAGS = '-I%(directory)s')
foo.Program(target = 'foo', source = 'foo.f')
bar.Program(target = 'bar', source = 'bar.f')
""" % locals())

    test.write('foo.f', r"""
      PROGRAM FOO
      PRINT *,'foo.f'
      STOP
      END
""")

    test.write('bar.f', r"""
      PROGRAM BAR
      PRINT *,'bar.f'
      STOP
      END
""")


    test.run(arguments = 'foo' + _exe, stderr = None)

    test.run(program = test.workpath('foo'), stdout =  " foo.f\n")

    test.must_not_exist('wrapper.out')

    import sys
    if sys.platform[:5] == 'sunos':
        test.run(arguments = 'bar' + _exe, stderr = None)
    else:
        test.run(arguments = 'bar' + _exe)

    test.run(program = test.workpath('bar'), stdout =  " bar.f\n")

    test.must_match('wrapper.out', "wrapper.py\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
