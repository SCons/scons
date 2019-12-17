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
Execute(Touch(File('f1-File')))
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())
Cat = Action(cat)
env = Environment()
env.Command('f2.out', 'f2.in', [Cat, Touch("f3")])
env = Environment(FILE='f4')
env.Command('f5.out', 'f5.in', [Touch("$FILE"), Cat])
env.Command('f6.out', 'f6.in', [Cat,
                                Touch("Touch-$SOURCE"),
                                Touch("$TARGET-Touch")])

# Make sure Touch works with a list of arguments
env = Environment()
env.Command('f7.out', 'f7.in', [Cat,
                                Touch(["Touch-$SOURCE",
                                       "$TARGET-Touch",
                                       File("f8")])])
""")

test.write('f1', "f1\n")
test.write('f1-File', "f1-File\n")
test.write('f2.in', "f2.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")
test.write('f7.in', "f7.in\n")

old_f1_time = os.path.getmtime(test.workpath('f1'))
old_f1_File_time = os.path.getmtime(test.workpath('f1-File'))

expect = test.wrap_stdout(read_str = """\
Touch("f1")
Touch("f1-File")
""",
                          build_str = """\
cat(["f2.out"], ["f2.in"])
Touch("f3")
Touch("f4")
cat(["f5.out"], ["f5.in"])
cat(["f6.out"], ["f6.in"])
Touch("Touch-f6.in")
Touch("f6.out-Touch")
cat(["f7.out"], ["f7.in"])
Touch(["Touch-f7.in", "f7.out-Touch", "f8"])
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.sleep(2)

new_f1_time = os.path.getmtime(test.workpath('f1'))
test.fail_test(old_f1_time != new_f1_time)
new_f1_File_time = os.path.getmtime(test.workpath('f1-File'))
test.fail_test(old_f1_File_time != new_f1_File_time)

test.must_not_exist(test.workpath('f2.out'))
test.must_not_exist(test.workpath('f3'))
test.must_not_exist(test.workpath('f4'))
test.must_not_exist(test.workpath('f5.out'))
test.must_not_exist(test.workpath('f6.out'))
test.must_not_exist(test.workpath('Touch-f6.in'))
test.must_not_exist(test.workpath('f6.out-Touch'))
test.must_not_exist(test.workpath('f7.out'))
test.must_not_exist(test.workpath('Touch-f7.in'))
test.must_not_exist(test.workpath('f7.out-Touch'))
test.must_not_exist(test.workpath('f8'))

test.run()

new_f1_time = os.path.getmtime(test.workpath('f1'))
test.fail_test(old_f1_time == new_f1_time)
new_f1_File_time = os.path.getmtime(test.workpath('f1-File'))
test.fail_test(old_f1_File_time == new_f1_File_time)

test.must_match('f2.out', "f2.in\n")
test.must_exist(test.workpath('f3'))
test.must_exist(test.workpath('f4'))
test.must_match('f5.out', "f5.in\n")
test.must_match('f6.out', "f6.in\n")
test.must_exist(test.workpath('Touch-f6.in'))
test.must_exist(test.workpath('f6.out-Touch'))
test.must_match('f7.out', "f7.in\n")
test.must_exist(test.workpath('Touch-f7.in'))
test.must_exist(test.workpath('f7.out-Touch'))
test.must_exist(test.workpath('f8'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
