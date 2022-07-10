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
Test scons when no MSVCs are present.
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test("Not win32 platform. Skipping test\n")

# test find_vc_pdir_vswhere by removing all other VS's reg keys
test.file_fixture('no_msvc/no_regs_sconstruct.py', 'SConstruct')
test.run(arguments='-Q -s', stdout='')

# test no msvc's
test.file_fixture('no_msvc/no_msvcs_sconstruct.py', 'SConstruct')
test.run(arguments='-Q -s')

if 'MSVC_VERSION=None' not in test.stdout():
    test.fail_test()

# test msvc version number request with no msvc's
test.file_fixture('no_msvc/no_msvcs_sconstruct_version.py', 'SConstruct')
test.run(arguments='-Q -s', status=2, stderr=r"^.*MSVCVersionNotFound.+", match=TestSCons.match_re_dotall)

# test that MSVCVersionNotFound is not raised for default msvc tools
# when a non-msvc tool list is used
test.subdir('site_scons', ['site_scons', 'site_tools'])

test.write(['site_scons', 'site_tools', 'myignoredefaultmsvctool.py'], """
import SCons.Tool
def generate(env):
    env['MYIGNOREDEFAULTMSVCTOOL']='myignoredefaultmsvctool'
def exists(env):
    return 1
""")

test.file_fixture('no_msvc/no_msvcs_sconstruct_tools.py', 'SConstruct')
test.run(arguments='-Q -s')

# test no msvc's and msvc_sdk_version() call
test.file_fixture('no_msvc/no_msvcs_sconstruct_msvc_sdk_versions.py', 'SConstruct')
test.run(arguments='-Q -s')
test.must_contain_all(test.stdout(), 'sdk_version_list=[]')

# test no msvc's and msvc_sdk_version() call
test.file_fixture('no_msvc/no_msvcs_sconstruct_msvc_toolset_versions.py', 'SConstruct')
test.run(arguments='-Q -s')
test.must_contain_all(test.stdout(), 'toolset_version_list=[]')

# test no msvc's and msvc_query_version_toolset() call
test.file_fixture('no_msvc/no_msvcs_sconstruct_msvc_query_toolset_version.py', 'SConstruct')
test.run(arguments='-Q -s')
test.must_contain_all(test.stdout(), 'msvc_version=None, msvc_toolset_version=None')

test.pass_test()

