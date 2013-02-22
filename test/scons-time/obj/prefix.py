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
Verify that the obj -p and --prefix options specify what log files to use.
"""

import os.path

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.subdir('logs')

header = '    pre-read    post-read    pre-build   post-build\n'

line_fmt = '       11010        11020        11030        11040    %s\n'

foo_lines = [ header ]
bar_lines = [ header ]

for i in range(3):
    logfile_name = os.path.join('foo-%s.log' % i)
    test.fake_logfile(logfile_name)
    foo_lines.append(line_fmt % logfile_name)

    logfile_name = os.path.join('bar-%s.log' % i)
    test.fake_logfile(logfile_name)
    bar_lines.append(line_fmt % logfile_name)

foo_expect = ''.join(foo_lines)
bar_expect = ''.join(bar_lines)

test.run(arguments = 'obj -p bar Environment.Base', stdout = bar_expect)

test.run(arguments = 'obj --prefix=foo Environment.Base', stdout = foo_expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
