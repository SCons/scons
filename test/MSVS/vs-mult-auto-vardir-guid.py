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
Test two project files (.vcxproj) and three solution (.sln) file.
"""

import TestSConsMSVS

test = None

for vc_version in TestSConsMSVS.get_tested_proj_file_vc_versions():

    for autofilter_projects in (None, False, True):

        test = TestSConsMSVS.TestSConsMSVS()

        # Make the test infrastructure think we have this version of MSVS installed.
        test._msvs_versions = [vc_version]

        dirs = ['inc1', 'inc2']
        major, minor = test.parse_vc_version(vc_version)
        project_ext = '.vcproj' if major <= 9 else '.vcxproj'

        project_file_1 = 'Test_1' + project_ext
        project_file_2 = 'Test_2' + project_ext

        filters_file_1 = project_file_1 + '.filters'
        filters_file_2 = project_file_2 + '.filters'
        filters_file_expected = major >= 10

        solution_file = 'Test.sln'
        solution_file_1 = 'Test_1.sln'
        solution_file_2 = 'Test_2.sln'

        if major >= 10:
            project_guid_1 = "{5A243E49-07F0-54C3-B3FD-1DBDF1BA5C9E}"
            project_guid_2 = "{E20E17C7-251E-5246-8FD1-5D51978A0A5D}"
        else:
            project_guid_1 = "{AB46DD68-8CD8-5832-B784-65B216B94739}"
            project_guid_2 = "{03EB0BC3-DA68-5825-9EBB-D8713304E739}"

        if major >= 10:
            solution_guid_1 = "{5E5E4F5D-3E6A-5958-81C6-D4B8B8C633FA}"
            solution_guid_2 = "{ECBCA12A-191D-54EC-BA78-F14249171130}"
        else:
            solution_guid_1 = "{5E5E4F5D-3E6A-5958-81C6-D4B8B8C633FA}"
            solution_guid_2 = "{ECBCA12A-191D-54EC-BA78-F14249171130}"

        expected_vcprojfile_1 = test.get_expected_projects_proj_file_contents(
            vc_version, dirs, project_file_1, project_guid_1,
        )

        expected_vcprojfile_2 = test.get_expected_projects_proj_file_contents(
            vc_version, dirs, project_file_2, project_guid_2,
        )

        expected_slnfile = test.get_expected_projects_sln_file_contents(
            vc_version,
            project_file_1,
            project_file_2,
            have_solution_project_nodes=True,
            autofilter_solution_project_nodes=autofilter_projects,
        )

        expected_slnfile_1 = test.get_expected_sln_file_contents(
            vc_version,
            project_file_1,
        )

        expected_slnfile_2 = test.get_expected_sln_file_contents(
            vc_version,
            project_file_2,
        )

        SConscript_contents = test.get_expected_projects_sconscript_file_contents(
            vc_version=vc_version,
            project_file_1=project_file_1,
            project_file_2=project_file_2,
            solution_file=solution_file,
            autobuild_solution=1,
            autofilter_projects=autofilter_projects,
            default_guids=True,
        )

        test.subdir('src')

        test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build')
""")

        test.write(['src', 'SConscript'], SConscript_contents)

        if autofilter_projects is None:
            test.run(arguments=".", status=2, stderr=r"^.*scons: [*]{3} An msvs solution file was detected in the MSVSSolution 'projects' argument:.+", match=test.match_re_dotall)
            continue

        test.run(arguments=".")

        test.must_exist(test.workpath('src', project_file_1))
        vcproj = test.read(['src', project_file_1], 'r')
        expect = test.msvs_substitute(expected_vcprojfile_1, vc_version, None, 'SConstruct', project_guid=project_guid_1)
        # don't compare the pickled data
        assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

        test.must_exist(test.workpath('src', project_file_2))
        vcproj = test.read(['src', project_file_2], 'r')
        expect = test.msvs_substitute(expected_vcprojfile_2, vc_version, None, 'SConstruct', project_guid=project_guid_2)
        # don't compare the pickled data
        assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

        test.must_exist(test.workpath('src', solution_file))
        sln = test.read(['src', solution_file], 'r')
        expect = test.msvs_substitute_projects(
            expected_slnfile, subdir='src',
            project_guid_1=project_guid_1, project_guid_2=project_guid_2,
            solution_guid_1=solution_guid_1, solution_guid_2=solution_guid_2,
        )
        # don't compare the pickled data
        assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

        test.must_exist(test.workpath('src', solution_file_1))
        sln = test.read(['src', solution_file_1], 'r')
        expect = test.msvs_substitute(expected_slnfile_1, vc_version, subdir='src', project_guid=project_guid_1)
        # don't compare the pickled data
        assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

        test.must_exist(test.workpath('src', solution_file_2))
        sln = test.read(['src', solution_file_2], 'r')
        expect = test.msvs_substitute(expected_slnfile_2, vc_version, subdir='src', project_guid=project_guid_2)
        # don't compare the pickled data
        assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

        if filters_file_expected:
            test.must_exist(test.workpath('src', filters_file_1))
            test.must_exist(test.workpath('src', filters_file_2))
        else:
            test.must_not_exist(test.workpath('src', filters_file_1))
            test.must_not_exist(test.workpath('src', filters_file_2))

        test.must_match(['build', project_file_1], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('src', project_file_1), mode='r')

        test.must_match(['build', project_file_2], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('src', project_file_2), mode='r')

        test.must_match(['build', solution_file], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', solution_file), mode='r')

        test.must_match(['build', solution_file_1], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', solution_file_1), mode='r')

        test.must_match(['build', solution_file_2], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', solution_file_2), mode='r')

        # TODO: clean tests

if test:
    test.pass_test()
