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



test.write('myyacc.py', """
import getopt
import string
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:', [])
output = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    else: opt_string = opt_string + ' ' + opt
for a in args:
    contents = open(a, 'rb').read()
    output.write(string.replace(contents, 'YACC', 'myyacc.py'))
output.close()
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(YACC = r'%s myyacc.py')
env.Program(target = 'aaa', source = 'aaa.y')
""" % python)

test.write('aaa.y', r"""
int
main(int argc, char *argv[])
{
	argv[argc++] = "--";
	printf("YACC\n");
	printf("aaa.y\n");
	exit (0);
}
""")

test.run(arguments = 'aaa' + _exe, stderr = None)

test.run(program = test.workpath('aaa' + _exe), stdout = "myyacc.py\naaa.y\n")



yacc = None
for dir in string.split(os.environ['PATH'], os.pathsep):
    y = os.path.join(dir, 'yacc' + _exe)
    if os.path.exists(y):
        yacc = y
        break

if yacc:

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment()
yacc = foo.Dictionary('YACC')
bar = Environment(YACC = r'%s wrapper.py ' + yacc)
foo.Program(target = 'foo', source = 'foo.y')
bar.Program(target = 'bar', source = 'bar.y')
""" % python)

    yacc = r"""
%%{
#include <stdio.h>

main()
{
    yyparse();
}

yyerror(s)
char *s;
{
    fprintf(stderr, "%%s\n", s);
}

yylex()
{
    int c;

    c = fgetc(stdin);
    return (c == EOF) ? 0 : c;
}
%%}
%%%%
input:	letter newline { printf("%s\n"); };
letter:  'a' | 'b';
newline: '\n';
"""

    test.write('foo.y', yacc % 'foo.y')

    test.write('bar.y', yacc % 'bar.y')

    test.run(arguments = 'foo' + _exe, stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(program = test.workpath('foo'), stdin = "a\n", stdout = "foo.y\n")

    test.run(arguments = 'bar' + _exe)

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

    test.run(program = test.workpath('bar'), stdin = "b\n", stdout = "bar.y\n")

test.pass_test()
