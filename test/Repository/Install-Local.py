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
import TestSCons

test = TestSCons.TestSCons()

test.subdir('repository', 'work', ['work', 'install'])

repository_install_file1 = test.workpath('repository', 'install', 'file1')
repository_install_file2 = test.workpath('repository', 'install', 'file2')
work_install_file1 = test.workpath('work', 'install', 'file1')
work_install_file2 = test.workpath('work', 'install', 'file2')

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
env = Environment()
env.Install('install', 'file1')
Local(r'%s')
Local(env.Install('install', 'file2'))
""" % os.path.join('install', 'file1'))

test.write(['repository', 'file1'], "repository/file1\n")
test.write(['repository', 'file2'], "repository/file2\n")

test.run(chdir = 'repository', options = opts, arguments = 'install')

test.must_match(repository_install_file1, "repository/file1\n", mode='r')
test.must_match(repository_install_file2, "repository/file2\n", mode='r')

test.up_to_date(chdir = 'repository', options = opts, arguments = 'install')

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', options = opts, arguments = 'install')

test.must_match(work_install_file1, "repository/file1\n", mode='r')
test.must_match(work_install_file2, "repository/file2\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = 'install')

#
test.write(['work', 'file1'], "work/file1\n")
test.write(['work', 'file2'], "work/file2\n")

test.run(chdir = 'work', options = opts, arguments = 'install')

test.must_match(work_install_file1, "work/file1\n", mode='r')
test.must_match(work_install_file2, "work/file2\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = 'install')

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
