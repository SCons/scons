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

#  Amended by Russel Winder <russel@russel.org.uk> 2010-05-05

import TestSCons

from os.path import abspath, dirname

import sys
sys.path.insert(1, abspath(dirname(__file__) + '/Support'))

from executablesSearch import isExecutableOfToolAvailable

_exe = TestSCons._exe
test = TestSCons.TestSCons()

if not isExecutableOfToolAvailable(test, 'ldc'):
    test.skip_test("Could not find 'ldc', skipping test.\n")

test.write('SConstruct', """\
import os
env = Environment(tools=['link', 'ldc'])
if env['PLATFORM'] == 'cygwin': env['OBJSUFFIX'] = '.obj'  # trick DMD
env.Program('foo', 'foo.d')
""")

test.write('foo.d', """\
import std.stdio;
int main(string[] args) {
    printf("Hello!");
    return 0;
}
""")

test.run()

test.run(program=test.workpath('foo'+_exe))

test.fail_test(not test.stdout() == 'Hello!')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
