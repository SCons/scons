"""
These tests check a problem with the linker options setting.
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

from SCons.Environment import Base

from os.path import abspath, dirname, join

import sys
sys.path.insert(1, abspath(dirname(__file__) + '/../../../Support'))

from executablesSearch import isExecutableOfToolAvailable

def testForTool(tool):

    test = TestSCons.TestSCons()

    if not isExecutableOfToolAvailable(test, tool) :
        test.skip_test("Required executable for tool '{0}' not found, skipping test.\n".format(tool))

    platform = Base()['PLATFORM']
    if platform == 'posix':
        libraryname = 'libstuff.so'
        filename = 'stuff.os'
    elif platform == 'darwin':
        if tool == 'dmd' or tool == 'gdc':
            test.skip_test('Dynamic libraries not yet supported by dmd and gdc on OSX.\n')
        libraryname = 'libstuff.dylib'
        filename = 'stuff.os'
    elif platform == 'win32':
        libraryname = 'stuff.dll'
        filename = 'stuff.obj'
    else:
        test.fail_test('No information about platform: ' + platform)

    test.dir_fixture('Project')
    with open('SConstruct_template', 'r') as f:
        config = f.read().format('tools=["{0}", "link"]'.format(tool))
    test.write('SConstruct', config)

    test.run()

    for f in (libraryname, filename, 'test1', 'test1.o', 'test2', 'test2.o'):
        test.must_exist(test.workpath(join('test', 'test1', f)))

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
