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
Verify that the Touch() Action works.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
Execute(Touch('f1'))
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
Cat = Action(cat)
env = Environment()
env.Command('f2.out', 'f2.in', [Cat, Touch("f3")])
env = Environment(FILE='f4')
env.Command('f5.out', 'f5.in', [Touch("$FILE"), Cat])
env.Command('f6.out', 'f6.in', [Cat,
                                Touch("Touch-$SOURCE"),
                                Touch("$TARGET-Touch")])
""")

test.write('f1', "f1\n")
test.write('f2.in', "f2.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

oldtime = os.path.getmtime(test.workpath('f1'))

expect = test.wrap_stdout(read_str = 'Touch("f1")\n',
                          build_str = """\
cat(["f2.out"], ["f2.in"])
Touch("f3")
Touch("f4")
cat(["f5.out"], ["f5.in"])
cat(["f6.out"], ["f6.in"])
Touch("Touch-f6.in")
Touch("f6.out-Touch")
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.sleep(2)

newtime = os.path.getmtime(test.workpath('f1'))
test.fail_test(oldtime != newtime)

test.must_not_exist(test.workpath('f2.out'))
test.must_not_exist(test.workpath('f3'))
test.must_not_exist(test.workpath('f4'))
test.must_not_exist(test.workpath('f5.out'))
test.must_not_exist(test.workpath('f6.out'))
test.must_not_exist(test.workpath('Touch-f6.in'))
test.must_not_exist(test.workpath('f6.out-Touch'))

test.run()

newtime = os.path.getmtime(test.workpath('f1'))
test.fail_test(oldtime == newtime)

test.must_match('f2.out', "f2.in\n")
test.must_exist(test.workpath('f3'))
test.must_exist(test.workpath('f4'))
test.must_match('f5.out', "f5.in\n")
test.must_match('f6.out', "f6.in\n")
test.must_exist(test.workpath('Touch-f6.in'))
test.must_exist(test.workpath('f6.out-Touch'))

test.pass_test()
