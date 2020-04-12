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
Verify that the scons.bat file returns error codes as we expect.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    msg = "Skipping scons.bat test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

python = test.where_is('python')

if not python:
    msg = "Skipping scons.bat test; python is not on %PATH%.\n"
    test.skip_test(msg)

scons_bat = os.path.splitext(test.program)[0] + '.bat'

if not os.path.exists(scons_bat):
    msg = "Skipping scons.bat test; %s does not exist.\n" % scons_bat
    test.skip_test(msg)

test.write('scons.bat', test.read(scons_bat))

# The scons.bat file tries to import SCons.Script from its sys.prefix
# directories first (i.e., site-packages) which means this test might
# end up using an installed SCons in preference to something local.
# If so, create a SConstruct file that will exit with our expected
# error status.  If there is *not* an installed SCons, we still want
# this test to work, so we make a "SCons" package in the local
# directory with a Script.py module that contains a main() function
# that just exits with the expected status.

test.subdir('SCons')

test.write(['SCons', '__init__.py'], "")

test.write(['SCons', 'Script.py'], """\
import sys
def main():
    sys.exit(7)
""")

test.write('SConstruct', """\
import sys
sys.exit(7)
""")

test.run(program = 'scons.bat', status = 7)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
