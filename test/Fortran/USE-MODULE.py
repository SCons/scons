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

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



test.write('myfortran.py', r"""
import os.path
import re
import sys
mod_regex = "(?im)^\\s*MODULE\\s+(?!PROCEDURE)(\\w+)"
with open(sys.argv[1]) as f:
    contents = f.read()
modules = re.findall(mod_regex, contents)
modules = [m.lower()+'.mod' for m in modules]
for t in sys.argv[2:] + modules:
    with open(t, 'wb') as f:
        f.write(('myfortran.py wrote %s\n' % os.path.split(t)[1]).encode())
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(FORTRANCOM = r'%(_python_)s myfortran.py $SOURCE $TARGET')
env.Object(target = 'test1.obj', source = 'test1.f')
""" % locals())

test.write('test1.f', """\
      PROGRAM TEST
      USE MOD_FOO
      USE MOD_BAR
      PRINT *,'TEST.f'
      CALL P
      STOP
      END
      MODULE MOD_FOO
         IMPLICIT NONE
         CONTAINS
         SUBROUTINE P
            PRINT *,'mod_foo'
         END SUBROUTINE P
      END MODULE MOD_FOO
      MODULE PROCEDURE MOD_BAR
         IMPLICIT NONE
         CONTAINS
         SUBROUTINE P
            PRINT *,'mod_bar'
         END SUBROUTINE P
      END MODULE MOD_BAR
""")

test.run(arguments = '.', stderr = None)

test.must_match('test1.obj', "myfortran.py wrote test1.obj\n")
test.must_match('mod_foo.mod', "myfortran.py wrote mod_foo.mod\n")
test.must_not_exist('mod_bar.mod')

test.up_to_date(arguments = '.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
