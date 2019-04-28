"""
Test compiling and executing a project with a C module.
"""

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

from os.path import abspath, dirname

import sys
sys.path.insert(1, abspath(dirname(__file__) + '/../../Support'))

from executablesSearch import isExecutableOfToolAvailable

def testForTool(tool):

    test = TestSCons.TestSCons()

    if not isExecutableOfToolAvailable(test, tool) :
        test.skip_test("Required executable for tool '{0}' not found, skipping test.\n".format(tool))

    test.dir_fixture('Image')
    with open('SConstruct_template', 'r') as f:
        config = f.read().format(tool)
    test.write('SConstruct', config)

    test.run()

    test.must_not_exist(test.workpath('amod.o'))
    test.must_not_exist(test.workpath('bmod.o'))
    test.must_not_exist(test.workpath('main.o'))
    if tool == 'gdc':
        test.must_not_exist(test.workpath('project.o'))
    else:
        test.must_exist(test.workpath('project.o'))
    test.must_exist(test.workpath('project'))

    test.run(program=test.workpath('project'+TestSCons._exe))
    test.fail_test(test.stdout() != '''This is a test program for a new SCons D builder.
The value is 42.
''')

    test.run('-c')

    test.must_not_exist(test.workpath('amod.o'))
    test.must_not_exist(test.workpath('bmod.o'))
    test.must_not_exist(test.workpath('main.o'))
    test.must_not_exist(test.workpath('project.o'))
    test.must_not_exist(test.workpath('project'))

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
