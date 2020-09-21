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

"""
Verify that the run -v and --verbose options display command output.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import re
import os
import TestSCons_time

_python_ = re.escape('"' + sys.executable + '"')


test = TestSCons_time.TestSCons_time(match=TestSCons_time.match_re,
                                     diff=TestSCons_time.diff_re)

scons_py = re.escape(test.workpath('scripts', 'scons.py'))
src_engine = re.escape(test.workpath())

tmp_scons_time = test.tempdir_re()
tmp_scons_time_foo = test.tempdir_re('foo')


test.write_fake_scons_py()

foo_tar_gz = test.write_sample_project('foo.tar.gz')

expect = """\
%(scons_py)s
    --version
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
""" % locals()

test.run(arguments='run -q foo.tar.gz', stdout=expect)

test.must_exist('foo-000-0.log',
                'foo-000-0.prof',
                'foo-000-1.log',
                'foo-000-1.prof',
                'foo-000-2.log',
                'foo-000-2.prof')

time_re = r'\[\d\d:\d\d:\d\d\]'

scons_flags = '--debug=count --debug=memory --debug=time --debug=memoizer'


expect = """\
scons-time%(time_re)s: cd %(tmp_scons_time)s
scons-time%(time_re)s: tar xzf %(foo_tar_gz)s
scons-time%(time_re)s: cd foo
scons-time%(time_re)s: find \\* -type f | xargs cat > /dev/null
scons-time%(time_re)s: export SCONS_LIB_DIR=%(src_engine)s
scons-time%(time_re)s: %(_python_)s %(scons_py)s --version
%(scons_py)s
    --version
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
scons-time%(time_re)s: %(_python_)s %(scons_py)s %(scons_flags)s --profile=%(prof0)s --help 2>&1 \\| tee %(log0)s
%(scons_py)s
    --debug=count
    --debug=memory
    --debug=time
    --debug=memoizer
    --profile=%(prof0)s
    --help
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
scons-time%(time_re)s: %(_python_)s %(scons_py)s %(scons_flags)s --profile=%(prof1)s  2>&1 \\| tee %(log1)s
%(scons_py)s
    --debug=count
    --debug=memory
    --debug=time
    --debug=memoizer
    --profile=%(prof1)s
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
scons-time%(time_re)s: %(_python_)s %(scons_py)s %(scons_flags)s --profile=%(prof2)s  2>&1 \\| tee %(log2)s
%(scons_py)s
    --debug=count
    --debug=memory
    --debug=time
    --debug=memoizer
    --profile=%(prof2)s
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: %(tmp_scons_time_foo)s
scons-time%(time_re)s: cd .*
"""
if 'PRESERVE' not in os.environ or not os.environ['PRESERVE']:
    expect += """scons-time%(time_re)s: rm -rf %(tmp_scons_time)s
"""

foo_tar_gz = re.escape(foo_tar_gz)

log0 = re.escape(test.workpath('foo-001-0.log'))
log1 = re.escape(test.workpath('foo-001-1.log'))
log2 = re.escape(test.workpath('foo-001-2.log'))

prof0 = re.escape(test.workpath('foo-001-0.prof'))
prof1 = re.escape(test.workpath('foo-001-1.prof'))
prof2 = re.escape(test.workpath('foo-001-2.prof'))

test.run(arguments='run -v foo.tar.gz', stdout=expect % locals())

test.must_exist('foo-001-0.log',
                'foo-001-0.prof',
                'foo-001-1.log',
                'foo-001-1.prof',
                'foo-001-2.log',
                'foo-001-2.prof')

log0 = re.escape(test.workpath('foo-002-0.log'))
log1 = re.escape(test.workpath('foo-002-1.log'))
log2 = re.escape(test.workpath('foo-002-2.log'))

prof0 = re.escape(test.workpath('foo-002-0.prof'))
prof1 = re.escape(test.workpath('foo-002-1.prof'))
prof2 = re.escape(test.workpath('foo-002-2.prof'))

test.run(arguments='run --verbose foo.tar.gz', stdout=expect % locals())


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
