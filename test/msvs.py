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

import TestSCons
import sys
import re
import os.path
import os
import TestCmd
import time

expected_dspfile = '''\
# Microsoft Developer Studio Project File - Name="Test" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) External Target" 0x0106

CFG=Test - Win32 Release
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "Test.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "Test.mak" CFG="Test - Win32 Release"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "Test - Win32 Release" (based on "Win32 (x86) External Target")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""

!IF  "$(CFG)" == "Test - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "<WORKPATH>"
# PROP BASE Intermediate_Dir "<WORKPATH>"
# PROP BASE Cmd_Line "<PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP BASE Rebuild_Opt "-c && <PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP BASE Target_File "<WORKPATH>\Test.exe"
# PROP BASE Bsc_Name ""
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "<WORKPATH>"
# PROP Intermediate_Dir "<WORKPATH>"
# PROP Cmd_Line "<PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP Rebuild_Opt "-c && <PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP Target_File "<WORKPATH>\Test.exe"
# PROP Bsc_Name ""
# PROP Target_Dir ""

!ENDIF

# Begin Target

# Name "Test - Win32 Release"

!IF  "$(CFG)" == "Test - Win32 Release"

!ENDIF 

# Begin Group " Source Files"

# PROP Default_Filter "cpp;c;cxx;l;y;def;odl;idl;hpj;bat"
# Begin Source File

SOURCE="test.cpp"
# End Source File
# End Group
# Begin Group "Header Files"

# PROP Default_Filter "h;hpp;hxx;hm;inl"
# Begin Source File

SOURCE="sdk.h"
# End Source File
# End Group
# Begin Group "Local Headers"

# PROP Default_Filter "h;hpp;hxx;hm;inl"
# Begin Source File

SOURCE="test.h"
# End Source File
# End Group
# Begin Group "Other Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE="readme.txt"
# End Source File
# End Group
# Begin Group "Resource Files"

# PROP Default_Filter "r;rc;ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe"
# Begin Source File

SOURCE="test.rc"
# End Source File
# End Group
# Begin Source File

SOURCE="<WORKPATH>\SConstruct"
# End Source File
# End Target
# End Project
'''

expected_dswfile = '''\
Microsoft Developer Studio Workspace File, Format Version 6.00
# WARNING: DO NOT EDIT OR DELETE THIS WORKSPACE FILE!

###############################################################################

Project: "Test"="<WORKPATH>\Test.dsp" - Package Owner=<4>

Package=<5>
{{{
}}}

Package=<4>
{{{
}}}

###############################################################################

Global:

Package=<5>
{{{
}}}

Package=<3>
{{{
}}}

###############################################################################
'''

expected_slnfile = '''\
Microsoft Visual Studio Solution File, Format Version 7.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{SLNGUID}"
EndProject
Global
	GlobalSection(SolutionConfiguration) = preSolution
		ConfigName.0 = Release
	EndGlobalSection
	GlobalSection(ProjectDependencies) = postSolution
	EndGlobalSection
	GlobalSection(ProjectConfiguration) = postSolution
		{SLNGUID}.Release.ActiveCfg = Release|Win32
		{SLNGUID}.Release.Build.0 = Release|Win32
	EndGlobalSection
	GlobalSection(ExtensibilityGlobals) = postSolution
	EndGlobalSection
	GlobalSection(ExtensibilityAddIns) = postSolution
	EndGlobalSection
EndGlobal
'''

expected_vcprojfile = '''\
<?xml version="1.0" encoding = "Windows-1252"?>
<VisualStudioProject
	ProjectType="Visual C++"
	Version="7.00"
	Name="Test"
	SccProjectName=""
	SccLocalPath=""
	Keyword="MakeFileProj">
	<Platforms>
		<Platform
			Name="Win32"/>
	</Platforms>
	<Configurations>
		<Configuration
			Name="Release|Win32"
			OutputDirectory="<WORKPATH>"
			IntermediateDirectory="<WORKPATH>"
			ConfigurationType="0"
			UseOfMFC="0"
			ATLMinimizesCRunTimeLibraryUsage="FALSE">
			<Tool
				Name="VCNMakeTool"
				BuildCommandLine="<PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe
"
				CleanCommandLine="<PYTHON> <SCONS> -C <WORKPATH> -f SConstruct -c <WORKPATH>\Test.exe"
				RebuildCommandLine="<PYTHON> <SCONS> -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe
"
				Output="<WORKPATH>\Test.exe"/>
		</Configuration>
	</Configurations>
	<Files>
		<Filter
			Name=" Source Files"
			Filter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
			<File
				RelativePath="test.cpp">
			</File>
		</Filter>
		<Filter
			Name="Header Files"
			Filter="h;hpp;hxx;hm;inl">
			<File
				RelativePath="sdk.h">
			</File>
		</Filter>
		<Filter
			Name="Local Headers"
			Filter="h;hpp;hxx;hm;inl">
			<File
				RelativePath="test.h">
			</File>
		</Filter>
		<Filter
			Name="Other Files"
			Filter="">
			<File
				RelativePath="readme.txt">
			</File>
		</Filter>
		<Filter
			Name="Resource Files"
			Filter="r;rc;ico;cur;bmp;dlg;rc2;rct;bin;cnt;rtf;gif;jpg;jpeg;jpe">
			<File
				RelativePath="test.rc">
			</File>
		</Filter>
		<File
			RelativePath="<WORKPATH>\SConstruct">
		</File>
	</Files>
	<Globals>
	</Globals>
</VisualStudioProject>
'''

