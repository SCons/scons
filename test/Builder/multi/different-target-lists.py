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
Verify that a target file can't be in two different target lists.
"""

# XXX It would be nice if the following two tests could be made to work
# by executing the action once for each unique set of targets. This
# would make it simple to deal with PDB files on Windows like so:
#
#     env.Object(['foo.obj', 'vc60.pdb'], 'foo.c')
#     env.Object(['bar.obj', 'vc60.pdb'], 'bar.c')

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
def build(env, target, source):
    for t in target:
        with open(str(target[0]), 'wb') as f:
            for s in source:
                with open(str(s), 'rb') as infp:
                    f.write(infp.read())

B = Builder(action=build, multi=1)
env = Environment(tools=[], BUILDERS = { 'B' : B })
env.B(target = ['file11a.out', 'file11b.out'], source = 'file11a.in')
env.B(target = ['file11b.out', 'file11c.out'], source = 'file11b.in')
""")

test.write('file11a.in', 'file11a.in\n')
test.write('file11b.in', 'file11b.in\n')

expect = TestSCons.re_escape("""
scons: *** Two different target lists have a target in common: file11b.out  (from ['file11a.out', 'file11b.out'] and from ['file11b.out', 'file11c.out'])
""") + TestSCons.file_expr

test.run(arguments='file11.out', status=2, stderr=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
