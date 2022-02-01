#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mylex.py')

test.write('SConstruct', """
env = Environment(LEX=r'%(_python_)s mylex.py', tools=['lex'])
env.CXXFile(target='foo', source='foo.ll')
env.Clone(CXXFILESUFFIX='.xyz').CXXFile(target='bar', source='bar.ll')

# Make sure that calling a Tool on a construction environment *after*
# we've set CXXFILESUFFIX doesn't overwrite the value.
env2 = Environment(tools=[], CXXFILESUFFIX='.env2')
env2.Tool('lex')
env2['LEX'] = r'%(_python_)s mylex.py'
env2.CXXFile(target='f3', source='f3.ll')
""" % locals())

input = r"""
int
main(int argc, char *argv[])
{
        argv[argc++] = (char *)"--";
        printf("LEX\n");
        printf("%s\n");
        exit (0);
}
"""

test.write('foo.ll', input % 'foo.ll')

test.write('bar.ll', input % 'bar.ll')

test.write('f3.ll', input % 'f3.ll')

test.run(arguments = '.')

test.must_exist(test.workpath('foo.cc'))

test.must_exist(test.workpath('bar.xyz'))

test.must_exist(test.workpath('f3.env2'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
