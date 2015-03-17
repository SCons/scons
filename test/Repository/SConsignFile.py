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
Verify that the Repository option works when recording signature
information in an SConsignFile().
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('repository', 'work')

SConstruct_contents = """\
SConsignFile('sconsignfile')
env = Environment()
result = env.Command('file.out', 'file.in', Copy("$TARGET", "$SOURCE"))
Default(result)
"""

test.write(['repository', 'SConstruct'], SConstruct_contents)

test.write(['repository', 'file.in'], "repository/file.in\n")

test.run(chdir='repository')

test.must_match(['repository', 'file.out'], "repository/file.in\n")

test.write(['work', 'SConstruct'], SConstruct_contents)

test.run(chdir='work',
         arguments='-Y ../repository -n --debug=explain',
         stdout=test.wrap_stdout("scons: `file.out' is up to date.\n"))

test.must_not_exist(['work', 'file.out'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
