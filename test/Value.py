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

import os
import re
import string
import sys
import TestSCons
import TestCmd

test = TestSCons.TestSCons(match=TestCmd.match_re)

test.write('SConstruct', """
class Custom:
    def __init__(self, value):  self.value = value
    def __str__(self):          return "C=" + str(self.value)

P = ARGUMENTS.get('prefix', '/usr/local')
L = len(P)
C = Custom(P)

def create(target, source, env):
    open(str(target[0]), 'wb').write(source[0].get_contents())

env = Environment()
env['BUILDERS']['B'] = Builder(action = create)
env.B('f1.out', Value(P))
env.B('f2.out', Value(L))
env.B('f3.out', Value(C))
""")


test.run()
out1 = """create("f1.out", "'/usr/local'")"""
out2 = """create("f2.out", "10")"""
out3 = """create\\("f3.out", "<.*.Custom instance at """
test.fail_test(string.find(test.stdout(), out1) == -1)
test.fail_test(string.find(test.stdout(), out2) == -1)
test.fail_test(re.search(out3, test.stdout()) == None)

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(open(test.workpath('f1.out'), 'rb').read() != '/usr/local')
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(open(test.workpath('f2.out'), 'rb').read() != '10')
test.fail_test(not os.path.exists(test.workpath('f3.out')))
test.fail_test(open(test.workpath('f3.out'), 'rb').read() != 'C=/usr/local')

test.up_to_date(arguments = ".")

test.run(arguments = 'prefix=/usr')
out4 = """create("f1.out", "'/usr'")"""
out5 = """create("f2.out", "4")"""
out6 = """create\\("f3.out", "<.*.Custom instance at """
test.fail_test(string.find(test.stdout(), out4) == -1)
test.fail_test(string.find(test.stdout(), out5) == -1)
test.fail_test(re.search(out6, test.stdout()) == None)

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(open(test.workpath('f1.out'), 'rb').read() != '/usr')
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(open(test.workpath('f2.out'), 'rb').read() != '4')
test.fail_test(not os.path.exists(test.workpath('f3.out')))
test.fail_test(open(test.workpath('f3.out'), 'rb').read() != 'C=/usr')

test.unlink('f3.out')

test.run(arguments = 'prefix=/var')
out4 = """create("f1.out", "'/var'")"""
test.fail_test(string.find(test.stdout(), out4) == -1)
test.fail_test(string.find(test.stdout(), out5) != -1)
test.fail_test(re.search(out6, test.stdout()) == None)

test.fail_test(not os.path.exists(test.workpath('f1.out')))
test.fail_test(open(test.workpath('f1.out'), 'rb').read() != '/var')
test.fail_test(not os.path.exists(test.workpath('f2.out')))
test.fail_test(open(test.workpath('f2.out'), 'rb').read() != '4')
test.fail_test(not os.path.exists(test.workpath('f3.out')))
test.fail_test(open(test.workpath('f3.out'), 'rb').read() != 'C=/var')

test.pass_test()
