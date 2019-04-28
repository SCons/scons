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
Verify appropriate printing of "is up to date" messages.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as ifp:
    f.write(ifp.read())
""")

test.write('SConstruct', """
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS =  { 'B' : B })
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
env.B(target = 'f3.out', source = 'f3.in')
env.B(target = 'f4.out', source = 'f4.in')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

test.run(arguments = 'f1.out f3.out')

expect = test.wrap_stdout("""\
scons: `f1.out' is up to date.
%(_python_)s build.py f2.out f2.in
scons: `f3.out' is up to date.
%(_python_)s build.py f4.out f4.in
""" % locals())

test.run(arguments = 'f1.out f2.out f3.out f4.out', stdout = expect)

# Make sure all of the "up to date" messages get printed even when -j
# is used.  This broke during signature refactoring development.
expected_lines = [
    "scons: `f1.out' is up to date.",
    "scons: `f2.out' is up to date.",
    "scons: `f3.out' is up to date.",
    "scons: `f4.out' is up to date.",
]

test.run(options = '-j4 f1.out f2.out f3.out f4.out')

test.must_contain_all_lines(test.stdout(), expected_lines)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
