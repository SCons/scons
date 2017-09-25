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
Verify that Scanners are called just once.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', r"""
import os.path

def scan(node, env, envkey, arg):
    print('XScanner: node = '+ os.path.split(str(node))[1])
    return []

def exists_check(node, env):
    return os.path.exists(str(node))

XScanner = Scanner(name = 'XScanner',
                   function = scan,
                   argument = None,
                   scan_check = exists_check,
                   skeys = ['.x'])

def echo(env, target, source):
    t = os.path.split(str(target[0]))[1]
    s = os.path.split(str(source[0]))[1]
    print('create %s from %s' % (t, s))

Echo = Builder(action = Action(echo, None),
               src_suffix = '.x',
               suffix = '.x')

env = Environment(BUILDERS = {'Echo':Echo}, SCANNERS = [XScanner])

f1 = env.Echo(source=['file1'], target=['file2'])
f2 = env.Echo(source=['file2'], target=['file3'])
f3 = env.Echo(source=['file3'], target=['file4'])
""")

test.write('file1.x', 'file1.x\n')

test.run(stdout = test.wrap_stdout("""\
XScanner: node = file1.x
create file2.x from file1.x
create file3.x from file2.x
create file4.x from file3.x
"""))

test.write('file2.x', 'file2.x\n')

test.run(stdout = test.wrap_stdout("""\
XScanner: node = file1.x
XScanner: node = file2.x
create file3.x from file2.x
create file4.x from file3.x
"""))

test.write('file3.x', 'file3.x\n')

test.run(stdout = test.wrap_stdout("""\
XScanner: node = file1.x
XScanner: node = file2.x
XScanner: node = file3.x
create file4.x from file3.x
"""))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
