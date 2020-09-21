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

import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

if sys.platform == 'win32':
    test.skip_test('CXXVERSION not set with MSVC, skipping test.')


test.write("versioned.py", """\
import subprocess
import sys
if '-dumpversion' in sys.argv:
    print('3.9.9')
    sys.exit(0)
if '--version' in sys.argv:
    print('this is version 2.9.9 wrapping', sys.argv[2])
    sys.exit(0)
if sys.argv[1] not in [ '2.9.9', '3.9.9' ]:
    print('wrong version', sys.argv[1], 'when wrapping', sys.argv[2])
    sys.exit(1)
subprocess.run(" ".join(sys.argv[2:]), shell=True)
""")

test.write('SConstruct', """
cxx = Environment().Dictionary('CXX')
foo = Environment(CXX = r'%(_python_)s versioned.py "${CXXVERSION}" ' + cxx)
foo.Program(target = 'foo', source = 'foo.cpp')
""" % locals())

test.write('foo.cpp', r"""
#include <stdio.h>
#include <stdlib.h>

int
main(int argc, char *argv[])
{
        printf("foo.c\n");
        exit (0);
}
""")

test.run(arguments = 'foo' + _exe)

test.up_to_date(arguments = 'foo' + _exe)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
