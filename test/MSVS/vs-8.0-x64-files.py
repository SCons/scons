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
Test that we can generate Visual Studio 8.0 project (.vcproj) and
solution (.sln) files that look correct.
"""

import os
import string

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['8.0']



expected_slnfile = TestSConsMSVS.expected_slnfile_8_0
expected_vcprojfile = TestSConsMSVS.expected_vcprojfile_8_0
SConscript_contents = TestSConsMSVS.SConscript_contents_8_0

# We didn't create an API for putting parameters like this into
# the common generated and expected files.  Until we do, just patch
# in the values.
expected_slnfile = string.replace(expected_slnfile, 'Win32', 'x64')
expected_vcprojfile = string.replace(expected_vcprojfile, 'Win32', 'x64')
SConscript_contents = string.replace(SConscript_contents, '\'Release\'', '\'Release|x64\'')



test.write('SConstruct', SConscript_contents)

test.run(arguments="Test.vcproj")

test.must_exist(test.workpath('Test.vcproj'))
vcproj = test.read('Test.vcproj', 'r')
expect = test.msvs_substitute(expected_vcprojfile, '8.0', None, 'SConstruct')
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('Test.sln'))
sln = test.read('Test.sln', 'r')
expect = test.msvs_substitute(expected_slnfile, '8.0', None, 'SConstruct')
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

test.run(arguments='-c .')

test.must_not_exist(test.workpath('Test.vcproj'))
test.must_not_exist(test.workpath('Test.sln'))

test.run(arguments='Test.vcproj')

test.must_exist(test.workpath('Test.vcproj'))
test.must_exist(test.workpath('Test.sln'))

test.run(arguments='-c Test.sln')

test.must_not_exist(test.workpath('Test.vcproj'))
test.must_not_exist(test.workpath('Test.sln'))



# Test that running SCons with $PYTHON_ROOT in the environment
# changes the .vcproj output as expected.
os.environ['PYTHON_ROOT'] = 'xyzzy'
python = os.path.join('$(PYTHON_ROOT)', os.path.split(TestSConsMSVS.python)[1])

test.run(arguments='Test.vcproj')

test.must_exist(test.workpath('Test.vcproj'))
vcproj = test.read('Test.vcproj', 'r')
expect = test.msvs_substitute(expected_vcprojfile, '8.0', None, 'SConstruct',
                              python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
