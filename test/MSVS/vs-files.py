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
Test that we can generate Visual Studio 10.0 or later project (.vcxproj) and
solution (.sln) files that look correct.
"""

import os

import TestSConsMSVS

for vc_version in TestSConsMSVS.get_tested_proj_file_vc_versions():
    test = TestSConsMSVS.TestSConsMSVS()
    host_arch = test.get_vs_host_arch()

    # Make the test infrastructure think we have this version of MSVS installed.
    test._msvs_versions = [vc_version]

    dirs = ['inc1', 'inc2']
    major, minor = test.parse_vc_version(vc_version)
    project_file = 'Test.vcproj' if major <= 9 else 'Test.vcxproj'
    filters_file = project_file + '.filters'
    filters_file_expected = major >= 10
    expected_slnfile = test.get_expected_sln_file_contents(vc_version, project_file)
    expected_vcprojfile = test.get_expected_proj_file_contents(vc_version, dirs, project_file)

    test.write('SConstruct', test.get_expected_sconscript_file_contents(vc_version, project_file))

    test.run(arguments=project_file)

    test.must_exist(test.workpath(project_file))
    if filters_file_expected:
        test.must_exist(test.workpath(filters_file))
    else:
        test.must_not_exist(test.workpath(filters_file))
    vcxproj = test.read(project_file, 'r')
    expect = test.msvs_substitute(expected_vcprojfile, vc_version, None, 'SConstruct')
    # don't compare the pickled data
    assert vcxproj[:len(expect)] == expect, test.diff_substr(expect, vcxproj)

    test.must_exist(test.workpath('Test.sln'))
    sln = test.read('Test.sln', 'r')
    expect = test.msvs_substitute(expected_slnfile, vc_version, None, 'SConstruct')
    # don't compare the pickled data
    assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

    test.run(arguments='-c .')

    test.must_not_exist(test.workpath(project_file))
    test.must_not_exist(test.workpath(filters_file))
    test.must_not_exist(test.workpath('Test.sln'))

    test.run(arguments=project_file)

    test.must_exist(test.workpath(project_file))
    if filters_file_expected:
        test.must_exist(test.workpath(filters_file))
    else:
        test.must_not_exist(test.workpath(filters_file))
    test.must_exist(test.workpath('Test.sln'))

    test.run(arguments='-c Test.sln')

    test.must_not_exist(test.workpath(project_file))
    test.must_not_exist(test.workpath(filters_file))
    test.must_not_exist(test.workpath('Test.sln'))

    # Test that running SCons with $PYTHON_ROOT in the environment
    # changes the .vcxproj output as expected.
    os.environ['PYTHON_ROOT'] = 'xyzzy'
    python = os.path.join('$(PYTHON_ROOT)', os.path.split(TestSConsMSVS.python)[1])

    test.run(arguments=project_file)

    test.must_exist(test.workpath(project_file))
    vcxproj = test.read(project_file, 'r')
    expect = test.msvs_substitute(expected_vcprojfile, vc_version, None, 'SConstruct',
                                  python=python)
    # don't compare the pickled data
    assert vcxproj[:len(expect)] == expect, test.diff_substr(expect, vcxproj)

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
