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

python = TestSCons.python
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



test.write('mylex.py', """
import getopt
import string
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'tx', [])
opt_string = ''
for opt, arg in cmd_opts:
    opt_string = opt_string + ' ' + opt
for a in args:
    contents = open(a, 'rb').read()
    sys.stdout.write(string.replace(contents, 'LEXFLAGS', opt_string))
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LEX = r'%s mylex.py', LEXFLAGS = '-x', tools=['default', 'lex'])
env.Program(target = 'aaa', source = 'aaa.l')
""" % python)

test.write('aaa.l', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("LEXFLAGS\n");
	printf("aaa.l\n");
	exit (0);
}
""")

test.run(arguments = 'aaa' + _exe, stderr = None)

test.run(program = test.workpath('aaa' + _exe), stdout = " -x -t\naaa.l\n")



lex = test.where_is('lex')

if lex:

    test.write('SConstruct', """
foo = Environment()
bar = Environment(LEXFLAGS = '-b')
foo.Program(target = 'foo', source = 'foo.l')
bar.Program(target = 'bar', source = 'bar.l')
""")

    lex = r"""
%%%%
a	printf("A%sA");
b	printf("B%sB");
%%%%
int
yywrap()
{
    return 1;
}

main()
{
    yylex();
}
"""

    test.write('foo.l', lex % ('foo.l', 'foo.l'))

    test.write('bar.l', lex % ('bar.l', 'bar.l'))

    test.run(arguments = 'foo' + _exe, stderr = None)

    test.fail_test(os.path.exists(test.workpath('lex.backup')))

    test.run(program = test.workpath('foo'), stdin = "a\n", stdout = "Afoo.lA\n")

    test.run(arguments = 'bar' + _exe)

    test.fail_test(not os.path.exists(test.workpath('lex.backup')))

    test.run(program = test.workpath('bar'), stdin = "b\n", stdout = "Bbar.lB\n")

test.pass_test()
