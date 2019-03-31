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
Verify the following things:
* _FORTRANMODFLAG is correctly constructed from FORTRANMODDIRPREFIX and
  FORTRANMODDIR.
* The dependency scanner does not expect a module file to be created
  from a "module procedure" statement.
* The dependency scanner expects the module files to be created in the correct
  module directory (this is verified by the test.up_to_date()).
"""

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

test.write('myfortran.py', r"""
import os.path
import re
import sys
# case insensitive matching, because Fortran is case insensitive
mod_regex = "(?im)^\\s*MODULE\\s+(?!PROCEDURE)(\\w+)"
with open(sys.argv[2]) as f:
    contents = f.read()
modules = re.findall(mod_regex, contents)
(prefix, moddir) = sys.argv[1].split('=')
if prefix != 'moduledir':
    sys.exit(1)
modules = [os.path.join(moddir, m.lower()+'.mod') for m in modules]
for t in sys.argv[3:] + modules:
    with open(t, 'wb') as f:
        f.write(('myfortran.py wrote %s\n' % os.path.split(t)[1]).encode())
""")

test.write('SConstruct', """
env = Environment(F90COM = r'%(_python_)s myfortran.py $_FORTRANMODFLAG $SOURCE $TARGET',
                  FORTRANMODDIRPREFIX='moduledir=', FORTRANMODDIR='modules')
env.Object(target = 'test1.obj', source = 'test1.f90')
env.Object(target = 'sub2/test2.obj', source = 'test1.f90',
           FORTRANMODDIR='${TARGET.dir}')
env.Object(target = 'sub3/test3.obj', source = 'test1.f90',
           F90COM = r'%(_python_)s myfortran.py moduledir=$FORTRANMODDIR $SOURCE $TARGET',
           FORTRANMODDIR='${TARGET.dir}')
""" % locals())

test.write('test1.f90', """\
module mod_foo
  implicit none
  interface q
    module procedure p
  end interface q
  contains
  subroutine p
    implicit none
    print *, 'mod_foo::p'
  end subroutine p
end module mod_foo
program test
  use mod_foo
  implicit none
  print *, 'test1.f90'
  call p
  call q
end
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.obj', "myfortran.py wrote test1.obj\n")
test.must_match(['modules', 'mod_foo.mod'], "myfortran.py wrote mod_foo.mod\n")
test.must_not_exist(['modules', 'p.mod'])

test.must_match(['sub2', 'test2.obj'], "myfortran.py wrote test2.obj\n")
test.must_match(['sub2', 'mod_foo.mod'], "myfortran.py wrote mod_foo.mod\n")

test.must_match(['sub3', 'test3.obj'], "myfortran.py wrote test3.obj\n")
test.must_match(['sub3', 'mod_foo.mod'], "myfortran.py wrote mod_foo.mod\n")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
