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

lex = None
for dir in string.split(os.environ['PATH'], os.pathsep):
    l = os.path.join(dir, 'lex' + _exe)
    if os.path.exists(l):
        lex = l
        break

test = TestSCons.TestSCons()

test.no_result(not lex)

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
