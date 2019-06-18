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
Verify that we can set CFILESUFFIX to arbitrary values.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('mylex.py', """
import getopt
import sys
if sys.platform == 'win32':
    longopts = ['nounistd']
else:
    longopts = []
cmd_opts, args = getopt.getopt(sys.argv[1:], 't', longopts)
for a in args:
    with open(a, 'rb') as f:
        contents = f.read()
    sys.stdout.write((contents.replace(b'LEX', b'mylex.py')).decode())
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LEX = r'%(_python_)s mylex.py', tools = ['lex'])
env.CFile(target = 'foo', source = 'foo.l')
env.Clone(CFILESUFFIX = '.xyz').CFile(target = 'bar', source = 'bar.l')

# Make sure that calling a Tool on a construction environment *after*
# we've set CFILESUFFIX doesn't overwrite the value.
env2 = Environment(tools = [], CFILESUFFIX = '.env2')
env2.Tool('lex')
env2['LEX'] = r'%(_python_)s mylex.py'
env2.CFile(target = 'f3', source = 'f3.l')
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

test.write('foo.l', input % 'foo.l')

test.write('bar.l', input % 'bar.l')

test.write('f3.l', input % 'f3.l')

test.run(arguments = '.')

test.must_exist(test.workpath('foo.c'))

test.must_exist(test.workpath('bar.xyz'))

test.must_exist(test.workpath('f3.env2'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
