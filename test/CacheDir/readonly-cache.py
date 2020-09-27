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
Verify accessing cache works even if it's read-only.
"""

import glob
import os
import TestSCons
import time

test = TestSCons.TestSCons()

test.write(['SConstruct'], """\
DefaultEnvironment(tools=[])
CacheDir('cache')
Command('file.out', 'file.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('file.in', "file.in\n")

test.run(arguments = '--debug=explain --cache-debug=- .')

cachefile = glob.glob("cache/??/*")[0]

time0 = os.stat(cachefile).st_mtime

time.sleep(.1)

test.unlink('file.out')

test.run(arguments = '--debug=explain --cache-debug=- .')

time1  = os.stat(cachefile).st_mtime

# make sure that mtime has been updated on cache use
if time1 <= time0:
    test.fail_test()

test.unlink('file.out')

for root, dirs, files in os.walk("cache", topdown=False):
    for file in files:
        os.chmod(os.path.join(root,file), 0o444)
    for dir in dirs:
        os.chmod(os.path.join(root,dir), 0o555)

test.run(arguments = '--debug=explain --cache-debug=- .')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
