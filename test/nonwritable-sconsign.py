#!/usr/bin/env python
#
# Copyright (c) 2001 Steven Knight
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

__revision__ = "test/nonwritable-sconsign.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import os

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
env.Program(target = 'foo1', source = 'f1.c')
""")

test.write('f1.c', """
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("f1.c\n");
	exit (0);
}
""")

test.write('.sconsign', "")

# For *NIX, systems, make .sconsign not writable.
# For Win32 systems, open it to lock it.
os.chmod(test.workpath('.sconsign'), 0444)
f = open(test.workpath('.sconsign'), 'r')

test.run(arguments = ".")
test.run(program = test.workpath('foo1'), stdout = "f1.c\n")

os.chmod(test.workpath('.sconsign'), 0666)
f.close()

test.pass_test()
