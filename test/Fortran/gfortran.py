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

"""
Verify that the gfortran tool compiles a .f90 file to an executable,
one time with and one time without placing module files in a subdirectory
specified by FORTRANMODDIR.
"""

import TestSCons

test = TestSCons.TestSCons()

_exe = TestSCons._exe

gfortran = test.detect_tool('gfortran')

if not gfortran:
    test.skip_test("Could not find gfortran tool, skipping test.\n")

test.write('SConstruct', """
env = Environment(tools=['gfortran','link'])
env.Program('test1', 'test1.f90')
""")

test.write('test1.f90', """\
module test1mod
  implicit none
  contains
  subroutine hello
    implicit none
    print *, "hello"
  end subroutine hello
end module test1mod
program main
  use test1mod
  implicit none
  call hello()
end program main
""")

test.run(arguments = '.')

test.must_exist('test1' + _exe)
test.must_exist('test1mod.mod')

test.up_to_date(arguments = '.')


test.write('SConstruct', """
env = Environment(tools=['gfortran','link'], F90PATH='modules', FORTRANMODDIR='modules')
env.Program('test2', 'test2.f90')
""")

test.write('test2.f90', """\
module test2mod
  implicit none
  contains
  subroutine hello
    implicit none
    print *, "hello"
  end subroutine hello
end module test2mod
program main
  use test2mod
  implicit none
  call hello()
end program main
""")

test.run(arguments = '.')

test.must_exist('test2' + _exe)
test.must_exist(['modules', 'test2mod.mod'])

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
