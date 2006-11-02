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
Test that we can generate Visual Studio 6 project (.dsp) and solution
(.dsw) files that look correct.
"""

import os
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    msg = "Skipping Visual Studio test on non-Windows platform '%s'\n" % sys.platform
    test.skip_test(msg)



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
# PROP BASE Output_Dir ""
# PROP BASE Intermediate_Dir ""
# PROP BASE Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct Test.exe"
# PROP BASE Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct Test.exe"
# PROP BASE Target_File "Test.exe"
# PROP BASE Bsc_Name ""
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ""
# PROP Intermediate_Dir ""
# PROP Cmd_Line "echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct Test.exe"
# PROP Rebuild_Opt "-c && echo Starting SCons && "<PYTHON>" -c "<SCONS_SCRIPT_MAIN>" -C "<WORKPATH>" -f SConstruct Test.exe"
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

expected_dswfile = '''\
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



SConscript_contents = """\
env=Environment(tools=['msvs'], MSVS_VERSION = '6.0')

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



test.subdir('work1')

test.write(['work1', 'SConstruct'], SConscript_contents)

test.run(chdir='work1', arguments="Test.dsp")

test.must_exist(test.workpath('work1', 'Test.dsp'))
dsp = test.read(['work1', 'Test.dsp'], 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0', 'work1', 'SConstruct')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, test.diff_substr(expect, dsp)

test.must_exist(test.workpath('work1', 'Test.dsw'))
dsw = test.read(['work1', 'Test.dsw'], 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0', 'work1', 'SConstruct')
assert dsw == expect, test.diff_substr(expect, dsw)

test.run(chdir='work1', arguments='-c .')

test.must_not_exist(test.workpath('work1', 'Test.dsp'))
test.must_not_exist(test.workpath('work1', 'Test.dsw'))

test.run(chdir='work1', arguments='Test.dsp')

test.must_exist(test.workpath('work1', 'Test.dsp'))
test.must_exist(test.workpath('work1', 'Test.dsw'))

test.run(chdir='work1', arguments='-c Test.dsw')

test.must_not_exist(test.workpath('work1', 'Test.dsp'))
test.must_not_exist(test.workpath('work1', 'Test.dsw'))



test.subdir('work2', ['work2', 'src'])

test.write(['work2', 'SConstruct'], """\
SConscript('src/SConscript', build_dir='build')
""")

test.write(['work2', 'src', 'SConscript'], SConscript_contents)

test.run(chdir='work2', arguments=".")

dsp = test.read(['work2', 'src', 'Test.dsp'], 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0', 'work2', 'SConstruct')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, test.diff_substr(expect, dsp)

test.must_exist(test.workpath('work2', 'src', 'Test.dsw'))
dsw = test.read(['work2', 'src', 'Test.dsw'], 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0',
                              os.path.join('work2', 'src'))
assert dsw == expect, test.diff_substr(expect, dsw)

test.must_match(['work2', 'build', 'Test.dsp'], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('work2', 'src', 'Test.dsp'),
                mode='r')

test.must_match(['work2', 'build', 'Test.dsw'], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('work2', 'src', 'Test.dsw'),
                mode='r')



test.subdir('work3')

test.write(['work3', 'SConstruct'], """\
env=Environment(tools=['msvs'], MSVS_VERSION = '6.0')

testsrc = ['test.c']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

p = env.MSVSProject(target = 'Test.dsp',
                    srcs = testsrc,
                    incs = testincs,
                    localincs = testlocalincs,
                    resources = testresources,
                    misc = testmisc,
                    buildtarget = 'Test.exe',
                    variant = 'Release',
                    auto_build_solution = 0)

env.MSVSSolution(target = 'Test.dsw',
                 slnguid = '{SLNGUID}',
                 projects = [p],
                 variant = 'Release')
""")

test.run(chdir='work3', arguments=".")

test.must_exist(test.workpath('work3', 'Test.dsp'))
dsp = test.read(['work3', 'Test.dsp'], 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0', 'work3', 'SConstruct')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, test.diff_substr(expect, dsp)

test.must_exist(test.workpath('work3', 'Test.dsw'))
dsw = test.read(['work3', 'Test.dsw'], 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0', 'work3', 'SConstruct')
assert dsw == expect, test.diff_substr(expect, dsw)

test.run(chdir='work3', arguments='-c .')

test.must_not_exist(test.workpath('work3', 'Test.dsp'))
test.must_not_exist(test.workpath('work3', 'Test.dsw'))

test.run(chdir='work3', arguments='.')

test.must_exist(test.workpath('work3', 'Test.dsp'))
test.must_exist(test.workpath('work3', 'Test.dsw'))

test.run(chdir='work3', arguments='-c Test.dsw')

test.must_exist(test.workpath('work3', 'Test.dsp'))
test.must_not_exist(test.workpath('work3', 'Test.dsw'))

test.run(chdir='work3', arguments='-c Test.dsp')

test.must_not_exist(test.workpath('work3', 'Test.dsp'))



test.pass_test()
