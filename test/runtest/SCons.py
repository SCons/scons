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
Verify that we find tests under the SCons/ tree only if they end
with *Tests.py.
"""

import os

import TestRuntest

test = TestRuntest.TestRuntest()
test.subdir(['SCons'], ['SCons', 'suite'])

pythonstring = TestRuntest.pythonstring
pythonflags = TestRuntest.pythonflags
src_passTests_py = os.path.join('SCons', 'passTests.py')
src_suite_passTests_py = os.path.join('SCons', 'suite', 'passTests.py')

test.write_passing_test(['SCons', 'pass.py'])
test.write_passing_test(['SCons', 'passTests.py'])
test.write_passing_test(['SCons', 'suite', 'pass.py'])
test.write_passing_test(['SCons', 'suite', 'passTests.py'])

expect_stdout = """\
%(pythonstring)s%(pythonflags)s %(src_passTests_py)s
PASSING TEST STDOUT
%(pythonstring)s%(pythonflags)s %(src_suite_passTests_py)s
PASSING TEST STDOUT
""" % locals()

expect_stderr = """\
PASSING TEST STDERR
PASSING TEST STDERR
""" % locals()

test.run(arguments='-k SCons', stdout=expect_stdout, stderr=expect_stderr)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
