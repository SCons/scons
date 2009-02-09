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
Verify specifying a list of archives through the archive_list setting
in a config file.
"""

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.write_fake_scons_py()

test.write_sample_project('foo.tar.gz')

test.write('config', """\
archive_list = ['foo.tar.gz', 'foo-file']
""")

test.write('foo-file', "foo-file\n")

test.run(arguments = 'run -f config')

test.must_exist('foo-000-0.log',
                'foo-000-0.prof',
                'foo-000-1.log',
                'foo-000-1.prof',
                'foo-000-2.log',
                'foo-000-2.prof')

test.must_exist('foo-file')


test.write_sample_project('bar.tar.gz')

test.run(arguments = 'run -f config bar.tar.gz')

test.must_not_exist('foo-001-0.log',
                    'foo-001-0.prof',
                    'foo-001-1.log',
                    'foo-001-1.prof',
                    'foo-001-2.log',
                    'foo-001-2.prof')

test.must_exist('bar-000-0.log',
                'bar-000-0.prof',
                'bar-000-1.log',
                'bar-000-1.prof',
                'bar-000-2.log',
                'bar-000-2.prof')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
