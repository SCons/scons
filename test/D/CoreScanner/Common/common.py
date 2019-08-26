"""
Verify that the D scanner can return multiple modules imported by
a single statement.
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

    _obj = TestSCons._obj

    if not isExecutableOfToolAvailable(test, tool) :
        test.skip_test("Required executable for tool '{0}' not found, skipping test.\n".format(tool))

    test.dir_fixture('Image')
    with open('SConstruct_template', 'r') as f:
        config = f.read().format(tool)
    test.write('SConstruct', config)

    arguments = 'test1%(_obj)s test2%(_obj)s' % locals()

    if tool == 'dmd':
        # The gdmd executable in Debian Unstable as at 2012-05-12, version 4.6.3 puts out messages on stderr
        # that cause inappropriate failure of the tests, so simply ignore them.
        test.run(arguments=arguments, stderr=None)
    else:
        test.run(arguments=arguments)

    test.up_to_date(arguments=arguments)

    test.write(['module2.d'], """\
module  module2;

int something_else;
""")

    if tool == 'dmd':
        # The gdmd executable in Debian Unstable as at 2012-05-12, version 4.6.3 puts out messages on stderr
        # that cause inappropriate failure of the tests, so simply ignore them.
        test.not_up_to_date(arguments=arguments, stderr=None)
    else:
        test.not_up_to_date(arguments=arguments)

    test.up_to_date(arguments=arguments)

    test.write(['p', 'submodule2.d'], """\
module p.submodule2;

int something_else;
""")

    if tool == 'dmd':
        # The gdmd executable in Debian Unstable as at 2012-05-12, version 4.6.3 puts out messages on stderr
        # that cause inappropriate failure of the tests, so simply ignore them.
        test.not_up_to_date(arguments=arguments, stderr=None)
    else:
        test.not_up_to_date(arguments=arguments)

    test.up_to_date(arguments=arguments)

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
