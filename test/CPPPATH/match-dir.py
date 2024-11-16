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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Verify that we don't blow up if there's a directory name within
$CPPPATH that matches a #include file name.
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

# TODO(sgk):  get this to work everywhere by using fake compilers
if sys.platform.find('sunos') != -1:
    msg = 'SunOS C compiler does not handle this case; skipping test.\n'
    test.skip_test(msg)

test.subdir(['src'],
            ['src', 'inc'],
            ['src', 'inc', 'inc2'])

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
SConscript('src/SConscript', variant_dir = 'build', duplicate = 0)
""")

test.write(['src', 'SConscript'], """\
env = Environment(CPPPATH = ['#build/inc', '#build/inc/inc2'])
env.Object('foo.c')
""")

test.write(['src', 'foo.c'], """\
#include "inc1"
""")

test.subdir(['src', 'inc', 'inc1'])

test.write(['src', 'inc', 'inc2', 'inc1'], "\n")

test.run(arguments = '.')

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
