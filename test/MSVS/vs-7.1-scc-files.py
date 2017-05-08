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
Test that we can generate Visual Studio 7.1 project (.vcproj) and
solution (.sln) files that contain SCC information and look correct.
"""

import os

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['7.1']



expected_slnfile = TestSConsMSVS.expected_slnfile_7_1
expected_vcprojfile = TestSConsMSVS.expected_vcprojfile_7_1
SConscript_contents = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='7.1',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                MSVS_SCC_CONNECTION_ROOT='.',
                MSVS_SCC_PROVIDER='MSSCCI:Perforce SCM',
                MSVS_SCC_PROJECT_NAME='Perforce Project',
                MSVS_SCC_AUX_PATH='AUX')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcproj',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""

expected_sln_sccinfo = """\
\tGlobalSection(SourceCodeControl) = preSolution
\t\tSccNumberOfProjects = 2
\t\tSccProjectName0 = Perforce\\u0020Project
\t\tSccLocalPath0 = .
\t\tSccProvider0 = MSSCCI:Perforce\\u0020SCM
\t\tCanCheckoutShared = true
\t\tSolutionUniqueID = {SLNGUID}
\t\tSccProjectUniqueName1 = Test.vcproj
\t\tSccLocalPath1 = .
\t\tCanCheckoutShared = true
\t\tSccProjectFilePathRelativizedFromConnection1 = .\\\\
\tEndGlobalSection
"""

expected_vcproj_sccinfo = """\
\tSccProjectName="Perforce Project"
\tSccAuxPath="AUX"
\tSccLocalPath="."
\tSccProvider="MSSCCI:Perforce SCM"
"""


test.write('SConstruct', SConscript_contents)

test.run(arguments="Test.vcproj")

test.must_exist(test.workpath('Test.vcproj'))
vcproj = test.read('Test.vcproj', 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', None, 'SConstruct',
                              vcproj_sccinfo=expected_vcproj_sccinfo)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('Test.sln'))
sln = test.read('Test.sln', 'r')
expect = test.msvs_substitute(expected_slnfile, '7.1', None, 'SConstruct',
                              sln_sccinfo=expected_sln_sccinfo)
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
