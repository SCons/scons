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
solution (.sln) files that look correct.
"""

import os
import os.path
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

expected_slnfile = """\
Microsoft Visual Studio Solution File, Format Version 8.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{SLNGUID}"
\tProjectSection(ProjectDependencies) = postProject
\tEndProjectSection
EndProject
Global
\tGlobalSection(SolutionConfiguration) = preSolution
\t\tConfigName.0 = Release
\tEndGlobalSection
\tGlobalSection(ProjectConfiguration) = postSolution
\t\t{SLNGUID}.Release.ActiveCfg = Release|Win32
\t\t{SLNGUID}.Release.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ExtensibilityGlobals) = postSolution
\tEndGlobalSection
\tGlobalSection(ExtensibilityAddIns) = postSolution
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile = """\
<?xml version="1.0" encoding = "Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="7.10"
\tName="Test"
\tSccProjectName=""
\tSccLocalPath=""
\tKeyword="MakeFileProj">
\t<Platforms>
\t\t<Platform
\t\t\tName="Win32"/>
\t</Platforms>
\t<Configurations>
\t\t<Configuration
\t\t\tName="Release|Win32"
\t\t\tOutputDirectory="<WORKPATH>"
\t\t\tIntermediateDirectory="<WORKPATH>"
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="FALSE">
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct -c <WORKPATH>\Test.exe"
\t\t\t\tRebuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
\t\t\t\tOutput="<WORKPATH>\Test.exe"/>
\t\t</Configuration>
\t</Configurations>
\t<References>
\t</References>
\t<Files>
\t\t<Filter
\t\t\tName=" Source Files"
\t\t\tFilter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
\t\t\t<File
\t\t\t\tRelativePath="test.cpp">
\t\t\t</File>
\t\t</Filter>
\t\t<Filter
\t\t\tName="Header Files"
\t\t\tFilter="h;hpp;hxx;hm;inl">
\t\t\t<File
\t\t\t\tRelativePath="sdk.h">
\t\t\t</File>
\t\t</Filter>
\t\t<Filter
\t\t\tName="Local Headers"
\t\t\tFilter="h;hpp;hxx;hm;inl">
\t\t\t<File
\t\t\t\tRelativePath="test.h">
\t\t\t</File>
\t\t</Filter>
\t\t<Filter
\t\t\tName="Other Files"
\t\t\tFilter="">
\t\t\t<File
\t\t\t\tRelativePath="readme.txt">
\t\t\t</File>
\t\t</Filter>
\t\t<Filter
\t\t\tName="Resource Files"
\t\t\tFilter="r;rc;ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe">
\t\t\t<File
\t\t\t\tRelativePath="test.rc">
\t\t\t</File>
\t\t</Filter>
\t\t<File
\t\t\tRelativePath="<WORKPATH>\SConstruct">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""



test.subdir('work1')

test.write(['work1', 'SConstruct'], """\
env=Environment(MSVS_VERSION = '7.1')

testsrc = ['test.cpp']
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
""")

test.run(chdir='work1', arguments="Test.vcproj")

test.must_exist(test.workpath('work1', 'Test.vcproj'))
vcproj = test.read(['work1', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', 'work1')
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('work1', 'Test.sln'))
sln = test.read(['work1', 'Test.sln'], 'r')
expect = test.msvs_substitute(expected_slnfile, '7.1', 'work1')
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

test.run(chdir='work1', arguments='-c .')

test.must_not_exist(test.workpath('work1', 'Test.vcproj'))
test.must_not_exist(test.workpath('work1', 'Test.sln'))

test.run(chdir='work1', arguments='Test.vcproj')

test.must_exist(test.workpath('work1', 'Test.vcproj'))
test.must_exist(test.workpath('work1', 'Test.sln'))

test.run(chdir='work1', arguments='-c Test.sln')

test.must_not_exist(test.workpath('work1', 'Test.vcproj'))
test.must_not_exist(test.workpath('work1', 'Test.sln'))



# Test that running SCons with $PYTHON_ROOT in the environment
# changes the .vcproj output as expected.
os.environ['PYTHON_ROOT'] = 'xyzzy'

test.run(chdir='work1', arguments='Test.vcproj')

python = os.path.join('$(PYTHON_ROOT)', os.path.split(sys.executable)[1])

test.must_exist(test.workpath('work1', 'Test.vcproj'))
vcproj = test.read(['work1', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', 'work1', python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

os.environ['PYTHON_ROOT'] = ''



test.pass_test()
