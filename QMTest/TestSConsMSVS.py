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
import string
import sys

from TestSCons import *
from TestSCons import __all__



expected_slnfile_7_0 = """\
Microsoft Visual Studio Solution File, Format Version 7.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{E5466E26-0003-F18B-8F8A-BCD76C86388D}"
EndProject
Global
\tGlobalSection(SolutionConfiguration) = preSolution
\t\tConfigName.0 = Release
\tEndGlobalSection
\tGlobalSection(ProjectDependencies) = postSolution
\tEndGlobalSection
\tGlobalSection(ProjectConfiguration) = postSolution
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release.ActiveCfg = Release|Win32
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ExtensibilityGlobals) = postSolution
\tEndGlobalSection
\tGlobalSection(ExtensibilityAddIns) = postSolution
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile_7_0 = """\
<?xml version="1.0" encoding = "Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="7.00"
\tName="Test"
\tProjectGUID=""
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
\t\t\tOutputDirectory=""
\t\t\tIntermediateDirectory=""
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="FALSE">
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tRebuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
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
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='7.0')

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
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{E5466E26-0003-F18B-8F8A-BCD76C86388D}"
\tProjectSection(ProjectDependencies) = postProject
\tEndProjectSection
EndProject
Global
\tGlobalSection(SolutionConfiguration) = preSolution
\t\tConfigName.0 = Release
\tEndGlobalSection
\tGlobalSection(ProjectConfiguration) = postSolution
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release.ActiveCfg = Release|Win32
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release.Build.0 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ExtensibilityGlobals) = postSolution
\tEndGlobalSection
\tGlobalSection(ExtensibilityAddIns) = postSolution
\tEndGlobalSection
EndGlobal
"""

expected_vcprojfile_7_1 = """\
<?xml version="1.0" encoding = "Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="7.10"
\tName="Test"
\tProjectGUID=""
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
\t\t\tOutputDirectory=""
\t\t\tIntermediateDirectory=""
\t\t\tConfigurationType="0"
\t\t\tUseOfMFC="0"
\t\t\tATLMinimizesCRunTimeLibraryUsage="FALSE">
\t\t\t<Tool
\t\t\t\tName="VCNMakeTool"
\t\t\t\tBuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
\t\t\t\tCleanCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct -c &quot;Test.exe&quot;"
\t\t\t\tRebuildCommandLine="echo Starting SCons &amp;&amp; &quot;<PYTHON>&quot; -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C &quot;<WORKPATH>&quot; -f SConstruct &quot;Test.exe&quot;"
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
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='7.1')

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
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{E5466E26-0003-F18B-8F8A-BCD76C86388D}"
EndProject
Global
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tRelease|Win32 = Release|Win32
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release|Win32.ActiveCfg = Release|Win32
\t\t{E5466E26-0003-F18B-8F8A-BCD76C86388D}.Release|Win32.Build.0 = Release|Win32
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
\tSccProjectName=""
\tSccLocalPath=""
\tRootNamespace="Test"
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
\t\t\t\tPreprocessorDefinitions=""
\t\t\t\tIncludeSearchPath=""
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

SConscript_contents_8_0 = """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='8.0')

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
print "self._scons_version =", repr(SCons.__%s__)
env = Environment();
print "self._msvs_versions =", str(env['MSVS']['VERSIONS'])
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
        contents = string.replace(contents, orig, replace)
        self.write(fname, contents)

    def msvs_substitute(self, input, msvs_ver,
                        subdir=None, sconscript=None,
                        python=None,
                        project_guid=None):
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

        if os.environ.has_key('SCONS_LIB_DIR'):
            exec_script_main = "from os.path import join; import sys; sys.path = [ r'%s' ] + sys.path; import SCons.Script; SCons.Script.main()" % os.environ['SCONS_LIB_DIR']
        else:
            exec_script_main = "from os.path import join; import sys; sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-%s'), join(sys.prefix, 'scons-%s'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons') ] + sys.path; import SCons.Script; SCons.Script.main()" % (self._scons_version, self._scons_version)
        exec_script_main_xml = string.replace(exec_script_main, "'", "&apos;")

        result = string.replace(input, r'<WORKPATH>', workpath)
        result = string.replace(result, r'<PYTHON>', python)
        result = string.replace(result, r'<SCONSCRIPT>', sconscript)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN>', exec_script_main)
        result = string.replace(result, r'<SCONS_SCRIPT_MAIN_XML>', exec_script_main_xml)
        result = string.replace(result, r'<PROJECT_GUID>', project_guid)
        return result

    def get_msvs_executable(self, version):
        """Returns a full path to the executable (MSDEV or devenv)
        for the specified version of Visual Studio.
        """
        common_msdev98_bin_msdev_com = ['Common', 'MSDev98', 'Bin', 'MSDEV.COM']
        common7_ide_devenv_com       = ['Common7', 'IDE', 'devenv.com']
        common7_ide_vcexpress_exe    = ['Common7', 'IDE', 'VCExpress.exe']
        sub_paths = {
            '6.0' : [
                common_msdev98_bin_msdev_com,
            ],
            '7.0' : [
                common7_ide_devenv_com,
            ],
            '7.1' : [
                common7_ide_devenv_com,
            ],
            '8.0' : [
                common7_ide_devenv_com,
                common7_ide_vcexpress_exe,
            ],
        }
        from SCons.Tool.msvs import get_msvs_install_dirs
        vs_path = get_msvs_install_dirs(version)['VSINSTALLDIR']
        for sp in sub_paths[version]:
            p = apply(os.path.join, [vs_path] + sp)
            if os.path.exists(p):
                return p
        return apply(os.path.join, [vs_path] + sub_paths[version][0])
