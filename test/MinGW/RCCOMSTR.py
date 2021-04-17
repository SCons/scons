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

"""
Test that the $RCCOMSTR construction variable allows you to customize
the displayed string when rc is called when using MinGW.
This test does not use a compiler.
"""

import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if sys.platform in ('irix6',):
    test.skip_test("Skipping mingw test on non-Windows %s platform."%sys.platform)

test.file_fixture('mycompile.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(
    tools=['default', 'mingw'],
    RCCOM=r'%(_python_)s mycompile.py rc $TARGET $SOURCES',
    RCCOMSTR='RCing $TARGET from $SOURCE',
)
env.RES(target='aaa', source='aaa.rc')
""" % locals())

test.write('aaa.rc', "aaa.rc\n/*rc*/\n")

test.run(stdout = test.wrap_stdout("""\
RCing aaa.o from aaa.rc
"""))

test.must_match('aaa.o', "aaa.rc\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
