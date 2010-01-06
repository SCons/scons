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
Verify ability to "check out" an SCons revision from a fake
Subversion utility.
"""

import re
import tempfile

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.write_sample_project('foo.tar')

_python_ = TestSCons_time._python_
my_svn_py = test.write_fake_svn_py('my_svn.py')

test.write('config', """\
svn = r'%(_python_)s %(my_svn_py)s'
""" % locals())

test.run(arguments = 'run -f config --svn http://xyzzy --number 617,716 foo.tar')

test.must_exist('foo-617-0.log',
                'foo-617-0.prof',
                'foo-617-1.log',
                'foo-617-1.prof',
                'foo-617-2.log',
                'foo-617-2.prof')

test.must_exist('foo-716-0.log',
                'foo-716-0.prof',
                'foo-716-1.log',
                'foo-716-1.prof',
                'foo-716-2.log',
                'foo-716-2.prof')

expect = [
    test.tempdir_re('src', 'script', 'scons.py'),
    'SCONS_LIB_DIR = %s' % test.tempdir_re('src', 'engine'),
]

content = test.read(test.workpath('foo-617-2.log'), mode='r')

def re_find(content, line):
    return re.search(line, content)
test.must_contain_all_lines(content, expect, 'foo-617-2.log', re_find)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
