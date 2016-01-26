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
Verify that files marked AlwaysBuild also get put into CHANGED_SOURCES.
Tigris bug 2622
"""

import TestSCons

test = TestSCons.TestSCons()
test.file_fixture('SConstruct_changed_sources_alwaysBuild','SConstruct')
test.file_fixture('changed_sources_main.cpp')
# always works on first run
test.run()

# On second run prior to fix the file hasn't changed and so never
# makes it into CHANGED_SOURCES.
# Compile is triggered because SCons knows it needs to build it.
# This tests that on second run the source file is in the scons
# output.  Also prior to fix the compile would fail because
# it would produce a compile command line lacking a source file.
test.run()
test.must_contain_all_lines(test.stdout(),['changed_sources_main.cpp'])
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
