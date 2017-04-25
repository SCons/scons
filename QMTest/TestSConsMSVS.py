"""
TestSConsMSVS.py:  a testing framework for the SCons software construction
tool.

A TestSConsMSVS environment object is created via the usual invocation:

    test = TestSConsMSVS()

TestSConsMSVS is a subsclass of TestSCons, which is in turn a subclass
of TestCommon, which is in turn is a subclass of TestCmd), and hence
has available all of the methods and attributes from those classes,
as well as any overridden or additional methods or attributes defined
in this subclass.
"""

# __COPYRIGHT__

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import platform
import traceback
from xml.etree import ElementTree

from TestSCons import *
from TestSCons import __all__



expected_dspfile_6_0 = '''\
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
# PROP BASE Output_Dir ""
# PROP BASE Intermediate_Dir ""
# PROP BASE Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct "Test.exe""
# PROP BASE Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct "Test.exe""
# PROP BASE Target_File "Test.exe"
# PROP BASE Bsc_Name ""
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ""
# PROP Intermediate_Dir ""
# PROP Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct "Test.exe""
# PROP Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct "Test.exe""
# PROP Target_File "Test.exe"
# PROP Bsc_Name ""
# PROP Target_Dir ""

!ENDIF

# Begin Target

# Name "Test - Win32 Release"

!IF  "$(CFG)" == "Test - Win32 Release"

!ENDIF 

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
# Begin Group "Source Files"

# PROP Default_Filter "cpp;c;cxx;l;y;def;odl;idl;hpj;bat"
# Begin Source File

SOURCE="test.c"
# End Source File
# End Group
# Begin Source File

SOURCE="<SCONSCRIPT>"
# End Source File
# End Target
# End Project
'''

