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
(.dsw) files that look correct when using a variant_dir.
"""

import TestSConsMSVS

test = TestSConsMSVS.TestSConsMSVS()

host_arch = test.get_vs_host_arch()


# Make the test infrastructure think we have this version of MSVS installed.
test._msvs_versions = ['6.0']

expected_dspfile = TestSConsMSVS.expected_dspfile_6_0
expected_dswfile = TestSConsMSVS.expected_dswfile_6_0
SConscript_contents = TestSConsMSVS.SConscript_contents_6_0


test.subdir('src')

test.write('SConstruct', """\
SConscript('src/SConscript', variant_dir='build')
""")

test.write(['src', 'SConscript'], SConscript_contents%{'HOST_ARCH': host_arch})

test.run(arguments=".")

dsp = test.read(['src', 'Test.dsp'], 'r')
expect = test.msvs_substitute(expected_dspfile, '6.0', None, 'SConstruct')
# don't compare the pickled data
assert dsp[:len(expect)] == expect, test.diff_substr(expect, dsp)

test.must_exist(test.workpath('src', 'Test.dsw'))
dsw = test.read(['src', 'Test.dsw'], 'r')
expect = test.msvs_substitute(expected_dswfile, '6.0', 'src')
assert dsw == expect, test.diff_substr(expect, dsw)

test.must_match(['build', 'Test.dsp'], """\
This is just a placeholder file.
The real project file is here:
%s
""" % test.workpath('src', 'Test.dsp'),
                mode='r')

test.must_match(['build', 'Test.dsw'], """\
This is just a placeholder file.
The real workspace file is here:
%s
""" % test.workpath('src', 'Test.dsw'),
                mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
