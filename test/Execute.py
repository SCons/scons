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
Test the Execute() function for executing actions directly.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('my_copy.py', """\
import sys
open(sys.argv[2], 'wb').write(open(sys.argv[1], 'rb').read())
try:
    exitval = int(sys.argv[3])
except IndexError:
    exitval = 0
sys.exit(exitval)
""")

test.write('SConstruct', """\
Execute("%s my_copy.py a.in a.out")
Execute(Action("%s my_copy.py b.in b.out"))
env = Environment(COPY = 'my_copy.py')
env.Execute("%s my_copy.py c.in c.out")
env.Execute(Action("%s my_copy.py d.in d.out"))
v = env.Execute("%s $COPY e.in e.out")
assert v == 0, v
v = env.Execute(Action("%s $COPY f.in f.out"))
assert v == 0, v
v = env.Execute("%s $COPY g.in g.out 1")
assert v == 1, v
v = env.Execute(Action("%s $COPY h.in h.out 2"))
assert v == 2, v
import shutil
Execute(lambda target, source, env: shutil.copy('i.in', 'i.out'))
Execute(Action(lambda target, source, env: shutil.copy('j.in', 'j.out')))
env.Execute(lambda target, source, env: shutil.copy('k.in', 'k.out'))
env.Execute(Action(lambda target, source, env: shutil.copy('l.in', 'l.out')))
""" % (python, python, python, python, python, python, python, python))

test.write('a.in', "a.in\n")
test.write('b.in', "b.in\n")
test.write('c.in', "c.in\n")
test.write('d.in', "d.in\n")
test.write('e.in', "e.in\n")
test.write('f.in', "f.in\n")
test.write('g.in', "g.in\n")
test.write('h.in', "h.in\n")
test.write('i.in', "i.in\n")
test.write('j.in', "j.in\n")
test.write('k.in', "k.in\n")
test.write('l.in', "l.in\n")

test.run(arguments = '.')

test.fail_test(test.read('a.out') != "a.in\n")
test.fail_test(test.read('b.out') != "b.in\n")
test.fail_test(test.read('c.out') != "c.in\n")
test.fail_test(test.read('d.out') != "d.in\n")
test.fail_test(test.read('e.out') != "e.in\n")
test.fail_test(test.read('f.out') != "f.in\n")
test.fail_test(test.read('g.out') != "g.in\n")
test.fail_test(test.read('h.out') != "h.in\n")
test.fail_test(test.read('i.out') != "i.in\n")
test.fail_test(test.read('j.out') != "j.in\n")
test.fail_test(test.read('k.out') != "k.in\n")
test.fail_test(test.read('l.out') != "l.in\n")

test.pass_test()
