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
Test that we can generate Visual Studio 10.0 project (.vcxproj) and
solution (.sln) files that contain SCC information and look correct.
"""

import TestSConsMSVS

for vc_version in TestSConsMSVS.get_tested_proj_file_vc_versions():
    test = TestSConsMSVS.TestSConsMSVS()

    # Make the test infrastructure think we have this version of MSVS installed.
    test._msvs_versions = [vc_version]

    dirs = ['inc1', 'inc2']
    major, minor = test.parse_vc_version(vc_version)
    project_file = 'Test.vcproj' if major <= 9 else 'Test.vcxproj'
    filters_file = project_file + '.filters'
    filters_file_expected = major >= 10
    expected_slnfile = test.get_expected_sln_file_contents(vc_version, project_file)
    expected_vcprojfile = test.get_expected_proj_file_contents(vc_version, dirs, project_file)
    SConscript_contents = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='{vc_version}',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                MSVS_SCC_CONNECTION_ROOT='.',
                MSVS_SCC_PROVIDER='MSSCCI:Perforce SCM',
                MSVS_SCC_PROJECT_NAME='Perforce Project')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = [r'sdk_dir\\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = '{project_file}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
""".format(vc_version=vc_version, project_file=project_file)

    expected_sln_sccinfo = """\
\tGlobalSection(SourceCodeControl) = preSolution
\t\tSccNumberOfProjects = 2
\t\tSccProjectName0 = Perforce\\u0020Project
\t\tSccLocalPath0 = .
\t\tSccProvider0 = MSSCCI:Perforce\\u0020SCM
\t\tCanCheckoutShared = true
\t\tSccProjectUniqueName1 = {project_file}
\t\tSccLocalPath1 = .
\t\tCanCheckoutShared = true
\t\tSccProjectFilePathRelativizedFromConnection1 = .\\\\
\tEndGlobalSection
""".format(project_file=project_file)

    if major < 10:
        # VC8 and VC9 used key-value pair format.
        expected_vcproj_sccinfo = """\
\tSccProjectName="Perforce Project"
\tSccLocalPath="."
\tSccProvider="MSSCCI:Perforce SCM"
"""
    else:
        # VC10 and later use XML format.
        expected_vcproj_sccinfo = """\
\t\t<SccProjectName>Perforce Project</SccProjectName>
\t\t<SccLocalPath>.</SccLocalPath>
\t\t<SccProvider>MSSCCI:Perforce SCM</SccProvider>
"""


    test.write('SConstruct', SConscript_contents)

    test.run(arguments=project_file)

    test.must_exist(test.workpath(project_file))
    vcproj = test.read(project_file, 'r')
    expect = test.msvs_substitute(expected_vcprojfile, vc_version, None, 'SConstruct',
                                  vcproj_sccinfo=expected_vcproj_sccinfo)
    # don't compare the pickled data
    assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

    test.must_exist(test.workpath('Test.sln'))
    sln = test.read('Test.sln', 'r')
    expect = test.msvs_substitute(expected_slnfile, vc_version, None, 'SConstruct',
                                  sln_sccinfo=expected_sln_sccinfo)
    # don't compare the pickled data
    assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)


    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
