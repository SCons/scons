"""
Support functions for all the tests.
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

from os.path import abspath, dirname
from subprocess import check_output

import sys
sys.path.insert(1, abspath(dirname(__file__) + '/../../Support'))

from executablesSearch import isExecutableOfToolAvailable

def testForTool(tool):

    test = TestSCons.TestSCons()

    if not isExecutableOfToolAvailable(test, tool) :
        test.skip_test("Required executable for tool '{0}' not found, skipping test.\n".format(tool))

    if tool == 'gdc':
        result = check_output(('gdc', '--version'))
        version = result.decode().splitlines()[0].split()[3]
        major, minor, debug = [int(x) for x in version.split('.')]
        if (major < 6) or (major == 6 and minor < 3):
            test.skip_test('gdc prior to version 6.0.0 does not support shared libraries.\n')

    if tool == 'dmd' and Base()['DC'] == 'gdmd':
        test.skip_test('gdmd does not recognize the -shared option so cannot support linking of shared objects.\n')

    code_root = 'code'
    library_root = 'answer'

    platform = Base()['PLATFORM']
    if platform == 'posix':
        code_name = code_root + '.o'
        library_name = 'lib' + library_root + '.so'
    elif platform == 'darwin':
        code_name = code_root + '.o'
        library_name = 'lib' + library_root + '.dylib'
        # As at 2017-08-22, DMD 2.075.1, LDC 1.2.0 (D 2.072.2), and GDC 7.2.0 (D 2.068.2)
        # it is not clear if shared libraries are supported on macOS.
        # test.skip_test('Dynamic libraries not yet supported on macOS.\n')
    elif platform == 'win32':
        code_name = code_root + '.obj'
        library_name = library_root + '.dll'
    else:
        test.fail_test()

    test.dir_fixture('Image')
    with open('SConstruct_template', 'r') as f:
        config = f.read().format(tool)
    test.write('SConstruct', config)

    if Base()['DC'] == 'gdmd':
        # The gdmd executable in Debian Unstable as at 2012-05-12, version 4.6.3 puts out messages on stderr
        # that cause inappropriate failure of the tests, so simply ignore them.
        test.run(stderr=None)
    else:
        test.run()

    test.must_exist(test.workpath(code_name))
    test.must_exist(test.workpath(library_name))

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
