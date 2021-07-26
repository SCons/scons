#!/usr/bin/env python
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
#

"""
Verify that a failed build action with -j works as expected.
"""

import TestSCons

python = TestSCons.python
test = TestSCons.TestSCons()

try:
    import psutil # noqa: F401
except ImportError:
    test.skip_test("Failed to import psutil required for test, skipping.")

test.dir_fixture('fixture')

# We want to verify that -j 2 starts precisely two jobs, the first of
# which fails and the second of which succeeds, and then stops processing
# due to the first build failure - the second build job does not just
# continue processing tasks.  To try to control the timing, the two
# task scripts will be managed by a server script which regulates the 
# state of the test.
#
# The failure script waits until the server responds that the 
# copy script has, in fact, gotten started. If we don't wait, then SCons 
# could detect our script failure early (typically if a high system load 
# happens to delay SCons' ability to start the next script) and then not 
# start the successful script at all.
#
# The successful script waits until the server responds that the 
# failure script has finished (the server checks that the task pid does not
# exist). If we don't wait for that, then SCons could detect our successful 
# exit first (typically if a high system load happens to delay the failure 
# script) and start another job before it sees the failure from the first 
# script.
#
# Both scripts are set to bail if they had to wait too long for what
# they expected to see.

test.run(arguments='-j 2 .',
        status=2,
        stderr="scons: *** [f3] Error 1\n")

test.must_not_exist(test.workpath('f3'))
test.must_match(test.workpath('f4'), 'f4.in')
test.must_not_exist(test.workpath('f5'))
test.must_not_exist(test.workpath('f6'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
