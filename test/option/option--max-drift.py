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

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as ifp:
    f.write(ifp.read())
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B }, tools=[])
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
""" % locals())

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")



test.run(arguments = 'f1.out')

test.run(arguments = 'f1.out f2.out',
         stdout = test.wrap_stdout(
"""scons: `f1.out' is up to date.
%(_python_)s build.py f2.out f2.in
""" % locals()))

atime = os.path.getatime(test.workpath('f1.in'))
mtime = os.path.getmtime(test.workpath('f1.in'))

test.up_to_date(options='--max-drift=0', arguments='f1.out f2.out')

test.write('f1.in', "f1.in delta\n")
os.utime(test.workpath('f1.in'), (atime,mtime))

test.up_to_date(options='--max-drift=0', arguments='f1.out f2.out')

expect = test.wrap_stdout(
"""%(_python_)s build.py f1.out f1.in
scons: `f2.out' is up to date.
""" % locals())

test.run(arguments = '--max-drift=-1 f1.out f2.out', stdout = expect)

# Test that Set/GetOption('max_drift') works:
test.write('SConstruct', """
DefaultEnvironment(tools=[])
assert GetOption('max_drift') == 2*24*60*60
SetOption('max_drift', 1)
assert GetOption('max_drift') == 1
""")

test.run()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
assert GetOption('max_drift') == 1
SetOption('max_drift', 10)
assert GetOption('max_drift') == 1
""")

test.run(arguments='--max-drift=1')

# Test that SetOption('max_drift') actually sets max_drift
# by mucking with the file timestamps to make SCons not realize the source has changed
test.write('SConstruct', """
DefaultEnvironment(tools=[])
SetOption('max_drift', 0)
B = Builder(action = r'%(_python_)s build.py $TARGETS $SOURCES')
env = Environment(BUILDERS = { 'B' : B }, tools=[])
env.B(target = 'foo.out', source = 'foo.in')
""" % locals())

test.write('foo.in', 'foo.in\n')

atime = os.path.getatime(test.workpath('foo.in'))
mtime = os.path.getmtime(test.workpath('foo.in'))

test.run()
test.must_match('foo.out', 'foo.in\n', mode='r')

test.write('foo.in', 'foo.in delta\n')
os.utime(test.workpath('foo.in'), (atime,mtime))

test.run()

test.must_match('foo.out', 'foo.in\n', mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
