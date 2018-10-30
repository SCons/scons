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
Verify the run --python option to specify an alternatie Python executable.
"""

import os

import TestSCons_time

_python_ = TestSCons_time._python_

test = TestSCons_time.TestSCons_time()

test.write_sample_project('foo.tar.gz')

my_python_py = test.workpath('my_python.py')

test.write(my_python_py, """\
#!%(_python_)s
import sys
profile = ''
for arg in sys.argv[1:]:
    if arg.startswith('--profile='):
        profile = arg[10:]
        break
sys.stdout.write('my_python.py: %%s\\n' %% profile)
""" % locals())

os.chmod(my_python_py, 0o755)

test.run(arguments = 'run --python %s foo.tar.gz' % my_python_py)

prof0 = test.workpath('foo-000-0.prof')
prof1 = test.workpath('foo-000-1.prof')
prof2 = test.workpath('foo-000-2.prof')

test.must_match('foo-000-0.log', "my_python.py: %s\n" % prof0, mode='r')
test.must_match('foo-000-1.log', "my_python.py: %s\n" % prof1, mode='r')
test.must_match('foo-000-2.log', "my_python.py: %s\n" % prof2, mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
