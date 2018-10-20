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
Verify the -c option's ability to clean generated Visual Studio 6
project (.dsp) and solution (.dsw) files.
"""

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()
host_arch = test.get_vs_host_arch()



# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['6.0']



expected_dspfile = TestSConsMSVS.expected_dspfile_6_0
expected_dswfile = TestSConsMSVS.expected_dswfile_6_0



test.write('SConstruct', """\
env=Environment(platform='win32', tools=['msvs'],
                MSVS_VERSION='6.0',HOST_ARCH='%(HOST_ARCH)s')

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
"""%{'HOST_ARCH':host_arch})

test.run()

test.must_exist(test.workpath('Test.dsp'))
dsp = test.read('Test.dsp', 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0', None, 'SConstruct')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, test.diff_substr(expect, dsp)

test.must_exist(test.workpath('Test.dsw'))
dsw = test.read('Test.dsw', 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0', None, 'SConstruct')
assert dsw == expect, test.diff_substr(expect, dsw)

test.run(arguments='-c .')

test.must_not_exist(test.workpath('Test.dsp'))
test.must_not_exist(test.workpath('Test.dsw'))

test.run(arguments='.')

test.must_exist(test.workpath('Test.dsp'))
test.must_exist(test.workpath('Test.dsw'))

test.run(arguments='-c Test.dsw')

test.must_exist(test.workpath('Test.dsp'))
test.must_not_exist(test.workpath('Test.dsw'))

test.run(arguments='-c Test.dsp')

test.must_not_exist(test.workpath('Test.dsp'))



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
