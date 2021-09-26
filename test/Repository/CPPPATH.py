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

import sys
from TestSCons import TestSCons

test = TestSCons()

test.subdir('repository',
            ['repository', 'include1'],
            ['repository', 'include2'],
            'work')

work_foo = test.workpath('work', 'foo')

opts = '-Y ' + test.workpath('repository')

test.write(['repository', 'include1', 'foo.h'], r"""
#define STRING  "repository/include1/foo.h"
""")

test.write(['repository', 'include2', 'foo.h'], r"""
#define STRING  "repository/include2/foo.h"
""")

test.write(['repository', 'foo.c'], r"""
#include <stdio.h>
#include <stdlib.h>
#include <foo.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("%s\n", STRING);
        exit (0);
}
""")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

#
test.write(['work', 'SConstruct'], """
env = Environment(CPPPATH = ['include1', 'include2'])
env.Program(target = 'foo', source = 'foo.c')
""")

test.run(chdir = 'work', options = opts, arguments = '.')

test.run(program = work_foo, stdout = "repository/include1/foo.h\n")

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

#
test.write(['work', 'SConstruct'], """
env = Environment(CPPPATH = ['include2', 'include1'])
env.Program(target = 'foo', source = 'foo.c')
""")

test.run(chdir = 'work', options = opts, arguments = '.')

test.run(program = work_foo, stdout = "repository/include2/foo.h\n")

test.up_to_date(chdir = 'work', options = opts, arguments = '.')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
