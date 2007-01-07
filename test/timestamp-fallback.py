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

import imp
import os
import os.path

import TestSCons

test = TestSCons.TestSCons()

try:
    file, name, desc = imp.find_module('md5')
except ImportError:
    pass
else:
    if desc[2] == imp.C_BUILTIN:
        msg = "The 'md5' module is built in to this version of Python.\n" + \
              "Cannot test falling back to timestamps.\n"
        test.skip_test(msg)

test.write('md5.py', r"""
raise ImportError
""")

os.environ['PYTHONPATH'] = test.workpath('.')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
def build(env, target, source):
    open(str(target[0]), 'wt').write(open(str(source[0]), 'rt').read())
B = Builder(action = build)
env = Environment(tools = [], BUILDERS = { 'B' : B })
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
env.B(target = 'f3.out', source = 'f3.in')
env.B(target = 'f4.out', source = 'f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

test.run(arguments = 'f1.out f3.out')

test.run(arguments = 'f1.out f2.out f3.out f4.out',
         stdout = test.wrap_stdout("""\
scons: `f1.out' is up to date.
build(["f2.out"], ["f2.in"])
scons: `f3.out' is up to date.
build(["f4.out"], ["f4.in"])
"""))

os.utime(test.workpath('f1.in'), 
         (os.path.getatime(test.workpath('f1.in')),
          os.path.getmtime(test.workpath('f1.in'))+10))
os.utime(test.workpath('f3.in'), 
         (os.path.getatime(test.workpath('f3.in')),
          os.path.getmtime(test.workpath('f3.in'))+10))

test.run(arguments = 'f1.out f2.out f3.out f4.out',
         stdout = test.wrap_stdout("""\
build(["f1.out"], ["f1.in"])
scons: `f2.out' is up to date.
build(["f3.out"], ["f3.in"])
scons: `f4.out' is up to date.
"""))


test.pass_test()

