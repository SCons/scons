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
Test that we can generate Visual Studio 7.0 project (.vcproj) and
solution (.sln) files that look correct when using a variant_dir.
"""

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()
host_arch = test.get_vs_host_arch()


# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['7.0']



expected_slnfile = TestSConsMSVS.expected_slnfile_7_0
expected_vcprojfile = TestSConsMSVS.expected_vcprojfile_7_0
SConscript_contents = TestSConsMSVS.SConscript_contents_7_0



test.subdir('src')

test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build')
""")

test.write(['src', 'SConscript'], SConscript_contents%{'HOST_ARCH': host_arch})

test.run(arguments=".")

project_guid = "{CB4637F1-2205-50B7-B115-DCFA0DA68FB1}"
vcproj = test.read(['src', 'Test.vcproj'], 'r')
expect = test.msvs_substitute(expected_vcprojfile, '7.0', None, 'SConstruct',
                              project_guid=project_guid)
# don't compare the pickled data
assert vcproj[:len(expect)] == expect, test.diff_substr(expect, vcproj)

test.must_exist(test.workpath('src', 'Test.sln'))
sln = test.read(['src', 'Test.sln'], 'r')
expect = test.msvs_substitute(expected_slnfile, '7.0', 'src',
                              project_guid=project_guid)
# don't compare the pickled data
assert sln[:len(expect)] == expect, test.diff_substr(expect, sln)

test.must_match(['build', 'Test.vcproj'], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('src', 'Test.vcproj'),
                mode='r')

test.must_match(['build', 'Test.sln'], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', 'Test.sln'),
                mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
