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

import os.path
import sys

import TestSCons
import TestCmd

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)

test.write("SConstruct","""
b=Builder(name='b', action='foo')
""")

test.run(arguments='.', stderr=r"""
scons: warning: The use of the 'name' parameter to Builder\(\) is deprecated\.
File "SConstruct", line 2, in \?
""")

test.run(arguments='--warn=no-deprecated .', stderr='')

test.run(arguments='--warn=no-all .', stderr='')

test.run(arguments='--warn=no-all --warn=deprecated .', stderr=r"""
scons: warning: The use of the 'name' parameter to Builder\(\) is deprecated\.
File "SConstruct", line 2, in \?
""")

test.write("SConstruct","""
def build(target, source, env):
    pass

env=Environment()
env['BUILDERS']['test'] = Builder(action=build)
env.test(target='foo', source='foo.c')
""")

test.write("foo.c","""
#include "not_there.h"
""")

test.run(arguments='--warn=dependency .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
File ".+", line \d+, in .+
""")

test.run(arguments='--warn=all .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
File ".+", line \d+, in .+
""")

test.run(arguments='--warn=all --warn=no-dependency .', stderr="")

test.run(arguments='--warn=no-dependency --warn=all .', stderr=r"""
scons: warning: No dependency generated for file: not_there\.h \(included from: foo\.c\) \-\- file not found
File ".+", line \d+, in .+
""")

test.pass_test()
