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
Test adding a src_builder to the RES builder so that RC files can
be generated.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

fake_rc = test.workpath('fake_rc.py')

test.write(fake_rc, """\
import sys
with open(sys.argv[1], 'w') as fo, open(sys.argv[2], 'r') as fi:
    fo.write("fake_rc.py\\n" + fi.read())
""")

test.write('SConstruct', """
def generate_rc(target, source, env):
    t = str(target[0])
    s = str(source[0])
    with open(t, 'w') as fo, open(s, 'r') as fi:
        fo.write('generate_rc\\n' + fi.read())

env = Environment(tools=['msvc'],
                  RCCOM=r'%(_python_)s %(fake_rc)s $TARGET $SOURCE')
env['BUILDERS']['GenerateRC'] = Builder(action=generate_rc,
                                        suffix='.rc',
                                        src_suffix='.in')
env['BUILDERS']['RES'].src_builder.append('GenerateRC')

env.RES('my.in')
""" % locals())

test.write('my.in', "my.in\n")

test.run(arguments = '.')

test.must_match('my.rc', "generate_rc\nmy.in\n", mode='r')
test.must_match('my.res', "fake_rc.py\ngenerate_rc\nmy.in\n", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
