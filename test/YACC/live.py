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
Test YACC and YACCFLAGS with a live yacc compiler.
"""

import TestSCons
import sys
import os

_exe = TestSCons._exe
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

yacc = test.where_is('yacc') or test.where_is('bison') or test.where_is('win_bison')

if not yacc:
    test.skip_test('No yacc or bison found; skipping test.\n')

test.file_fixture('wrapper.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
foo = Environment(YACCFLAGS='-d', tools = ['default', 'yacc'])
yacc = foo.Dictionary('YACC')
bar = Environment(YACC = r'%(_python_)s wrapper.py ' + yacc, tools = ['default', 'yacc'])
foo.Program(target = 'foo', source = 'foo.y')
bar.Program(target = 'bar', source = 'bar.y')
foo.Program(target = 'hello', source = ['hello.cpp'])
foo.CXXFile(target = 'file.cpp', source = ['file.yy'], YACCFLAGS='-d')
foo.CFile(target = 'not_foo', source = 'foo.y')
""" % locals())

yacc = r"""
%%{
#include <stdio.h>
extern int yyparse();
int yyerror(char *s);
int yylex();

int main(void)
{
    return yyparse();
}

int yyerror(s)
char *s;
{
    fprintf(stderr, "%%s\n", s);
    return 0;
}

int yylex()
{
    int c;

    c = fgetc(stdin);
    return (c == EOF) ? 0 : c;
}
%%}
%%%%
input:  letter newline { printf("%s\n"); };
letter:  'a' | 'b';
newline: '\n';
"""

test.write("file.yy", """\
%token   GRAPH_T NODE_T EDGE_T DIGRAPH_T EDGEOP_T SUBGRAPH_T

%%
graph:        GRAPH_T
              ;

%%
""")

# Apparently, OS X now creates file.hpp like everybody else
# I have no idea when it changed; it was fixed in 10.4
#import sys
#if sys.platform[:6] == 'darwin':
#   file_hpp = 'file.cpp.h'
#else:
#   file_hpp = 'file.hpp'
file_hpp = 'file.hpp'

test.write("hello.cpp", """\
#include "%(file_hpp)s"

int main(void)
{
}
""" % locals())

test.write('foo.y', yacc % 'foo.y')

test.write('bar.y', yacc % 'bar.y')



test.run(arguments = 'foo' + _exe, stderr = None)

test.up_to_date(arguments = 'foo' + _exe)

test.must_not_exist(test.workpath('wrapper.out'))

test.run(program = test.workpath('foo'), stdin = "a\n", stdout = "foo.y\n")

test.must_exist(test.workpath('foo.h'))

test.run(arguments = '-c .')

test.must_not_exist(test.workpath('foo.h'))



test.run(arguments = 'not_foo.c')

test.up_to_date(arguments = 'not_foo.c')

test.must_not_exist(test.workpath('foo.h'))
test.must_exist(test.workpath('not_foo.h'))

test.run(arguments = '-c .')

test.must_not_exist(test.workpath('not_foo.h'))



test.run(arguments = 'bar' + _exe)

test.up_to_date(arguments = 'bar' + _exe)

test.must_match(test.workpath('wrapper.out'), "wrapper.py\n")

test.run(program = test.workpath('bar'), stdin = "b\n", stdout = "bar.y\n")



test.run(arguments = '.')

test.up_to_date(arguments = '.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
