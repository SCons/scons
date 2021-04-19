#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""
Verify that the func -C and --chdir options change directory before
globbing for files.
"""

import re

import TestSCons_time

test = TestSCons_time.TestSCons_time(match = TestSCons_time.match_re)

try:
    import pstats
except ImportError:
    test.skip_test('No pstats module, skipping test.\n')

test.subdir('profs')

input = """\
def _main():
    pass
"""

expect = []
for i in range(9):
    i = str(i)
    test.subdir(i)
    test.profile_data('profs/foo-%s.prof' % i, '%s/prof.py' % i, '_main', input)
    s = r'\d.\d\d\d %s.prof\.py:1\(_main\)' % re.escape(test.workpath(i))
    expect.append(s + '\n')

expect = ''.join(expect)

test.run(arguments = 'func -C profs foo-*.prof', stdout = expect)

test.run(arguments = 'func --chdir profs foo-?.prof', stdout = expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
