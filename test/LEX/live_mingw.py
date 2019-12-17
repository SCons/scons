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
Test LEX and LEXFLAGS and unistd.h with a live lex in mingw environment.
"""

import sys

import TestSCons

_exe = TestSCons._exe
_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test('Not windows environment; skipping test.\n')

if not test.where_is('gcc'):
        test.skip_test('No mingw or cygwin build environment found; skipping test.\n')

lex = test.where_is('lex') or test.where_is('flex')

if not lex:
    test.skip_test('No lex or flex found; skipping test.\n')

test.file_fixture('wrapper.py')

test.write('SConstruct', """
foo = Environment(tools=['default', 'mingw', 'lex'], LEXUNISTD="")
lex = foo.Dictionary('LEX')
bar = Environment(LEX = r'%(_python_)s wrapper.py ' + lex,
                  LEXFLAGS = '-b',
                  LEXUNISTD="",
                  tools=['default', 'mingw', 'lex'])
foo.Program(target = 'foo', source = 'foo.l')
bar.Program(target = 'bar', source = 'bar.l')
""" % locals())

lex = r"""
%%%%
a       printf("A%sA");
b       printf("B%sB");
%%%%
int
yywrap()
{
    return 1;
}

int
main()
{
    yylex();
}
"""

test.write('foo.l', lex % ('foo.l', 'foo.l'))

test.write('bar.l', lex % ('bar.l', 'bar.l'))

test.run(arguments = 'foo' + _exe, stderr = None)

test.must_not_exist(test.workpath('wrapper.out'))
test.must_not_exist(test.workpath('lex.backup'))

test.run(program = test.workpath('foo'), stdin = "a\n", stdout = "Afoo.lA\n")

test.run(arguments = 'bar' + _exe)

test.must_match(test.workpath('wrapper.out'), "wrapper.py\n")
test.must_exist(test.workpath('lex.backup'))

test.run(program = test.workpath('bar'), stdin = "b\n", stdout = "Bbar.lB\n")
test.must_contain(test.workpath('bar.c'), "unistd.h")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
