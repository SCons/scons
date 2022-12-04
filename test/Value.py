#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

import re

import TestSCons
import TestCmd

_python_ = TestSCons._python_

test = TestSCons.TestSCons(match=TestCmd.match_re)

python = TestSCons.python

SConstruct_content = """
Decider(r'%(source_signature)s')

class Custom:
    def __init__(self, value):  self.value = value
    def __str__(self):          return "C=" + str(self.value)

P = ARGUMENTS.get('prefix', '/usr/local')
L = len(P)
C = Custom(P)

def create(target, source, env):
    with open(str(target[0]), 'wb') as f:
        f.write(source[0].get_contents())

DefaultEnvironment(tools=[])  # test speedup
env = Environment()
env['BUILDERS']['B'] = Builder(action = create)
env['BUILDERS']['S'] = Builder(action = r'%(_python_)s put.py $SOURCES into $TARGET')
env.B('f1.out', Value(P))
env.B('f2.out', env.Value(L))
env.B('f3.out', Value(C))
env.S('f4.out', Value(L))

def create_value (target, source, env):
    target[0].write(source[0].get_contents())

def create_value_file (target, source, env):
    with open(str(target[0]), 'wb') as f:
        f.write(source[0].read())

env['BUILDERS']['B2'] = Builder(action = create_value)
env['BUILDERS']['B3'] = Builder(action = create_value_file)

V = Value('my value')
env.B2(V, 'f3.out')
env.B3('f5.out', V)
"""

test.write('put.py', """\
import os
import sys
with open(sys.argv[-1],'w') as f:
    f.write(" ".join(sys.argv[1:-2]))
""")

# Run all of the tests with both types of source signature
# to make sure there's no difference in behavior.
for source_signature in ['MD5', 'timestamp-newer']:

    print("Testing Value node with source signatures:", source_signature)

    test.write('SConstruct', SConstruct_content % locals())

    test.run(arguments='-c')
    test.run()

    out7 = """create_value(['my value'], ["f3.out"])"""
    out8 = """create_value_file(["f5.out"], ['my value'])"""

    out1 = """create(["f1.out"], ['/usr/local'])"""
    out2 = """create(["f2.out"], [10])"""
    out3 = """create\\(\\["f3.out"\\], \\[<.*.Custom (instance|object) at """
    #" <- unconfuses emacs syntax highlighting

    test.must_contain_all_lines(test.stdout(), [out1, out2, out7, out8])
    #print test.stdout()
    test.fail_test(re.search(out3, test.stdout()) is None)

    test.must_match('f1.out', "/usr/local")
    test.must_match('f2.out', "10")
    test.must_match('f3.out', "C=/usr/local")
    test.must_match('f4.out', '10')
    test.must_match('f5.out', "C=/usr/local")

    test.up_to_date(arguments='.')

    test.run(options='prefix=/usr')
    out4 = """create(["f1.out"], ['/usr'])"""
    out5 = """create(["f2.out"], [4])"""
    out6 = """create\\(\\["f3.out"\\], \\[<.*.Custom (instance|object) at """
    #" <- unconfuses emacs syntax highlighting
    test.must_contain_all_lines(test.stdout(), [out4, out5])
    test.fail_test(re.search(out6, test.stdout()) is None)

    test.must_match('f1.out', "/usr")
    test.must_match('f2.out', "4")
    test.must_match('f3.out', "C=/usr")
    test.must_match('f4.out', '4')

    test.up_to_date(options='prefix=/usr', arguments='.')

    test.unlink('f3.out')

    test.run(options='prefix=/var')
    out4 = """create(["f1.out"], ['/var'])"""

    test.must_contain_all_lines(test.stdout(), [out4, out7, out8])
    test.must_not_contain_any_line(test.stdout(), [out5])
    test.fail_test(re.search(out6, test.stdout()) is None)

    test.up_to_date(options='prefix=/var', arguments='.')

    test.must_match('f1.out', "/var")
    test.must_match('f2.out', "4")
    test.must_match('f3.out', "C=/var")
    test.must_match('f4.out', "4")
    test.must_match('f5.out', "C=/var")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