test = TestSCons.TestSCons(match = TestCmd.match_re)

if sys.platform != 'win32':
    test.pass_test()

####
# Determine which environments are installed on the test machine.
test.write('SConstruct','''
env = Environment()

f = open('versions','w')
f.write('versions = ' + str(env['MSVS']['VERSIONS']))
f.close()
''')

test.run()
versions = []
execfile(test.workpath('versions'))

#####
# Test v6.0 output

if '6.0' in versions:
    test.write('SConstruct','''
env=Environment(MSVS_VERSION = '6.0')

testsrc = ['test.cpp']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.dsp',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
    ''')

    test.run(arguments="Test.dsp")

    test.fail_test(not os.path.exists(test.workpath('Test.dsp')))
    test.fail_test(not os.path.exists(test.workpath('Test.dsw')))

    # check to see that we got what we expected:
    expected_dspfile = expected_dspfile.replace(r'<WORKPATH>',test.workpath())
    expected_dspfile = expected_dspfile.replace(r'<PYTHON>',sys.executable)
    expected_dspfile = expected_dspfile.replace(r'<SCONS>',os.path.join(os.environ['SCONS_SCRIPT_DIR'],'scons.py'))
    expected_dswfile = expected_dswfile.replace(r'<WORKPATH>',test.workpath())

    f = open(test.workpath('Test.dsp'))
    dsp = f.read()
    f.close()

    # don't compare the pickled data
    assert dsp[:len(expected_dspfile)] == expected_dspfile

    f = open(test.workpath('Test.dsw'))
    dsw = f.read()
    f.close()
    assert dsw == expected_dswfile

    test.run(arguments='-c .')

    test.fail_test(os.path.exists(test.workpath('Test.dsp')))
    test.fail_test(os.path.exists(test.workpath('Test.dsw')))

    test.run(arguments='Test.dsp')

    test.fail_test(not os.path.exists(test.workpath('Test.dsp')))
    test.fail_test(not os.path.exists(test.workpath('Test.dsw')))

    test.run(arguments='-c Test.dsw')

    test.fail_test(os.path.exists(test.workpath('Test.dsp')))
    test.fail_test(os.path.exists(test.workpath('Test.dsw')))

#####
# Test .NET output

if '7.0' in versions:
    test.write('SConstruct','''
env=Environment(MSVS_VERSION = '7.0')

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
    ''')

    test.run(arguments="Test.vcproj")

    test.fail_test(not os.path.exists(test.workpath('Test.vcproj')))
    test.fail_test(not os.path.exists(test.workpath('Test.sln')))

    f = open(test.workpath('Test.vcproj'))
    vcproj = f.read()
    f.close()
    expected_vcprojfile = expected_vcprojfile.replace(r'<WORKPATH>',test.workpath())
    expected_vcprojfile = expected_vcprojfile.replace(r'<PYTHON>',sys.executable)
    expected_vcprojfile = expected_vcprojfile.replace(r'<SCONS>',os.path.join(os.environ['SCONS_SCRIPT_DIR'],'scons.py'))

    # don't compare the pickled data
    assert vcproj[:len(expected_vcprojfile)] == expected_vcprojfile

    f = open(test.workpath('Test.sln'))
    sln = f.read()
    f.close()

    assert sln[:len(expected_slnfile)] == expected_slnfile

    test.run(arguments='-c .')

    test.fail_test(os.path.exists(test.workpath('Test.vcproj')))
    test.fail_test(os.path.exists(test.workpath('Test.sln')))

    test.run(arguments='Test.vcproj')

    test.fail_test(not os.path.exists(test.workpath('Test.vcproj')))
    test.fail_test(not os.path.exists(test.workpath('Test.sln')))

    test.run(arguments='-c Test.sln')

    test.fail_test(os.path.exists(test.workpath('Test.vcproj')))
    test.fail_test(os.path.exists(test.workpath('Test.sln')))

test.pass_test()





