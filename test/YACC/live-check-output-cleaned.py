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
Test that .output file is cleaned
"""

import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

yacc = test.where_is('yacc') or test.where_is('bison') or test.where_is('win_bison')

if not yacc:
    test.skip_test('No yacc or bison found; skipping test.\n')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
foo = Environment(YACCFLAGS='-v -d', tools = ['default', 'yacc'])
foo.CFile(source = 'foo.y')
""" % locals())

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
    return 0;
}

yylex()
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

test.write('foo.y', yacc % 'foo.y')

test.run('.', stderr = None)

test.up_to_date(arguments = 'foo.c')

test.must_exist(test.workpath('foo.output'))
test.must_exist(test.workpath('foo.c'))

test.run(arguments = '-c .')
test.must_not_exist(test.workpath('foo.output'))
test.must_not_exist(test.workpath('foo.c'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
