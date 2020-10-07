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


import TestSCons

test = TestSCons.TestSCons()

test.subdir('install', 'repository', 'work')

install = test.workpath('install')
install_file = test.workpath('install', 'file')

opts = "-Y " + test.workpath('repository')

#
test.write(['repository', 'SConstruct'], r"""
env = Environment()
env.Install(r'%s', 'file')
""" % install)

test.write(['repository', 'file'], "repository/file\n")

# Make the entire repository non-writable, so we'll detect
# if we try to write into it accidentally.
test.writable('repository', 0)

test.run(chdir = 'work', options = opts, arguments = install)

test.must_match(install_file, "repository/file\n", mode='r')

test.up_to_date(chdir = 'work', options = opts, arguments = install)

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
