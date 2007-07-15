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
Execute(Copy('f1.out', 'f1.in'))
Execute(Copy('d2.out', 'd2.in'))
Execute(Copy('d3.out', 'f3.in'))
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
Cat = Action(cat)
env = Environment()
env.Command('bar.out', 'bar.in', [Cat,
                                  Copy("f4.out", "f4.in"),
                                  Copy("d5.out", "d5.in"),
                                  Copy("d6.out", "f6.in")])
env = Environment(OUTPUT = 'f7.out', INPUT = 'f7.in')
env.Command('f8.out', 'f8.in', [Copy('$OUTPUT', '$INPUT'), Cat])
env.Command('f9.out', 'f9.in', [Cat, Copy('${TARGET}-Copy', '$SOURCE')])

env.CopyTo( 'd4', 'f10.in' )
env.CopyAs( 'd4/f11.out', 'f11.in')
env.CopyAs( 'd4/f12.out', 'd5/f12.in')
""")

test.write('f1.in', "f1.in\n")
test.subdir('d2.in')
test.write(['d2.in', 'file'], "d2.in/file\n")
test.write('f3.in', "f3.in\n")
test.subdir('d3.out')
test.write('bar.in', "bar.in\n")
test.write('f4.in', "f4.in\n")
test.subdir('d5.in')
test.write(['d5.in', 'file'], "d5.in/file\n")
test.write('f6.in', "f6.in\n")
test.subdir('d6.out')
test.write('f7.in', "f7.in\n")
test.write('f8.in', "f8.in\n")
test.write('f9.in', "f9.in\n")
test.write('f10.in', "f10.in\n")
test.write('f11.in', "f11.in\n")
test.subdir('d5')
test.write(['d5', 'f12.in'], "f12.in\n")

expect = test.wrap_stdout(read_str = """\
Copy("f1.out", "f1.in")
Copy("d2.out", "d2.in")
Copy("d3.out", "f3.in")
""",
                          build_str = """\
cat(["bar.out"], ["bar.in"])
Copy("f4.out", "f4.in")
Copy("d5.out", "d5.in")
Copy("d6.out", "f6.in")
Copy file(s): "f10.in" to "d4/f10.in"
Copy file(s): "f11.in" to "d4/f11.out"
Copy file(s): "d5/f12.in" to "d4/f12.out"
Copy("f7.out", "f7.in")
cat(["f8.out"], ["f8.in"])
cat(["f9.out"], ["f9.in"])
Copy("f9.out-Copy", "f9.in")
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.must_not_exist('f1.out')
test.must_not_exist('d2.out')
test.must_not_exist(os.path.join('d3.out', 'f3.in'))
test.must_not_exist('f4.out')
test.must_not_exist('d5.out')
test.must_not_exist(os.path.join('d6.out', 'f6.in'))
test.must_not_exist('f7.out')
test.must_not_exist('f8.out')
test.must_not_exist('f9.out')
test.must_not_exist('f9.out-Copy')
test.must_not_exist('d4/f10.in')
test.must_not_exist('d4/f11.out')
test.must_not_exist('d4/f12.out')

test.run()

test.must_match('f1.out', "f1.in\n")
test.must_match(['d2.out', 'file'], "d2.in/file\n")
test.must_match(['d3.out', 'f3.in'], "f3.in\n")
test.must_match('f4.out', "f4.in\n")
test.must_match(['d5.out', 'file'], "d5.in/file\n")
test.must_match(['d6.out', 'f6.in'], "f6.in\n")
test.must_match('f7.out', "f7.in\n")
test.must_match('f8.out', "f8.in\n")
test.must_match('f9.out', "f9.in\n")
test.must_match('f9.out-Copy', "f9.in\n")
test.must_match('d4/f10.in', 'f10.in\n')
test.must_match('d4/f11.out', 'f11.in\n')
test.must_match('d4/f12.out', 'f12.in\n')

test.pass_test()
