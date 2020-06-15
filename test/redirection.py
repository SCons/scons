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

test = TestSCons.TestSCons()

test.write('cat.py', r"""
import sys

# write binary to stdout
if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)

try:
    with open(sys.argv[1], 'rb') as f:
        indata = f.read()
except IndexError:
    indata = sys.stdin.buffer.read()
    
sys.stdout.buffer.write(indata)
sys.exit(0)
""")

test.write('SConstruct', r"""
env = Environment()
env.Command(target='foo1', source='bar1',
            action= r'%(_python_)s cat.py $SOURCES > $TARGET')
env.Command(target='foo2', source='bar2',
            action= r'%(_python_)s cat.py < $SOURCES > $TARGET')
env.Command(target='foo3', source='bar3',
            action=r'%(_python_)s cat.py $SOURCES | %(_python_)s cat.py > $TARGET')
env.Command(target='foo4', source='bar4',
            action=r'%(_python_)s cat.py <$SOURCES |%(_python_)s cat.py >$TARGET')
""" % locals())

test.write('bar1', 'bar1\r\n')
test.write('bar2', 'bar2\r\n')
test.write('bar3', 'bar3\r\n')
test.write('bar4', 'bar4\r\n')

test.run(arguments='.')

test.must_match('foo1', 'bar1\r\n')
test.must_match('foo2', 'bar2\r\n')
test.must_match('foo3', 'bar3\r\n')
test.must_match('foo4', 'bar4\r\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
