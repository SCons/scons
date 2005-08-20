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

import os
import os.path
import string
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match = TestCmd.match_re)

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)

if not '7.1' in test.msvs_versions():
    msg = "Visual Studio 7.1 not installed; skipping test.\n"
    test.skip_test(msg)

def diff_section(expect, actual):
    i = 0
    for x, y in zip(expect, actual):
        if x != y:
            return "Actual did not match expect at char %d:\n" \
                   "    Expect:  %s\n" \
                   "    Actual:  %s\n" \
                   % (i, repr(expect[i-20:i+40]), repr(actual[i-20:i+40]))
        i = i + 1
    return "Actual matched the expected output???"

expected_slnfile = """\
Microsoft Visual Studio Solution File, Format Version 8.00
Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "Test", "Test.vcproj", "{SLNGUID}"
	ProjectSection(ProjectDependencies) = postProject
	EndProjectSection
EndProject
Global
	GlobalSection(SolutionConfiguration) = preSolution
		ConfigName.0 = Release
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
"""

expected_vcprojfile = """\
<?xml version="1.0" encoding = "Windows-1252"?>
<VisualStudioProject
	ProjectType="Visual C++"
	Version="7.10"
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
				BuildCommandLine="echo Starting SCons &amp;&amp; <PYTHON> -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
				CleanCommandLine="echo Starting SCons &amp;&amp; <PYTHON> -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct -c <WORKPATH>\Test.exe"
				RebuildCommandLine="echo Starting SCons &amp;&amp; <PYTHON> -c &quot;<SCONS_SCRIPT_MAIN_XML>&quot; -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
				Output="<WORKPATH>\Test.exe"/>
		</Configuration>
	</Configurations>
	<References>
	</References>
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
"""

test.write('SConstruct', """\
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

test.run(arguments="Test.vcproj")

test.must_exist(test.workpath('Test.vcproj'))
vcproj = test.read('Test.vcproj', 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1')
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, diff_section(expect, vcproj)
    

test.must_exist(test.workpath('Test.sln'))
sln = test.read('Test.sln', 'r')
expect = test.msvs_substitute(expected_slnfile, '7.1')
# don't compare the pickled data
assert sln[:len(expect)] == expect, diff_section(expect, sln)

test.run(arguments='-c .')

test.must_not_exist(test.workpath('Test.vcproj'))
test.must_not_exist(test.workpath('Test.sln'))

test.run(arguments='Test.vcproj')

test.must_exist(test.workpath('Test.vcproj'))
test.must_exist(test.workpath('Test.sln'))

test.run(arguments='-c Test.sln')

test.must_not_exist(test.workpath('Test.vcproj'))
test.must_not_exist(test.workpath('Test.sln'))




# Test that running SCons with $PYTHON_ROOT in the environment
# changes the .vcproj output as expected.
os.environ['PYTHON_ROOT'] = 'xyzzy'

test.run(arguments='Test.vcproj')

python = os.path.join('$(PYTHON_ROOT)', os.path.split(sys.executable)[1])

test.must_exist(test.workpath('Test.vcproj'))
vcproj = test.read('Test.vcproj', 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, diff_section(expect, vcproj)

os.environ['PYTHON_ROOT'] = ''



test.write('SConstruct', """\
env=Environment(MSVS_VERSION = '7.1')

env.MSVSProject(target = 'foo.vcproj',
                srcs = ['foo.c'],
                buildtarget = 'foo.exe',
                variant = 'Release')

t = env.Program('foo.c')
print "t =", t[0]
print "t =", t[0].abspath
import sys
print sys.argv
""")

test.write('foo.c', r"""
int
main(int argc, char *argv)
{
    printf("test.c\n");
    exit (0);
}
""")

# Let SCons figure out the Visual Studio environment variables for us and
# print out a statement that we can exec to suck them into our external
# environment so we can execute devenv and really try to build something.

test.run(arguments = '-n -q -Q -f -', stdin = """\
env = Environment(tools = ['msvc'])
print "os.environ.update(%s)" % repr(env['ENV'])
""")

exec(test.stdout())

test.run(arguments='foo.vcproj')

test.vcproj_sys_path('foo.vcproj')

test.run(program=['devenv'],
         arguments=['foo.sln', '/build', 'Release'])

test.run(program=test.workpath('foo'), stdout = "test.c\n")



test.pass_test()
