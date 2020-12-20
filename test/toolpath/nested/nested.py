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

import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture('image')

test.run(arguments = '.', stdout = """\
scons: Reading SConscript files ...
Test where tools are located under site_scons/site_tools
env1['Toolpath_TestTool1'] = 1
env1['Toolpath_TestTool2'] = 1
env1['Toolpath_TestTool1_1'] = 1
env1['Toolpath_TestTool1_2'] = 1
env1['Toolpath_TestTool2_1'] = 1
env1['Toolpath_TestTool2_2'] = 1
Test where toolpath is set in the env constructor
env2['Toolpath_TestTool1'] = 1
env2['Toolpath_TestTool2'] = 1
env2['Toolpath_TestTool1_1'] = 1
env2['Toolpath_TestTool1_2'] = 1
env2['Toolpath_TestTool2_1'] = 1
env2['Toolpath_TestTool2_2'] = 1
Test a Clone
derived['Toolpath_TestTool1_1'] = 1
Test using syspath as the toolpath
Lets pretend that tools_example within Libs is actually a module installed via pip
env3['Toolpath_TestTool1'] = 1
env3['Toolpath_TestTool2'] = 1
env3['Toolpath_TestTool1_1'] = 1
env3['Toolpath_TestTool1_2'] = 1
env3['Toolpath_TestTool2_1'] = 1
env3['Toolpath_TestTool2_2'] = 1
Test using PyPackageDir
env4['Toolpath_TestTool2_1'] = 1
env4['Toolpath_TestTool2_2'] = 1
scons: done reading SConscript files.
scons: Building targets ...
scons: `.' is up to date.
scons: done building targets.
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
