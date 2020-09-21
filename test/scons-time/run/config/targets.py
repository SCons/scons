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
Verify specifying a list of targets through a config file.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import re

import TestSCons_time

test = TestSCons_time.TestSCons_time(match=TestSCons_time.match_re)

test.write_fake_scons_py()

test.write_sample_project('foo.tar.gz')

test.write('config', """\
targets = 'target1 target2'
""")

test.run(arguments = 'run -f config foo.tar.gz')

scons_py = re.escape(test.workpath('scripts', 'scons.py'))
src_engine = re.escape(test.workpath())

prof1 = re.escape(test.workpath('foo-000-1.prof'))
prof2 = re.escape(test.workpath('foo-000-2.prof'))

sep = re.escape(os.sep)

expect = """\
%(scons_py)s
    --debug=count
    --debug=memory
    --debug=time
    --debug=memoizer
    --profile=%(prof1)s
    target1
    target2
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: .*scons-time-.*%(sep)sfoo
""" % locals()

test.must_match('foo-000-1.log', expect, mode='r')

expect = """\
%(scons_py)s
    --debug=count
    --debug=memory
    --debug=time
    --debug=memoizer
    --profile=%(prof2)s
    target1
    target2
SCONS_LIB_DIR = %(src_engine)s
SConstruct file directory: .*scons-time-.*%(sep)sfoo
""" % locals()

test.must_match('foo-000-2.log', expect, mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
