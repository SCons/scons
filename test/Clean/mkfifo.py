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
Verify that SCons reports an error when cleaning up a target directory
containing a named pipe created with o.mkfifo().
"""

import os

import TestSCons

test = TestSCons.TestSCons()

if not hasattr(os, 'mkfifo'):
    test.skip_test('No os.mkfifo() function; skipping test\n')

test_dir_name = 'testdir'
pipe_path = os.path.join(test_dir_name, 'namedpipe')

test.write('SConstruct', """\
Execute(Mkdir("{0}"))
dir = Dir("{0}")
Clean(dir, '{0}')
""".format(test_dir_name))

test.run(arguments='-Q -q', stdout='Mkdir("{0}")\n'.format(test_dir_name))

os.mkfifo(pipe_path)

test.must_exist(test.workpath(pipe_path))

expect1 = """\
Mkdir("{0}")
Path '{1}' exists but isn't a file or directory.
scons: Could not remove '{0}': Directory not empty
""".format(test_dir_name, pipe_path)

expect2 = """\
Mkdir("{0}")
Path '{1}' exists but isn't a file or directory.
scons: Could not remove '{0}': File exists
""".format(test_dir_name, pipe_path)

test.run(arguments='-c -Q -q')

test.must_exist(test.workpath(pipe_path))

if test.stdout() not in [expect1, expect2]:
    test.diff(expect1, test.stdout(), 'STDOUT ')
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
