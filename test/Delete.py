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
Verify that the Delete() Action works.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
Execute(Delete('f1'))
Execute(Delete('d2'))
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
Cat = Action(cat)
env = Environment()
env.Command('f3.out', 'f3.in', [Cat, Delete("f4"), Delete("d5")])
env = Environment(FILE='f6', DIR='d7')
env.Command('f8.out', 'f8.in', [Delete("$FILE"), Delete("$DIR"), Cat])
env.Command('f9.out', 'f9.in', [Cat,
                                Delete("Delete-$SOURCE"),
                                Delete("$TARGET-Delete")])
""")

test.write('f1', "f1\n")
test.subdir('d2')
test.write(['d2', 'file'], "d2/file\n")
test.write('f3.in', "f3.in\n")
test.write('f4', "f4\n")
test.subdir('d5')
test.write(['d5', 'file'], "d5/file\n")
test.write('f6', "f6\n")
test.subdir('d7')
test.write(['d7', 'file'], "d7/file\n")
test.write('f8.in', "f8.in\n")
test.write('f9.in', "f9.in\n")
test.write('Delete-f9.in', "Delete-f9.in\n")
test.write('f9.out-Delete', "f9.out-Delete\n")

expect = test.wrap_stdout(read_str = """\
Delete("f1")
Delete("d2")
""",
                          build_str = """\
cat(["f3.out"], ["f3.in"])
Delete("f4")
Delete("d5")
Delete("f6")
Delete("d7")
cat(["f8.out"], ["f8.in"])
cat(["f9.out"], ["f9.in"])
Delete("Delete-f9.in")
Delete("f9.out-Delete")
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.must_exist('f1')
test.must_exist('d2')
test.must_exist(os.path.join('d2', 'file'))
test.must_not_exist('f3.out')
test.must_exist('f4')
test.must_exist('d5')
test.must_exist(os.path.join('d5', 'file'))
test.must_exist('f6')
test.must_exist('d7')
test.must_exist(os.path.join('d7', 'file'))
test.must_not_exist('f8.out')
test.must_not_exist('f9.out')
test.must_exist('Delete-f9.in')
test.must_exist('f9.out-Delete')

test.run()

test.must_not_exist('f1')
test.must_not_exist('d2')
test.must_not_exist(os.path.join('d2', 'file'))
test.must_match('f3.out', "f3.in\n")
test.must_not_exist('f4')
test.must_not_exist('d5')
test.must_not_exist(os.path.join('d5', 'file'))
test.must_not_exist('f6')
test.must_not_exist('d7')
test.must_not_exist(os.path.join('d7', 'file'))
test.must_match('f8.out', "f8.in\n")
test.must_match('f9.out', "f9.in\n")
test.must_not_exist('Delete-f9.in')
test.must_not_exist('f9.out-Delete')

test.pass_test()
