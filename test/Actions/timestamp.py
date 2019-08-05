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
Verify that changing an Action causes rebuilds when using timestamp
signatures.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()
env.Decider('timestamp-match')
env.Command('file.out', 'file.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('file.in', "file.in\n")

test.not_up_to_date(arguments = 'file.out')

test.write('SConstruct', """\
def my_copy(target, source, env):
    with open(str(target[0]), 'w') as f, open(str(source[0]), 'r') as infp:
        f.write(infp.read())
env = Environment()
env.Decider('timestamp-match')
env.Command('file.out', 'file.in', my_copy)
""")

test.not_up_to_date(arguments = 'file.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
