#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

python = sys.executable

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

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
env = Environment(LEX = r'%s mylex.py')
env.Program(target = 'aaa', source = 'aaa.l')
""" % python)

test.write('aaa.l', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("LEX\n");
	printf("aaa.l\n");
	exit (0);
}
""")

test.run(arguments = 'aaa' + _exe, stderr = None)

test.run(program = test.workpath('aaa' + _exe), stdout = "mylex.py\naaa.l\n")



lex = test.where_is('lex')

if lex:

    test.write("wrapper.py", """import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment()
lex = foo.Dictionary('LEX')
bar = Environment(LEX = r'%s wrapper.py ' + lex)
foo.Program(target = 'foo', source = 'foo.l')
bar.Program(target = 'bar', source = 'bar.l')
""" % python)

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

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(program = test.workpath('foo'), stdin = "a\n", stdout = "Afoo.lA\n")

    test.run(arguments = 'bar' + _exe)

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

    test.run(program = test.workpath('bar'), stdin = "b\n", stdout = "Bbar.lB\n")

test.pass_test()
