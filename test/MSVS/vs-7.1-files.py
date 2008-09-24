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

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['7.1']



expected_slnfile = TestSConsMSVS.expected_slnfile_7_1
expected_vcprojfile = TestSConsMSVS.expected_vcprojfile_7_1
SConscript_contents = TestSConsMSVS.SConscript_contents_7_1



test.subdir('work1')

test.write(['work1', 'SConstruct'], SConscript_contents)

test.run(chdir='work1', arguments="Test.vcproj")

test.must_exist(test.workpath('work1', 'Test.vcproj'))
vcproj = test.read(['work1', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', 'work1', 'SConstruct')
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('work1', 'Test.sln'))
sln = test.read(['work1', 'Test.sln'], 'r')
expect = test.msvs_substitute(expected_slnfile, '7.1', 'work1', 'SConstruct')
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
python = os.path.join('$(PYTHON_ROOT)', os.path.split(TestSConsMSVS.python)[1])

test.run(chdir='work1', arguments='Test.vcproj')

test.must_exist(test.workpath('work1', 'Test.vcproj'))
vcproj = test.read(['work1', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', 'work1', 'SConstruct',
                              python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

del os.environ['PYTHON_ROOT']
python = None



test.subdir('work2', ['work2', 'src'])

test.write(['work2', 'SConstruct'], """\
SConscript('src/SConscript', variant_dir='build')
""")

test.write(['work2', 'src', 'SConscript'], SConscript_contents)

test.run(chdir='work2', arguments=".")

vcproj = test.read(['work2', 'src', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.0', 'work2', 'SConstruct',
                              python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('work2', 'src', 'Test.sln'))
sln = test.read(['work2', 'src', 'Test.sln'], 'r')
expect = test.msvs_substitute(expected_slnfile, '7.0',
                              os.path.join('work2', 'src'))
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

test.must_match(['work2', 'build', 'Test.vcproj'], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('work2', 'src', 'Test.vcproj'),
                mode='r')

test.must_match(['work2', 'build', 'Test.sln'], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('work2', 'src', 'Test.sln'),
                mode='r')



test.subdir('work3')

test.write(['work3', 'SConstruct'], """\
env=Environment(platform='win32', tools=['msvs'], MSVS_VERSION='7.1')

testsrc = ['test1.cpp', 'test2.cpp']
testincs = ['sdk.h']
testlocalincs = ['test.h']
testresources = ['test.rc']
testmisc = ['readme.txt']

p = env.MSVSProject(target = 'Test.vcproj',
                    srcs = testsrc,
                    incs = testincs,
                    localincs = testlocalincs,
                    resources = testresources,
                    misc = testmisc,
                    buildtarget = 'Test.exe',
                    variant = 'Release',
                    auto_build_solution = 0)

env.MSVSSolution(target = 'Test.sln',
                 slnguid = '{SLNGUID}',
                 projects = [p],
                 variant = 'Release')
""")

test.run(chdir='work3', arguments=".")

test.must_exist(test.workpath('work3', 'Test.vcproj'))
vcproj = test.read(['work3', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.1', 'work3', 'SConstruct',
                              python=python)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('work3', 'Test.sln'))
sln = test.read(['work3', 'Test.sln'], 'r')
expect = test.msvs_substitute(expected_slnfile, '7.1', 'work3', 'SConstruct')
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

test.run(chdir='work3', arguments='-c .')

test.must_not_exist(test.workpath('work3', 'Test.vcproj'))
test.must_not_exist(test.workpath('work3', 'Test.sln'))

test.run(chdir='work3', arguments='.')

test.must_exist(test.workpath('work3', 'Test.vcproj'))
test.must_exist(test.workpath('work3', 'Test.sln'))

test.run(chdir='work3', arguments='-c Test.sln')

test.must_exist(test.workpath('work3', 'Test.vcproj'))
test.must_not_exist(test.workpath('work3', 'Test.sln'))

test.run(chdir='work3', arguments='-c Test.vcproj')

test.must_not_exist(test.workpath('work3', 'Test.vcproj'))



test.pass_test()
