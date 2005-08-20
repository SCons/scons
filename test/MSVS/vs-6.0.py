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

if not '6.0' in test.msvs_versions():
    msg = "Visual Studio 6 not installed; skipping test.\n"
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
# PROP BASE Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP BASE Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP BASE Target_File "<WORKPATH>\Test.exe"
# PROP BASE Bsc_Name ""
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "<WORKPATH>"
# PROP Intermediate_Dir "<WORKPATH>"
# PROP Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
# PROP Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C <WORKPATH> -f SConstruct <WORKPATH>\Test.exe"
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

SOURCE="test.c"
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



test.write('SConstruct','''
env=Environment(MSVS_VERSION = '6.0')

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
''')

test.run(arguments="Test.dsp")

test.must_exist(test.workpath('Test.dsp'))
dsp = test.read('Test.dsp', 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, diff_section(expect, dsp)

test.must_exist(test.workpath('Test.dsw'))
dsw = test.read('Test.dsw', 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0')
assert dsw == expect, diff_section(expect, dsw)

test.run(arguments='-c .')

test.must_not_exist(test.workpath('Test.dsp'))
test.must_not_exist(test.workpath('Test.dsw'))

test.run(arguments='Test.dsp')

test.must_exist(test.workpath('Test.dsp'))
test.must_exist(test.workpath('Test.dsw'))

test.run(arguments='-c Test.dsw')

test.must_not_exist(test.workpath('Test.dsp'))
test.must_not_exist(test.workpath('Test.dsw'))



test.write('SConstruct','''
env=Environment(MSVS_VERSION = '6.0')

env.MSVSProject(target = 'Test.dsp',
                srcs = ['test.c'],
                buildtarget = 'Test.exe',
                variant = 'Release')

env.Program('test.c')
''')

test.write('test.c', r"""
int
main(int argc, char *argv)
{
    printf("test.c\n");
    exit (0);
}
""")

# Let SCons figure out the Visual Studio environment variables for us and
# print out a statement that we can exec to suck them into our external
# environment so we can execute msdev and really try to build something.

test.run(arguments = '-n -q -Q -f -', stdin = """\
env = Environment(tools = ['msvc'])
print "os.environ.update(%s)" % repr(env['ENV'])
""")

exec(test.stdout())

test.run(arguments='Test.dsp')

test.run(program=['msdev'],
         arguments=['Test.dsp', '/MAKE', 'test - Win32 Release'])

test.run(program=test.workpath('test'), stdout = "test.c\n")



test.pass_test()
