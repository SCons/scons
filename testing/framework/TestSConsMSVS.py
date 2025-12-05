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
A testing framework for the SCons software construction tool.

A TestSConsMSVS environment object is created via the usual invocation:

    test = TestSConsMSVS()

TestSConsMSVS is a subsclass of TestSCons, which is in turn a subclass
of TestCommon, which is in turn is a subclass of TestCmd), and hence
has available all of the methods and attributes from those classes,
as well as any overridden or additional methods or attributes defined
in this subclass.
"""

import os
import sys
import platform
import traceback
from xml.etree import ElementTree

try:
    import winreg
except ImportError:
    winreg = None

import SCons.Errors
from TestSCons import *
from TestSCons import __all__


PROJECT_GUID = "{00000000-0000-0000-0000-000000000000}"
PROJECT_GUID_1 = "{11111111-1111-1111-1111-111111111111}"
PROJECT_GUID_2 = "{22222222-2222-2222-2222-222222222222}"

SOLUTION_GUID_1 = "{88888888-8888-8888-8888-888888888888}"
SOLUTION_GUID_2 = "{99999999-9999-9999-9999-999999999999}"

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
env=Environment(tools=['msvs'],
                MSVS_VERSION='6.0',
                HOST_ARCH='%(HOST_ARCH)s')

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
env=Environment(tools=['msvs'],
                MSVS_VERSION='7.0',
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcproj',
                MSVS_PROJECT_GUID = '%(PROJECT_GUID)s',
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
env=Environment(tools=['msvs'],
                MSVS_VERSION='7.1',
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = 'Test.vcproj',
                MSVS_PROJECT_GUID = '%(PROJECT_GUID)s',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""


expected_slnfile_fmt = """\
Microsoft Visual Studio Solution File, Format Version %(FORMAT_VERSION)s
# Visual Studio %(VS_NUMBER)s
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(PROJECT_NAME)s", "%(PROJECT_FILE)s", "<PROJECT_GUID>"
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

expected_vcprojfile_fmt = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="%(TOOLS_VERSION)s"
\tName="%(PROJECT_BASENAME)s"
\tProjectGUID="<PROJECT_GUID>"
\tRootNamespace="%(PROJECT_BASENAME)s"
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
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;%(PROJECT_BASENAME)s.exe&quot;"
\t\t\t\tReBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;%(PROJECT_BASENAME)s.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;%(PROJECT_BASENAME)s.exe&quot;"
\t\t\t\tOutput="%(PROJECT_BASENAME)s.exe"
\t\t\t\tPreprocessorDefinitions="DEF1;DEF2;DEF3=1234"
\t\t\t\tIncludeSearchPath="%(INCLUDE_DIRS)s"
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
\t\t\t\tRelativePath="sdk_dir\\sdk.h">
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

expected_vcxprojfile_fmt = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="%(TOOLS_VERSION)s" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
\t<ItemGroup Label="ProjectConfigurations">
\t\t<ProjectConfiguration Include="Release|Win32">
\t\t\t<Configuration>Release</Configuration>
\t\t\t<Platform>Win32</Platform>
\t\t</ProjectConfiguration>
\t</ItemGroup>
\t<PropertyGroup Label="Globals">
\t\t<ProjectGuid>%(PROJECT_GUID)s</ProjectGuid>
<SCC_VCPROJ_INFO>
\t\t<RootNamespace>%(PROJECT_BASENAME)s</RootNamespace>
\t\t<Keyword>MakeFileProj</Keyword>
\t\t<VCProjectUpgraderObjectName>NoUpgrade</VCProjectUpgraderObjectName>
\t</PropertyGroup>
\t<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />
\t<PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
\t\t<ConfigurationType>Makefile</ConfigurationType>
\t\t<UseOfMfc>false</UseOfMfc>
\t\t<PlatformToolset>%(PLATFORM_TOOLSET)s</PlatformToolset>
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
\t\t<NMakeBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;%(PROJECT_BASENAME)s.exe&quot;</NMakeBuildCommandLine>
\t\t<NMakeReBuildCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;%(PROJECT_BASENAME)s.exe&quot;</NMakeReBuildCommandLine>
\t\t<NMakeCleanCommandLine Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;%(PROJECT_BASENAME)s.exe&quot;</NMakeCleanCommandLine>
\t\t<NMakeOutput Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">%(PROJECT_BASENAME)s.exe</NMakeOutput>
\t\t<NMakePreprocessorDefinitions Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">DEF1;DEF2;DEF3=1234</NMakePreprocessorDefinitions>
\t\t<NMakeIncludeSearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">%(INCLUDE_DIRS)s</NMakeIncludeSearchPath>
\t\t<NMakeForcedIncludes Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedIncludes)</NMakeForcedIncludes>
\t\t<NMakeAssemblySearchPath Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeAssemblySearchPath)</NMakeAssemblySearchPath>
\t\t<NMakeForcedUsingAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">$(NMakeForcedUsingAssemblies)</NMakeForcedUsingAssemblies>
\t\t<AdditionalOptions Condition="'$(Configuration)|$(Platform)'=='Release|Win32'"></AdditionalOptions>
\t</PropertyGroup>
\t<ItemGroup>
\t\t<ClInclude Include="sdk_dir\\sdk.h" />
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

