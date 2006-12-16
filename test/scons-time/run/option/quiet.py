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
Verify that the run -q and --quiet options suppress build output.
"""

import re

import TestSCons_time

python = TestSCons_time.python

test = TestSCons_time.TestSCons_time(match = TestSCons_time.match_re)
test.diff_function = TestSCons_time.diff_re


def tempdir_re(*args):
    import os
    import os.path
    import string
    import tempfile

    sep = re.escape(os.sep)
    args = (tempfile.gettempdir(), 'scons-time-',) + args
    x = apply(os.path.join, args)
    x = re.escape(x)
    x = string.replace(x, 'time\\-', 'time\\-[^%s]*' % sep)
    return x

scons_py = re.escape(test.workpath('src', 'script', 'scons.py'))
src_engine = re.escape(test.workpath('src', 'engine'))

tmp_scons_time = tempdir_re()
tmp_scons_time_foo = tempdir_re('foo')


test.write_fake_scons_py()

foo_tar_gz = test.write_sample_project('foo.tar.gz')

expect = """\
%(scons_py)s
    --version
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
""" % locals()

test.run(arguments = 'run -q foo.tar.gz', stdout = expect)

test.must_exist('foo-000-0.log',
                'foo-000-0.prof',
                'foo-000-1.log',
                'foo-000-1.prof',
                'foo-000-2.log',
                'foo-000-2.prof')

scons_py = test.workpath('src/script/scons.py')

src_engine = test.workpath('src/engine')

test.run(arguments = 'run -q foo.tar.gz', stdout = expect)

test.must_exist('foo-001-0.log',
                'foo-001-0.prof',
                'foo-001-1.log',
                'foo-001-1.prof',
                'foo-001-2.log',
                'foo-001-2.prof')

test.run(arguments = 'run --quiet foo.tar.gz', stdout = expect)

test.pass_test()
