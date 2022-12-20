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
Test that the --diskcheck option and SetOption('diskcheck') correctly
control where or not we look for on-disk matches files and directories
that we look up.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('file', "file\n")



test.write('SConstruct', """

if GetOption('diskcheck') == ['match'] or ARGUMENTS.get('setoption_none',0):
    SetOption('diskcheck', 'none')
File('subdir')
""")

test.run(status=2, stderr=None)
test.must_contain_all_lines(test.stderr(), ["found where file expected"])

test.run(arguments='--diskcheck=match', status=2, stderr=None)
test.must_contain_all_lines(test.stderr(), ["found where file expected"])

# Test that setting --diskcheck to none via command line also works.
test.run(arguments='--diskcheck=none')

# Test that SetOption('diskcheck','none') works to override default as well
test.run(arguments='setoption_none=1')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