SConscript_contents_fmt = """\
env=Environment(tools=['msvs'],
                MSVS_VERSION='%(MSVS_VERSION)s',
                CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
                CPPPATH=['inc1', 'inc2'],
                HOST_ARCH='%(HOST_ARCH)s')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = [r'sdk_dir\\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

env.MSVSProject(target = '%(PROJECT_FILE)s',
                MSVS_PROJECT_GUID = '%(PROJECT_GUID)s',
                slnguid = '{SLNGUID}',
                srcs = testsrc,
                incs = testincs,
                localincs = testlocalincs,
                resources = testresources,
                misc = testmisc,
                buildtarget = 'Test.exe',
                variant = 'Release')
"""

expected_projects_slnfile_fmt = """\
Microsoft Visual Studio Solution File, Format Version %(FORMAT_VERSION)s
# Visual Studio %(VS_NUMBER)s
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(PROJECT_NAME_1)s", "%(PROJECT_FILE_1)s", "<PROJECT_GUID_1>"
EndProject
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(PROJECT_NAME_2)s", "%(PROJECT_FILE_2)s", "<PROJECT_GUID_2>"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t<PROJECT_GUID_1>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID_1>.Release|Win32.Build.0 = Release|Win32
\t\t<PROJECT_GUID_2>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID_2>.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

expected_projects_slnfile_fmt_slnnodes = """\
Microsoft Visual Studio Solution File, Format Version %(FORMAT_VERSION)s
# Visual Studio %(VS_NUMBER)s
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(PROJECT_NAME_1)s", "%(PROJECT_FILE_1)s", "<PROJECT_GUID_1>"
EndProject
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(SOLUTION_FILE_1)s", "%(SOLUTION_FILE_1)s", "<SOLUTION_GUID_1>"
EndProject
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(PROJECT_NAME_2)s", "%(PROJECT_FILE_2)s", "<PROJECT_GUID_2>"
EndProject
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%(SOLUTION_FILE_2)s", "%(SOLUTION_FILE_2)s", "<SOLUTION_GUID_2>"
EndProject
Global
<SCC_SLN_INFO>
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t<PROJECT_GUID_1>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID_1>.Release|Win32.Build.0 = Release|Win32
\t\t<SOLUTION_GUID_1>.Release|Win32.ActiveCfg = Release|Win32
\t\t<SOLUTION_GUID_1>.Release|Win32.Build.0 = Release|Win32
\t\t<PROJECT_GUID_2>.Release|Win32.ActiveCfg = Release|Win32
\t\t<PROJECT_GUID_2>.Release|Win32.Build.0 = Release|Win32
\t\t<SOLUTION_GUID_2>.Release|Win32.ActiveCfg = Release|Win32
\t\t<SOLUTION_GUID_2>.Release|Win32.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(SolutionProperties) = preSolution
\t\tHideSolutionNode = FALSE
\tEndGlobalSection
EndGlobal
"""

SConscript_projects_contents_fmt = """\
env=Environment(
    tools=['msvs'],
    MSVS_VERSION='%(MSVS_VERSION)s',
    CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
    CPPPATH=['inc1', 'inc2'],
    HOST_ARCH='%(HOST_ARCH)s',
)

