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
Verify that the D scanner can return multiple modules imported by
a single statement.
"""

import TestSCons

import sys
from os.path import abspath, dirname, join
sys.path.append(join(dirname(abspath(__file__)), 'Support'))
from executablesSearch import isExecutableOfToolAvailable

test = TestSCons.TestSCons()

_obj = TestSCons._obj

if not isExecutableOfToolAvailable(test, 'dmd'):
    test.skip_test("Could not find 'dmd'; skipping test.\n")

test.subdir(['p'])

test.write('SConstruct', """
env = Environment()
env.Program('test1.d')
env.Program('test2.d')
""")

test.write(['test1.d'], """\
import module1;
import module2;
import module3;
import p.submodule1;
import p.submodule2;

int main() {
   return 0;
}
""")

test.write(['test2.d'], """\
import
   module1,
   module2,
   module3;
import
   p.submodule1,
   p.submodule2;

int main() {
   return 0;
}
""")

test.write(['ignored.d'], """\
module  ignored;

int something;
""")

test.write(['module1.d'], """\
module  module1;

int something;
""")

test.write(['module2.d'], """\
module  module2;

int something;
""")

test.write(['module3.di'], """\
module  module3;

int something;
""")

test.write(['p', 'ignored.d'], """\
module  p.ignored;

int something;
""")

test.write(['p', 'submodule1.d'], """\
module  p.submodule1;

int something;
""")

test.write(['p', 'submodule2.d'], """\
module p.submodule2;

int something;
""")

arguments = 'test1%(_obj)s test2%(_obj)s' % locals()

test.run(arguments = arguments)

test.up_to_date(arguments = arguments)

test.write(['module2.d'], """\
module  module2;

int something_else;
""")

test.not_up_to_date(arguments = arguments)

test.up_to_date(arguments = arguments)

test.write(['p', 'submodule2.d'], """\
module p.submodule2;

int something_else;
""")

test.not_up_to_date(arguments = arguments)

test.up_to_date(arguments = arguments)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
