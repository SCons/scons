# MIT License
#
# Copyright The SCons Foundation
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

"""
Test D compilers use of .di files
"""

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

    for img in ["VariantDirImage","Image"]:
            
        if img == "VariantDirImage":
            buildPrefix = "build/"
            sourcePrefix = "hws/"
        else:
            sourcePrefix = ""
            buildPrefix = ""
        test.dir_fixture(img)
        with open('SConstruct_template', 'r') as f:
            config = f.read().format(tool)
        test.write('SConstruct', config)

        test.run(options="--debug=explain")

        test.must_exist(buildPrefix + 'parts/part.o')
        test.must_exist(buildPrefix + 'main.o')
        test.must_exist(buildPrefix + 'include/part.di')
        test.must_exist(buildPrefix + 'hw')

        test.run(program=test.workpath(buildPrefix + 'hw'+TestSCons._exe))
        test.fail_test(test.stdout() != 'Hello World.\n')

        #add a comment and test that this doesn't result in a complete rebuild of all the files that include helloWorld.d because the comment doesn't change helloWorld.di
        test.write(sourcePrefix + "parts/part.d",'''import std.stdio;
void go()
{
    //comment
    writeln("Hello World.");
}''')

        test.not_up_to_date(buildPrefix + "parts/part.o")
        test.up_to_date(buildPrefix + "main.o",options='--debug=explain')
        test.up_to_date(buildPrefix + "hw")

        test.run("-c")
        
        test.must_not_exist(buildPrefix + 'parts/part.o')
        test.must_not_exist(buildPrefix + 'main.o')
        test.must_not_exist(buildPrefix + 'include/part.di')
        test.must_not_exist(buildPrefix + 'hw')

    test.pass_test()
# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