expected_dswfile_6_0 = '''\
Microsoft Developer Studio Workspace File, Format Version 6.00
# WARNING: DO NOT EDIT OR DELETE THIS WORKSPACE FILE!

###############################################################################

Project: "Test"="Test.dsp" - Package Owner=<4>

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

SConscript_contents_6_0 = """\
env=Environment(platform='win32', tools=['msvs'],
                MSVS_VERSION='6.0',HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test.c']
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
"""



expected_slnfile_7_0 = """\
Microsoft Visual Studio Solution File, Format Version 7.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "<PROJECT_GUID>"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfiguration) = preSolution
\t\tConfigName.0 = Release
\tEndGlobalSection
\tGlobalSection(ProjectDependencies) = postSolution
\tEndGlobalSection
\tGlobalSection(ProjectConfiguration) = postSolution
\t\t<PROJECT_GUID>.Release.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID>.Release.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ExtensibilityGlobals) = postSolution
\tEndGlobalSection
\tGlobalSection(ExtensibilityAddIns) = postSolution
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile_7_0 = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="7.00"
\tName="Test"
\tProjectGUID="<PROJECT_GUID>"
<SCC_VCPROJ_INFO>
\tKeyword="MakeFileProj">
\t<Platforms>
\t\t<Platform
\t\t\tName="Win32"/>
\t</Platforms>
\t<Configurations>
\t\t<Configuration
\t\t\tName="Release|Win32"
\t\t\tOutputDirectory=""
\t\t\tIntermediateDirectory=""
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="FALSE">
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tReBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tOutput="Test.exe"/>
\t\t</Configuration>
\t</Configurations>
\t<Files>
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
\t\t<Filter
\t\t\tName="Source Files"
\t\t\tFilter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
\t\t\t<File
\t\t\t\tRelativePath="test1.cpp">
\t\t\t</File>
\t\t\t<File
\t\t\t\tRelativePath="test2.cpp">
\t\t\t</File>
\t\t</Filter>
\t\t<File
\t\t\tRelativePath="<SCONSCRIPT>">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""

SConscript_contents_7_0 = """\
env=Environment(platform='win32', tools=['msvs'],
                MSVS_VERSION='7.0',HOST_ARCH='%(HOST_ARCH)s')

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



expected_slnfile_7_1 = """\
Microsoft Visual Studio Solution File, Format Version 8.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "<PROJECT_GUID>"
\tProjectSection(ProjectDependencies) = postProject
\tEndProjectSection
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfiguration) = preSolution
\t\tConfigName.0 = Release
\tEndGlobalSection
\tGlobalSection(ProjectDependencies) = postSolution
\tEndGlobalSection
\tGlobalSection(ProjectConfiguration) = postSolution
\t\t<PROJECT_GUID>.Release.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID>.Release.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ExtensibilityGlobals) = postSolution
\tEndGlobalSection
\tGlobalSection(ExtensibilityAddIns) = postSolution
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile_7_1 = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="7.10"
\tName="Test"
\tProjectGUID="<PROJECT_GUID>"
<SCC_VCPROJ_INFO>
\tKeyword="MakeFileProj">
\t<Platforms>
\t\t<Platform
\t\t\tName="Win32"/>
\t</Platforms>
\t<Configurations>
\t\t<Configuration
\t\t\tName="Release|Win32"
\t\t\tOutputDirectory=""
\t\t\tIntermediateDirectory=""
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="FALSE">
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tReBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tOutput="Test.exe"/>
\t\t</Configuration>
\t</Configurations>
\t<References>
\t</References>
\t<Files>
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
\t\t<Filter
\t\t\tName="Source Files"
\t\t\tFilter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
\t\t\t<File
\t\t\t\tRelativePath="test1.cpp">
\t\t\t</File>
\t\t\t<File
\t\t\t\tRelativePath="test2.cpp">
\t\t\t</File>
\t\t</Filter>
\t\t<File
\t\t\tRelativePath="<SCONSCRIPT>">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""

SConscript_contents_7_1 = """\
env=Environment(platform='win32', tools=['msvs'],
                MSVS_VERSION='7.1',HOST_ARCH='%(HOST_ARCH)s')

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



expected_slnfile_8_0 = """\
Microsoft Visual Studio Solution File, Format Version 9.00
# Visual Studio 2005
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "<PROJECT_GUID>"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t<PROJECT_GUID>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID>.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_slnfile_9_0 = """\
Microsoft Visual Studio Solution File, Format Version 10.00
# Visual Studio 2008
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "<PROJECT_GUID>"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t<PROJECT_GUID>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID>.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_slnfile_10_0 = """\
Microsoft Visual Studio Solution File, Format Version 11.00
# Visual Studio 2010
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test.vcxproj", "Test.vcxproj", "{39A97E1F-1A52-8954-A0B1-A10A8487545E}"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.ActiveCfg = Release|Win32
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_slnfile_11_0 = """\
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio 11
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test.vcxproj", "Test.vcxproj", "{39A97E1F-1A52-8954-A0B1-A10A8487545E}"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.ActiveCfg = Release|Win32
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_slnfile_14_0 = """\
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio 14
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test.vcxproj", "Test.vcxproj", "{39A97E1F-1A52-8954-A0B1-A10A8487545E}"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.ActiveCfg = Release|Win32
\t\t{39A97E1F-1A52-8954-A0B1-A10A8487545E}.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile_8_0 = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="8.00"
\tName="Test"
\tProjectGUID="<PROJECT_GUID>"
\tRootNamespace="Test"
<SCC_VCPROJ_INFO>
\tKeyword="MakeFileProj">
\t<Platforms>
\t\t<Platform
\t\t\tName="Win32"/>
\t</Platforms>
\t<ToolFiles>
\t</ToolFiles>
\t<Configurations>
\t\t<Configuration
\t\t\tName="Release|Win32"
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="false"
\t\t\t>
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tReBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tOutput="Test.exe"
\t\t\t\tPreprocessorDefinitions="DEF1;DEF2;DEF3=1234"
\t\t\t\tIncludeSearchPath="inc1;inc2"
\t\t\t\tForcedIncludes=""
\t\t\t\tAssemblySearchPath=""
\t\t\t\tForcedUsingAssemblies=""
\t\t\t\tCompileAsManaged=""
\t\t\t/>
\t\t</Configuration>
\t</Configurations>
\t<References>
\t</References>
\t<Files>
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
\t\t<Filter
\t\t\tName="Source Files"
\t\t\tFilter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
\t\t\t<File
\t\t\t\tRelativePath="test1.cpp">
\t\t\t</File>
\t\t\t<File
\t\t\t\tRelativePath="test2.cpp">
\t\t\t</File>
\t\t</Filter>
\t\t<File
\t\t\tRelativePath="<SCONSCRIPT>">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""

expected_vcprojfile_9_0 = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="9.00"
\tName="Test"
\tProjectGUID="<PROJECT_GUID>"
\tRootNamespace="Test"
<SCC_VCPROJ_INFO>
\tKeyword="MakeFileProj">
\t<Platforms>
\t\t<Platform
\t\t\tName="Win32"/>
\t</Platforms>
\t<ToolFiles>
\t</ToolFiles>
\t<Configurations>
\t\t<Configuration
\t\t\tName="Release|Win32"
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="false"
\t\t\t>
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tReBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tOutput="Test.exe"
\t\t\t\tPreprocessorDefinitions="DEF1;DEF2;DEF3=1234"
\t\t\t\tIncludeSearchPath="inc1;inc2"
\t\t\t\tForcedIncludes=""
\t\t\t\tAssemblySearchPath=""
\t\t\t\tForcedUsingAssemblies=""
\t\t\t\tCompileAsManaged=""
\t\t\t/>
\t\t</Configuration>
\t</Configurations>
\t<References>
\t</References>
\t<Files>
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
\t\t<Filter
\t\t\tName="Source Files"
\t\t\tFilter="cpp;c;cxx;l;y;def;odl;idl;hpj;bat">
\t\t\t<File
\t\t\t\tRelativePath="test1.cpp">
\t\t\t</File>
\t\t\t<File
\t\t\t\tRelativePath="test2.cpp">
\t\t\t</File>
\t\t</Filter>
\t\t<File
\t\t\tRelativePath="<SCONSCRIPT>">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""

expected_vcprojfile_10_0 = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
\t<ItemGroup Label="ProjectConfigurations">
\t\t<ProjectConfiguration Include="Release|Win32">
\t\t\t<Configuration>Release</Configuration>
\t\t\t<Platform>Win32</Platform>
\t\t</ProjectConfiguration>
\t</ItemGroup>
\t<PropertyGroup Label="Globals">
\t\t<ProjectGuid>{39A97E1F-1A52-8954-A0B1-A10A8487545E}</ProjectGuid>
<SCC_VCPROJ_INFO>
\t\t<RootNamespace>Test</RootNamespace>
\t\t<Keyword>MakeFileProj</Keyword>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
\t<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
\t\t<ConfigurationType>Makefile</ConfigurationType>
\t\t<UseOfMfc>false</UseOfMfc>
\t\t<PlatformToolset>v100</PlatformToolset>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />
\t<ImportGroup Label="ExtensionSettings">
\t</ImportGroup>
\t<ImportGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="PropertySheets">
\t\t<Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
\t</ImportGroup>
\t<PropertyGroup Label="UserMacros" />
\t<PropertyGroup>
\t<_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
\t\t<NMakeBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeBuildCommandLine>
\t\t<NMakeReBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeReBuildCommandLine>
\t\t<NMakeCleanCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;</NMakeCleanCommandLine>
\t\t<NMakeOutput Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">Test.exe</NMakeOutput>
\t\t<NMakePreprocessorDefinitions Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">DEF1;DEF2;DEF3=1234</NMakePreprocessorDefinitions>
\t\t<NMakeIncludeSearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">inc1;inc2</NMakeIncludeSearchPath>
\t\t<NMakeForcedIncludes Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedIncludes)</NMakeForcedIncludes>
\t\t<NMakeAssemblySearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeAssemblySearchPath)</NMakeAssemblySearchPath>
\t\t<NMakeForcedUsingAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedUsingAssemblies)</NMakeForcedUsingAssemblies>
\t</PropertyGroup>
\t<ItemGroup>
\t\t<ClInclude Include="sdk_dir\sdk.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClInclude Include="test.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="readme.txt" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="test.rc" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClCompile Include="test1.cpp" />
\t\t<ClCompile Include="test2.cpp" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="SConstruct" />
\t</ItemGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />
\t<ImportGroup Label="ExtensionTargets">
\t</ImportGroup>
</Project>
"""

expected_vcprojfile_11_0 = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
\t<ItemGroup Label="ProjectConfigurations">
\t\t<ProjectConfiguration Include="Release|Win32">
\t\t\t<Configuration>Release</Configuration>
\t\t\t<Platform>Win32</Platform>
\t\t</ProjectConfiguration>
\t</ItemGroup>
\t<PropertyGroup Label="Globals">
\t\t<ProjectGuid>{39A97E1F-1A52-8954-A0B1-A10A8487545E}</ProjectGuid>
<SCC_VCPROJ_INFO>
\t\t<RootNamespace>Test</RootNamespace>
\t\t<Keyword>MakeFileProj</Keyword>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
\t<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
\t\t<ConfigurationType>Makefile</ConfigurationType>
\t\t<UseOfMfc>false</UseOfMfc>
\t\t<PlatformToolset>v110</PlatformToolset>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />
\t<ImportGroup Label="ExtensionSettings">
\t</ImportGroup>
\t<ImportGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="PropertySheets">
\t\t<Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
\t</ImportGroup>
\t<PropertyGroup Label="UserMacros" />
\t<PropertyGroup>
\t<_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
\t\t<NMakeBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeBuildCommandLine>
\t\t<NMakeReBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeReBuildCommandLine>
\t\t<NMakeCleanCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;</NMakeCleanCommandLine>
\t\t<NMakeOutput Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">Test.exe</NMakeOutput>
\t\t<NMakePreprocessorDefinitions Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">DEF1;DEF2;DEF3=1234</NMakePreprocessorDefinitions>
\t\t<NMakeIncludeSearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">inc1;inc2</NMakeIncludeSearchPath>
\t\t<NMakeForcedIncludes Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedIncludes)</NMakeForcedIncludes>
\t\t<NMakeAssemblySearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeAssemblySearchPath)</NMakeAssemblySearchPath>
\t\t<NMakeForcedUsingAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedUsingAssemblies)</NMakeForcedUsingAssemblies>
\t</PropertyGroup>
\t<ItemGroup>
\t\t<ClInclude Include="sdk_dir\sdk.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClInclude Include="test.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="readme.txt" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="test.rc" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClCompile Include="test1.cpp" />
\t\t<ClCompile Include="test2.cpp" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="SConstruct" />
\t</ItemGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />
\t<ImportGroup Label="ExtensionTargets">
\t</ImportGroup>
</Project>
"""

expected_vcprojfile_14_0 = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
\t<ItemGroup Label="ProjectConfigurations">
\t\t<ProjectConfiguration Include="Release|Win32">
\t\t\t<Configuration>Release</Configuration>
\t\t\t<Platform>Win32</Platform>
\t\t</ProjectConfiguration>
\t</ItemGroup>
\t<PropertyGroup Label="Globals">
\t\t<ProjectGuid>{39A97E1F-1A52-8954-A0B1-A10A8487545E}</ProjectGuid>
<SCC_VCPROJ_INFO>
\t\t<RootNamespace>Test</RootNamespace>
\t\t<Keyword>MakeFileProj</Keyword>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
\t<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
\t\t<ConfigurationType>Makefile</ConfigurationType>
\t\t<UseOfMfc>false</UseOfMfc>
\t\t<PlatformToolset>v140</PlatformToolset>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />
\t<ImportGroup Label="ExtensionSettings">
\t</ImportGroup>
\t<ImportGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="PropertySheets">
\t\t<Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
\t</ImportGroup>
\t<PropertyGroup Label="UserMacros" />
\t<PropertyGroup>
\t<_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
\t\t<NMakeBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeBuildCommandLine>
\t\t<NMakeReBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;</NMakeReBuildCommandLine>
\t\t<NMakeCleanCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;</NMakeCleanCommandLine>
\t\t<NMakeOutput Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">Test.exe</NMakeOutput>
\t\t<NMakePreprocessorDefinitions Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">DEF1;DEF2;DEF3=1234</NMakePreprocessorDefinitions>
\t\t<NMakeIncludeSearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">inc1;inc2</NMakeIncludeSearchPath>
\t\t<NMakeForcedIncludes Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedIncludes)</NMakeForcedIncludes>
\t\t<NMakeAssemblySearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeAssemblySearchPath)</NMakeAssemblySearchPath>
\t\t<NMakeForcedUsingAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedUsingAssemblies)</NMakeForcedUsingAssemblies>
\t</PropertyGroup>
\t<ItemGroup>
\t\t<ClInclude Include="sdk_dir\sdk.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClInclude Include="test.h" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="readme.txt" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="test.rc" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<ClCompile Include="test1.cpp" />
\t\t<ClCompile Include="test2.cpp" />
\t</ItemGroup>
\t<ItemGroup>
\t\t<None Include="SConstruct" />
\t</ItemGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />
\t<ImportGroup Label="ExtensionTargets">
\t</ImportGroup>
</Project>
"""

SConscript_contents_8_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='8.0',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

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

SConscript_contents_9_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='9.0',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

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

SConscript_contents_10_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='10.0',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk_dir\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcxproj',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""

SConscript_contents_11_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='11.0',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk_dir\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcxproj',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""

SConscript_contents_14_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='14.0',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk_dir\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcxproj',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""

class TestSConsMSVS(TestSCons):
    """Subclass for testing MSVS-specific portions of SCons."""

    def msvs_versions(self):
        if not hasattr(self, '_msvs_versions'):

            # Determine the SCons version and the versions of the MSVS
            # environments installed on the test machine.
            #
            # We do this by executing SCons with an SConstruct file
            # (piped on stdin) that spits out Python assignments that
            # we can just exec().  We construct the SCons.__"version"__
            # string in the input here so that the SCons build itself
            # doesn't fill it in when packaging SCons.
            input = """\
import SCons
import SCons.Tool.MSCommon
print("self.scons_version =", repr(SCons.__%s__))
print("self._msvs_versions =", str(SCons.Tool.MSCommon.query_versions()))
""" % 'version'
        
            self.run(arguments = '-n -q -Q -f -', stdin = input)
            exec(self.stdout())

        return self._msvs_versions

    def vcproj_sys_path(self, fname):
        """
        """
        orig = 'sys.path = [ join(sys'

        enginepath = repr(os.path.join(self._cwd, '..', 'engine'))
        replace = 'sys.path = [ %s, join(sys' % enginepath

        contents = self.read(fname)
        contents = contents.replace(orig, replace)
        self.write(fname, contents)

    def msvs_substitute(self, input, msvs_ver,
                        subdir=None, sconscript=None,
                        python=None,
                        project_guid=None,
                        vcproj_sccinfo='', sln_sccinfo=''):
        if not hasattr(self, '_msvs_versions'):
            self.msvs_versions()

        if subdir:
            workpath = self.workpath(subdir)
        else:
            workpath = self.workpath()

        if sconscript is None:
            sconscript = self.workpath('SConstruct')

        if python is None:
            python = sys.executable

        if project_guid is None:
            project_guid = "{E5466E26-0003-F18B-8F8A-BCD76C86388D}"

        if 'SCONS_LIB_DIR' in os.environ:
            exec_script_main = "from os.path import join; import sys; sys.path = [ r'%s' ] + sys.path; import SCons.Script; SCons.Script.main()" % os.environ['SCONS_LIB_DIR']
        else:
            exec_script_main = "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-%s'), join(sys.prefix, 'scons-%s'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()" % (self.scons_version, self.scons_version)
        exec_script_main_xml = exec_script_main.replace("'", "&apos;")

        result = input.replace(r'<WORKPATH>', workpath)
        result = result.replace(r'<PYTHON>', python)
        result = result.replace(r'<SCONSCRIPT>', sconscript)
        result = result.replace(r'<SCONS_SCRIPT_MAIN>', exec_script_main)
        result = result.replace(r'<SCONS_SCRIPT_MAIN_XML>', exec_script_main_xml)
        result = result.replace(r'<PROJECT_GUID>', project_guid)
        result = result.replace('<SCC_VCPROJ_INFO>\n', vcproj_sccinfo)
        result = result.replace('<SCC_SLN_INFO>\n', sln_sccinfo)
        return result

    def get_msvs_executable(self, version):
        """Returns a full path to the executable (MSDEV or devenv)
        for the specified version of Visual Studio.
        """
        from SCons.Tool.MSCommon import get_vs_by_version

        msvs = get_vs_by_version(version)
        if not msvs:
            return None
        return msvs.get_executable()

    def run(self, *args, **kw):
        """
        Suppress MSVS deprecation warnings.
        """
        save_sconsflags = os.environ.get('SCONSFLAGS')
        if save_sconsflags:
            sconsflags = [save_sconsflags]
        else:
            sconsflags = []
        sconsflags = sconsflags + ['--warn=no-deprecated']
        os.environ['SCONSFLAGS'] = ' '.join(sconsflags)
        try:
            result = TestSCons.run(self, *args, **kw)
        finally:
            os.environ['SCONSFLAGS'] = save_sconsflags or ''
        return result
    
    def get_vs_host_arch(self):
        """ Get an MSVS, SDK , and/or MSVS acceptable platform arch
        """
        
        # Dict to 'canonalize' the arch
        _ARCH_TO_CANONICAL = {
            "x86": "x86",
            "amd64": "amd64",
            "i386": "x86",
            "emt64": "amd64",
            "x86_64": "amd64",
            "itanium": "ia64",
            "ia64": "ia64",
        }

        host_platform = platform.machine()
        # TODO(2.5):  the native Python platform.machine() function returns
        # '' on all Python versions before 2.6, after which it also uses
        # PROCESSOR_ARCHITECTURE.
        if not host_platform:
            host_platform = os.environ.get('PROCESSOR_ARCHITECTURE', '')
                
            
        try:
            host = _ARCH_TO_CANONICAL[host_platform]
        except KeyError as e:
            # Default to x86 for all other platforms
            host = 'x86'
    
   
        return host

    def validate_msvs_file(self,  file):
        try:
            x = ElementTree.parse(file)
        except: 
            print("--------------------------------------------------------------")
            print("--------------------------------------------------------------")
            print(traceback.format_exc())
            print("Failed to validate xml in MSVS file: ")
            print(file)
            print("--------------------------------------------------------------")
            print("--------------------------------------------------------------")
            self.fail_test()
# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
