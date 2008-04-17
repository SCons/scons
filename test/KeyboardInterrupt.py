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
Verify that we handle keyboard interrupts (CTRL-C) correctly.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

if 'killpg' not in dir(os) or 'setpgrp' not in dir(os):
    test.skip_test("This Python version does not support killing process groups; skipping test.\n")

test.write('toto.c', r"""
void foo()
{}
""")

test.write('SConstruct', r"""
import os
import signal

# Make sure that SCons is a process group leader.
os.setpgrp()

all = []

def explode(env, target, source):
    os.killpg(0, signal.SIGINT)

for i in xrange(40):
    all += Object('toto%5d' % i, 'toto.c')

all+= Command( 'broken', 'toto.c', explode)

Default( Alias('all', all))
"""
)

interruptedStr = """\
.*\
scons: Build interrupted\\.
.*\
scons: building terminated because of errors\\.
.*\
scons: writing .sconsign file\\.
.*\
"""

def runtest(arguments):
    test.run(arguments='-c')
    test.run(arguments=arguments, status=2,
             stdout=interruptedStr, stderr=r'.*', match=TestSCons.match_re_dotall)

for i in range(2):
    runtest('-j1')
    runtest('-j4')
    runtest('-j8')
    runtest('-j16')
    runtest('-j32')
    runtest('-j64')

    runtest('-j1 --random')
    runtest('-j4 --random')
    runtest('-j8 --random')
    runtest('-j16 --random')
    runtest('-j32 --random')
    runtest('-j64 --random')
