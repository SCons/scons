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
would be used by scons, when we run under an unactivated virtualenv (i.e. PATH
does not contain virtualenv's bin path). This test is skipped if ran in
a regular environment or in an activated virtualenv.
"""

import TestSCons
import SCons.Platform.virtualenv
import sys
import os
import re

test = TestSCons.TestSCons()

if not SCons.Platform.virtualenv.Virtualenv():
    test.skip_test("No virtualenv detected, skipping\n")

if SCons.Platform.virtualenv.select_paths_in_venv(os.getenv('PATH')):
    test.skip_test("Virtualenv detected and it looks like activated, skipping\n")

test.write('SConstruct', """
import sys
env = DefaultEnvironment(tools=[])
print("sys.executable: %s" % repr(sys.executable))
print("env.WhereIs('python'): %s" % repr(env.WhereIs('python')))
""")

if SCons.Platform.virtualenv.virtualenv_enabled_by_default:
    test.run(['-Q'])
else:
    test.run(['-Q', '--enable-virtualenv'])

s = test.stdout()
m = re.search(r"""^sys\.executable:\s*(?P<py>["']?[^\"']+["']?)\s*$""", s, re.MULTILINE)
if not m:
    test.fail_test(message="""\
can't determine sys.executable from stdout:
========= STDOUT =========
%s
==========================
""" % s)

interpreter = eval(m.group('py'))

m = re.search(r"""^\s*env\.WhereIs\('python'\):\s*(?P<py>["']?[^"']+[\"']?)\s*$""", s, re.MULTILINE)
if not m:
    test.fail_test(message="""
can't determine env.WhereIs('python') from stdout:
========= STDOUT =========
%s
==========================
""" % s)

python = eval(m.group('py'))

# running without activating virtualenv (by just /path/to/virtualenv/bin/python runtest.py ...).
test.fail_test(not SCons.Platform.virtualenv.IsInVirtualenv(interpreter),
               message="sys.executable points outside of virtualenv")
test.fail_test(SCons.Platform.virtualenv.IsInVirtualenv(python),
               message="env.WhereIs('python') points to virtualenv")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
