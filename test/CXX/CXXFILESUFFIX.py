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
import os.path
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mylex.py', """
import getopt
import string
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 't', [])
for a in args:
    contents = open(a, 'rb').read()
    sys.stdout.write(string.replace(contents, 'LEX', 'mylex.py'))
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LEX = r'%(_python_)s mylex.py', tools = ['lex'])
env.CXXFile(target = 'foo', source = 'foo.ll')
env.Copy(CXXFILESUFFIX = '.xyz').CXXFile(target = 'bar', source = 'bar.ll')
""" % locals())

input = r"""
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("LEX\n");
        printf("%s\n");
        exit (0);
}
"""

test.write('foo.ll', input % 'foo.ll')

test.write('bar.ll', input % 'bar.ll')

test.run(arguments = '.')

test.fail_test(not os.path.exists(test.workpath('foo.cc')))

test.fail_test(not os.path.exists(test.workpath('bar.xyz')))

test.pass_test()
