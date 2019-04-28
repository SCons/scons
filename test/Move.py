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
Verify that the Move() Action works.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
Execute(Move('f1.out', 'f1.in'))
Execute(Move('File-f1.out', File('f1.in-File')))
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())
Cat = Action(cat)
env = Environment()
env.Command('f2.out', 'f2.in', [Cat, Move("f3.out", "f3.in")])
env = Environment(OUT = 'f4.out', IN = 'f4.in')
env.Command('f5.out', 'f5.in', [Move("$OUT", "$IN"), Cat])
env.Command('f6.out', 'f6.in', [Cat, Move("Move-$TARGET", "$SOURCE-Move")])
""")

test.write('f1.in', "f1.in\n")
test.write('f1.in-File', "f1.in-File\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")
test.write('f6.in-Move', "f6.in-Move\n")

expect = test.wrap_stdout(read_str = """\
Move("f1.out", "f1.in")
Move("File-f1.out", "f1.in-File")
""",
                          build_str = """\
cat(["f2.out"], ["f2.in"])
Move("f3.out", "f3.in")
Move("f4.out", "f4.in")
cat(["f5.out"], ["f5.in"])
cat(["f6.out"], ["f6.in"])
Move("Move-f6.out", "f6.in-Move")
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.must_not_exist('f1.out')
test.must_not_exist('File-f1.out')
test.must_not_exist('f2.out')
test.must_not_exist('f3.out')
test.must_not_exist('f4.out')
test.must_not_exist('f5.out')
test.must_not_exist('f6.out')
test.must_not_exist('Move-f6.out')

test.run()

test.must_match('f1.out', "f1.in\n")
test.must_match('File-f1.out', "f1.in-File\n")
test.must_match('f2.out', "f2.in\n")
test.must_not_exist('f3.in')
test.must_match('f3.out', "f3.in\n")
test.must_match('f4.out', "f4.in\n")
test.must_match('f5.out', "f5.in\n")
test.must_match('f6.out', "f6.in\n")
test.must_match('Move-f6.out', "f6.in-Move\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
