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
Test that we can generate Visual Studio 8.0 project (.vcproj) and
solution (.sln) files that look correct when using a variant_dir.
"""

import TestSConsMSVS

test = None

for vc_version in TestSConsMSVS.get_tested_proj_file_vc_versions():
    test = TestSConsMSVS.TestSConsMSVS()
    host_arch = test.get_vs_host_arch()

    # Make the test infrastructure think we have this version of MSVS installed.
    test._msvs_versions = [vc_version]

    dirs = ['inc1', 'inc2']
    major, minor = test.parse_vc_version(vc_version)
    project_file = 'Test.vcproj' if major <= 9 else 'Test.vcxproj'
    expected_slnfile = test.get_expected_sln_file_contents(vc_version, project_file)
    expected_vcprojfile = test.get_expected_proj_file_contents(vc_version, dirs, project_file)

    test.subdir('src')

    test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build')
""")

    test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build')
""")

    test.write(['src', 'SConscript'], test.get_expected_sconscript_file_contents(vc_version, project_file))

    test.run(arguments=".")

    vcproj = test.read(['src', project_file], 'r')
    expect = test.msvs_substitute(expected_vcprojfile, vc_version, None, 'SConstruct')
    # don't compare the pickled data
    assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

    test.must_exist(test.workpath('src', 'Test.sln'))
    sln = test.read(['src', 'Test.sln'], 'r')
    expect = test.msvs_substitute(expected_slnfile, '8.0', 'src')
    # don't compare the pickled data
    assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

    test.must_match(['build', project_file], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('src', project_file), mode='r')

    test.must_match(['build', 'Test.sln'], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', 'Test.sln'), mode='r')

if test:
    test.pass_test()
