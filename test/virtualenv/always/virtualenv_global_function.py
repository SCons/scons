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
Check which python executable is running scons and which python executable
would be used by scons, when we run under activated virtualenv (i.e. PATH
contains the virtualenv's bin path).
"""

import TestSCons
import SCons.Platform.virtualenv
import re

test = TestSCons.TestSCons()

test.write('SConstruct', """
print("Virtualenv(): %r" % Virtualenv())
""")

test.run(['-Q'])

s = test.stdout()
m = re.search(r"^Virtualenv\(\):\s*(?P<ve>.+\S)\s*$", s, re.MULTILINE)
if not m:
    test.fail_test(message="""\
can't determine Virtualenv() result from stdout:
========= STDOUT =========
%s
==========================
""" % s)

scons_ve = m.group('ve')
our_ve = "%r" % SCons.Platform.virtualenv.Virtualenv()

# runing in activated virtualenv (after "activate") - PATH includes virtualenv's bin directory
test.fail_test(scons_ve != our_ve,
               message="Virtualenv() from SCons != Virtualenv() from caller script (%r != %r)" % (scons_ve, our_ve))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
