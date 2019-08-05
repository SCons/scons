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
Verify that specifying a source file more than once works correctly
and dos not cause a rebuild.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
def cat(target, source, env):
    with open(str(target[0]), 'wb') as t:
        for s in source:
            with open(str(s), 'rb') as s:
                t.write(s.read())
env = Environment(BUILDERS = {'Cat' : Builder(action = cat)})
env.Cat('out.txt', ['f1.in', 'f2.in', 'f1.in'])
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

test.run(arguments='--debug=explain .')

test.must_match('out.txt', "f1.in\nf2.in\nf1.in\n")

test.up_to_date(options='--debug=explain', arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
