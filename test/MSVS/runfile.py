
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
Test that we can generate Visual Studio 8.0 project (.vcproj) and
solution (.sln) files that look correct.
"""

import os
import sys

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

expected_vcprojfile = """\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
\tProjectType="Visual C++"
\tVersion="8.00"
\tName="Test"
\tProjectGUID="<PROJECT_GUID>"
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
\t\t\t\tOutput="runfile.exe"
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
\t\t\t<File
\t\t\t\tRelativePath="test.cpp">
\t\t\t</File>
\t\t<File
\t\t\tRelativePath="<SCONSCRIPT>">
\t\t</File>
\t</Files>
\t<Globals>
\t</Globals>
</VisualStudioProject>
"""



SConscript_contents = """\
env=Environment(tools=['msvs'], MSVS_VERSION = '8.0')

env.MSVSProject(target = 'Test.vcproj',
                slnguid = '{SLNGUID}',
                srcs = ['test.cpp'],
                buildtarget = 'Test.exe',
                runfile = 'runfile.exe',
                variant = 'Release',
                auto_build_solution = 0)
"""



test.subdir('work1')

test.write(['work1', 'SConstruct'], SConscript_contents)

test.run(chdir='work1', arguments="Test.vcproj")

test.must_exist(test.workpath('work1', 'Test.vcproj'))
vcproj = test.read(['work1', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '8.0', 'work1', 'SConstruct')
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
