#!/usr/bin/env python
#
# MIT Licenxe
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
Test that the $INSTALLSTR variable is displayed when we install a file.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('install')

# Check that spaces aren't stripped in INSTALLSTR  by using
# extra whitespace in the string (issue 2018)
test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(tools=[], INSTALLSTR='INSTALL  $SOURCE => $TARGET!')
env.Install('install', 'file')
""")

test.write('file', "file\n")

test.run(stdout=test.wrap_stdout("""\
INSTALL  file => %s!
""") % os.path.join('install', 'file'))

test.must_match(['install', 'file'], "file\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