testsrc = ['test1.cpp', 'test2.cpp']
testincs = [r'sdk_dir\\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

p1 = env.MSVSProject(
    target = '%(PROJECT_FILE_1)s',
    MSVS_PROJECT_GUID = '%(PROJECT_GUID_1)s',
    slnguid = '{SLNGUID}',
    srcs = testsrc,
    incs = testincs,
    localincs = testlocalincs,
    resources = testresources,
    misc = testmisc,
    buildtarget = 'Test_1.exe',
    variant = 'Release',
    auto_build_solution = %(AUTOBUILD_SOLUTION)s,
)

p2 = env.MSVSProject(
    target = '%(PROJECT_FILE_2)s',
    MSVS_PROJECT_GUID = '%(PROJECT_GUID_2)s',
    slnguid = '{SLNGUID}',
    srcs = testsrc,
    incs = testincs,
    localincs = testlocalincs,
    resources = testresources,
    misc = testmisc,
    buildtarget = 'Test_2.exe',
    variant = 'Release',
    auto_build_solution = %(AUTOBUILD_SOLUTION)s,
)

env.MSVSSolution(
    target = '%(SOLUTION_FILE)s',
    projects = [p1, p2],
    variant = 'Release',
    auto_filter_projects = %(AUTOFILTER_PROJECTS)s,
)
"""

SConscript_projects_defaultguids_contents_fmt = """\
env=Environment(
    tools=['msvs'],
    MSVS_VERSION='%(MSVS_VERSION)s',
    CPPDEFINES=['DEF1', 'DEF2',('DEF3','1234')],
    CPPPATH=['inc1', 'inc2'],
    HOST_ARCH='%(HOST_ARCH)s',
)

testsrc = ['test1.cpp', 'test2.cpp']
testincs = [r'sdk_dir\\sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

p1 = env.MSVSProject(
    target = '%(PROJECT_FILE_1)s',
    slnguid = '{SLNGUID}',
    srcs = testsrc,
    incs = testincs,
    localincs = testlocalincs,
    resources = testresources,
    misc = testmisc,
    buildtarget = 'Test_1.exe',
    variant = 'Release',
    auto_build_solution = %(AUTOBUILD_SOLUTION)s,
)

p2 = env.MSVSProject(
    target = '%(PROJECT_FILE_2)s',
    slnguid = '{SLNGUID}',
    srcs = testsrc,
    incs = testincs,
    localincs = testlocalincs,
    resources = testresources,
    misc = testmisc,
    buildtarget = 'Test_2.exe',
    variant = 'Release',
    auto_build_solution = %(AUTOBUILD_SOLUTION)s,
)

env.MSVSSolution(
    target = '%(SOLUTION_FILE)s',
    projects = [p1, p2],
    variant = 'Release',
    auto_filter_projects = %(AUTOFILTER_PROJECTS)s,
)
"""


def get_tested_proj_file_vc_versions():
    """
    Returns all MSVC versions that we want to test project file creation for.
    """
    return ['8.0', '9.0', '10.0', '11.0', '12.0', '14.0', '14.1', '14.2', '14.3']


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
            input = (
                """\
import SCons
import SCons.Tool.MSCommon
print("self.scons_version =%%s"%%repr(SCons.__%s__))
print("self._msvs_versions =%%s"%%str(SCons.Tool.MSCommon.query_versions(env=None)))
"""
                % 'version'
            )

            self.run(arguments='-n -q -Q -f -', stdin=input)
            exec(self.stdout())

        return self._msvs_versions

    def vcproj_sys_path(self, fname) -> None:
        """ """
        orig = 'sys.path = [ join(sys'

        enginepath = repr(os.path.join(self._cwd, '..', 'engine'))
        replace = f'sys.path = [ {enginepath}, join(sys'

        contents = self.read(fname, mode='r')
        contents = contents.replace(orig, replace)
        self.write(fname, contents)

    def msvs_substitute(
        self,
        input,
        msvs_ver,
        subdir=None,
        sconscript=None,
        python=None,
        project_guid=None,
        vcproj_sccinfo: str = '',
        sln_sccinfo: str = '',
    ):
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
            project_guid = PROJECT_GUID

        if 'SCONS_LIB_DIR' in os.environ:
            exec_script_main = f"from os.path import join; import sys; sys.path = [ r'{os.environ['SCONS_LIB_DIR']}' ] + sys.path; import SCons.Script; SCons.Script.main()"
        else:
            exec_script_main = f"from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-{self.scons_version}'), join(sys.prefix, 'scons-{self.scons_version}'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()"
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

    def get_msvs_executable(self, version, env=None):
        """Returns a full path to the executable (MSDEV or devenv)
        for the specified version of Visual Studio.
        """
        from SCons.Tool.MSCommon import get_vs_by_version

        msvs = get_vs_by_version(version, env)
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
        """Returns an MSVS, SDK, and/or MSVS acceptable platform arch."""

        # Dict to 'canonicalize' the arch (synchronize with MSCommon\vc.py)
        _ARCH_TO_CANONICAL = {
            "amd64": "amd64",
            "emt64": "amd64",
            "i386": "x86",
            "i486": "x86",
            "i586": "x86",
            "i686": "x86",
            "ia64": "ia64",  # deprecated
            "itanium": "ia64",  # deprecated
            "x86": "x86",
            "x86_64": "amd64",
            "arm": "arm",
            "arm64": "arm64",
            "aarch64": "arm64",
        }

        host_platform = None

        if winreg:
            try:
                winkey = winreg.OpenKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                )
                host_platform, _ = winreg.QueryValueEx(winkey, 'PROCESSOR_ARCHITECTURE')
            except OSError:
                pass

        if not host_platform:
            host_platform = platform.machine()

        try:
            host = _ARCH_TO_CANONICAL[host_platform.lower()]
        except KeyError as e:
            # Default to x86 for all other platforms
            host = 'x86'

        return host

    def validate_msvs_file(self, file) -> None:
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

    def parse_vc_version(self, vc_version):
        """
        Parses the string vc_version to determine the major and minor version
        included.
        """
        components = vc_version.split('.')
        major = int(components[0])
        minor = 0 if len(components) < 2 else int(components[1])
        return major, minor

    def _get_solution_file_format_version(self, vc_version) -> str:
        """
        Returns the Visual Studio format version expected in the .sln file.
        """
        major, _ = self.parse_vc_version(vc_version)
        if major == 8:
            return '9.00'
        elif major == 9:
            return '10.00'
        elif major == 10:
            return '11.00'
        elif major > 10:
            return '12.00'
        else:
            raise SCons.Errors.UserError(f'Received unexpected VC version {vc_version}')

    def _get_solution_file_vs_number(self, vc_version) -> str:
        """
        Returns the Visual Studio number expected in the .sln file.
        """
        major, minor = self.parse_vc_version(vc_version)
        if major == 8:
            return '2005'
        elif major == 9:
            return '2008'
        if major == 10:
            return '2010'
        elif major == 11:
            return '11'
        elif major == 12:
            return '14'
        elif major == 14 and (minor == 0 or minor == 1):
            # Visual Studio 2015 and 2017 both use 15 in this entry.
            return '15'
        elif major == 14 and minor == 2:
            return '16'
        elif major == 14 and minor == 3:
            return '17'
        elif major == 14 and minor == 5:
            return '18'
        else:
            raise SCons.Errors.UserError(f'Received unexpected VC version {vc_version}')

    def _get_vcxproj_file_tools_version(self, vc_version) -> str:
        """
        Returns the version entry expected in the project file.
        For .vcxproj files, this goes is ToolsVersion.
        For .vcproj files, this goes in Version.
        """
        major, minor = self.parse_vc_version(vc_version)
        if major == 8:
            # Version="8.00"
            return '8.00'
        elif major == 9:
            # Version="9.00"
            return '9.00'
        elif major < 14:
            # ToolsVersion='4.0'
            return '4.0'
        elif major == 14 and minor == 0:
            # ToolsVersion='14.0'
            return '14.0'
        elif major == 14 and minor == 1:
            # ToolsVersion='15.0'
            return '15.0'
        elif vc_version == '14.2':
            # ToolsVersion='16'
            return '16.0'
        elif vc_version == '14.3':
            # ToolsVersion='17'
            return '17.0'
        elif vc_version == '14.5':
            # ToolsVersion='18'
            return '18.0'
        else:
            raise SCons.Errors.UserError(f'Received unexpected VC version {vc_version}')

    def _get_vcxproj_file_platform_toolset(self, vc_version) -> str:
        """
        Returns the version entry expected in the project file.
        For .vcxproj files, this goes is PlatformToolset.
        For .vcproj files, not applicable.
        """
        major, minor = self.parse_vc_version(vc_version)
        return f"v{major}{minor}"

    def _get_vcxproj_file_cpp_path(self, dirs):
        """Returns the include paths expected in the .vcxproj file"""
        return ';'.join([self.workpath(dir) for dir in dirs])

    def get_expected_sln_file_contents(self, vc_version, project_file):
        """
        Returns the expected .sln file contents.
        Currently this function only supports the newer VC versions that use
        the .vcxproj file format.
        """
        return expected_slnfile_fmt % {
            'FORMAT_VERSION': self._get_solution_file_format_version(vc_version),
            'VS_NUMBER': self._get_solution_file_vs_number(vc_version),
            'PROJECT_NAME': project_file.split('.')[0],
            'PROJECT_FILE': project_file,
        }

    def get_expected_proj_file_contents(self, vc_version, dirs, project_file):
        """Returns the expected .vcxproj file contents"""
        if project_file.endswith('.vcxproj'):
            fmt = expected_vcxprojfile_fmt
        else:
            fmt = expected_vcprojfile_fmt
        project_filename = os.path.split(project_file)[-1]
        project_basename = os.path.splitext(project_filename)[0]
        return fmt % {
            'PROJECT_BASENAME': project_basename,
            'PROJECT_GUID': PROJECT_GUID,
            'TOOLS_VERSION': self._get_vcxproj_file_tools_version(vc_version),
            'INCLUDE_DIRS': self._get_vcxproj_file_cpp_path(dirs),
            'PLATFORM_TOOLSET': self._get_vcxproj_file_platform_toolset(vc_version),
        }

    def get_expected_sconscript_file_contents(self, vc_version, project_file):
        return SConscript_contents_fmt % {
            'HOST_ARCH': self.get_vs_host_arch(),
            'MSVS_VERSION': vc_version,
            'PROJECT_GUID': PROJECT_GUID,
            'PROJECT_FILE': project_file,
        }

    def msvs_substitute_projects(
        self,
        input,
        *,
        subdir=None,
        sconscript=None,
        python=None,
        project_guid_1=None,
        project_guid_2=None,
        solution_guid_1=None,
        solution_guid_2=None,
        vcproj_sccinfo: str = '',
        sln_sccinfo: str = '',
    ):
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

        if project_guid_1 is None:
            project_guid_1 = PROJECT_GUID_1

        if project_guid_2 is None:
            project_guid_2 = PROJECT_GUID_2

        if solution_guid_1 is None:
            solution_guid_1 = SOLUTION_GUID_1

        if solution_guid_2 is None:
            solution_guid_2 = SOLUTION_GUID_2

        if 'SCONS_LIB_DIR' in os.environ:
            exec_script_main = f"from os.path import join; import sys; sys.path = [ r'{os.environ['SCONS_LIB_DIR']}' ] + sys.path; import SCons.Script; SCons.Script.main()"
        else:
            exec_script_main = f"from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-{self.scons_version}'), join(sys.prefix, 'scons-{self.scons_version}'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()"
        exec_script_main_xml = exec_script_main.replace("'", "&apos;")

        result = input.replace(r'<WORKPATH>', workpath)
        result = result.replace(r'<PYTHON>', python)
        result = result.replace(r'<SCONSCRIPT>', sconscript)
        result = result.replace(r'<SCONS_SCRIPT_MAIN>', exec_script_main)
        result = result.replace(r'<SCONS_SCRIPT_MAIN_XML>', exec_script_main_xml)
        result = result.replace(r'<PROJECT_GUID_1>', project_guid_1)
        result = result.replace(r'<PROJECT_GUID_2>', project_guid_2)
        result = result.replace(r'<SOLUTION_GUID_1>', solution_guid_1)
        result = result.replace(r'<SOLUTION_GUID_2>', solution_guid_2)
        result = result.replace('<SCC_VCPROJ_INFO>\n', vcproj_sccinfo)
        result = result.replace('<SCC_SLN_INFO>\n', sln_sccinfo)
        return result

    def get_expected_projects_proj_file_contents(
        self, vc_version, dirs, project_file, project_guid
    ):
        """Returns the expected .vcxproj file contents"""
        if project_file.endswith('.vcxproj'):
            fmt = expected_vcxprojfile_fmt
        else:
            fmt = expected_vcprojfile_fmt
        project_filename = os.path.split(project_file)[-1]
        project_basename = os.path.splitext(project_filename)[0]
        return fmt % {
            'PROJECT_BASENAME': project_basename,
            'PROJECT_GUID': project_guid,
            'TOOLS_VERSION': self._get_vcxproj_file_tools_version(vc_version),
            'INCLUDE_DIRS': self._get_vcxproj_file_cpp_path(dirs),
            'PLATFORM_TOOLSET': self._get_vcxproj_file_platform_toolset(vc_version),
        }

    def get_expected_projects_sln_file_contents(
        self,
        vc_version,
        project_file_1,
        project_file_2,
        have_solution_project_nodes=False,
        autofilter_solution_project_nodes=None,
    ):
        if not have_solution_project_nodes or autofilter_solution_project_nodes:
            rval = expected_projects_slnfile_fmt % {
                'FORMAT_VERSION': self._get_solution_file_format_version(vc_version),
                'VS_NUMBER': self._get_solution_file_vs_number(vc_version),
                'PROJECT_NAME_1': project_file_1.split('.')[0],
                'PROJECT_FILE_1': project_file_1,
                'PROJECT_NAME_2': project_file_2.split('.')[0],
                'PROJECT_FILE_2': project_file_2,
            }
        else:
            rval = expected_projects_slnfile_fmt_slnnodes % {
                'FORMAT_VERSION': self._get_solution_file_format_version(vc_version),
                'VS_NUMBER': self._get_solution_file_vs_number(vc_version),
                'PROJECT_NAME_1': project_file_1.split('.')[0],
                'PROJECT_FILE_1': project_file_1,
                'PROJECT_NAME_2': project_file_2.split('.')[0],
                'PROJECT_FILE_2': project_file_2,
                'SOLUTION_FILE_1': project_file_1.split('.')[0] + ".sln",
                'SOLUTION_FILE_2': project_file_2.split('.')[0] + ".sln",
            }
        return rval

    def get_expected_projects_sconscript_file_contents(
        self,
        vc_version,
        project_file_1,
        project_file_2,
        solution_file,
        autobuild_solution=0,
        autofilter_projects=None,
        default_guids=False,
    ):
        values = {
            'HOST_ARCH': self.get_vs_host_arch(),
            'MSVS_VERSION': vc_version,
            'PROJECT_FILE_1': project_file_1,
            'PROJECT_FILE_2': project_file_2,
            'SOLUTION_FILE': solution_file,
            "AUTOBUILD_SOLUTION": autobuild_solution,
            "AUTOFILTER_PROJECTS": autofilter_projects,
        }

        if default_guids:
            format = SConscript_projects_defaultguids_contents_fmt
        else:
            format = SConscript_projects_contents_fmt

            values.update(
                {
                    'PROJECT_GUID_1': PROJECT_GUID_1,
                    'PROJECT_GUID_2': PROJECT_GUID_2,
                }
            )
        return format % values
