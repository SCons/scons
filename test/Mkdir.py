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
Verify that the Mkdir() Action works.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
Execute(Mkdir('d1'))
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
Cat = Action(cat)
env = Environment()
env.Command('f2.out', 'f2.in', [Cat, Mkdir("d3")])
env = Environment(DIR = 'd4')
env.Command('f5.out', 'f5.in', [Mkdir("$DIR"), Cat])
env.Command('f6.out', 'f6.in', [Cat,
                                Mkdir("Mkdir-$SOURCE"),
                                Mkdir("$TARGET-Mkdir")])
""")

test.write('f2.in', "f2.in\n")
test.write('f5.in', "f5.in\n")
test.write('f6.in', "f6.in\n")

expect = test.wrap_stdout(read_str = 'Mkdir("d1")\n',
                          build_str = """\
cat(["f2.out"], ["f2.in"])
Mkdir("d3")
Mkdir("d4")
cat(["f5.out"], ["f5.in"])
cat(["f6.out"], ["f6.in"])
Mkdir("Mkdir-f6.in")
Mkdir("f6.out-Mkdir")
""")
test.run(options = '-n', arguments = '.', stdout = expect)

test.must_not_exist('d1')
test.must_not_exist('f2.out')
test.must_not_exist('d3')
test.must_not_exist('d4')
test.must_not_exist('f5.out')
test.must_not_exist('f6.out')
test.must_not_exist('Mkdir-f6.in')
test.must_not_exist('f6.out-Mkdir')

test.run()

test.must_exist('d1')
test.must_match('f2.out', "f2.in\n")
test.must_exist('d3')
test.must_exist('d4')
test.must_match('f5.out', "f5.in\n")
test.must_exist('f6.out')
test.must_exist('Mkdir-f6.in')
test.must_exist('f6.out-Mkdir')

test.write(['d1', 'file'], "d1/file\n")
test.write(['d3', 'file'], "d3/file\n")
test.write(['Mkdir-f6.in', 'file'], "Mkdir-f6.in/file\n")
test.write(['f6.out-Mkdir', 'file'], "f6.out-Mkdir/file\n")

test.pass_test()
