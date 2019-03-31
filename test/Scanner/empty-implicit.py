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
Verify that Scanners are not called if a previous --implicit-cache
run stored an empty list of implicit dependencies.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', r"""
import os.path

def scan(node, env, envkey, arg):
    print('XScanner: node = '+os.path.split(str(node))[1])
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
    with open(t, 'wb') as ofb, open(s, 'rb') as ifb:
        ofb.write(ifb.read())

Echo = Builder(action = Action(echo, None),
               src_suffix = '.x',
               suffix = '.x')

env = Environment(BUILDERS = {'Echo':Echo}, SCANNERS = [XScanner])

f1 = env.Echo(source=['f1_in'], target=['f1_out'])
""")

test.write('f1_in.x', 'f1_in.x\n')

expect = test.wrap_stdout("""\
XScanner: node = f1_in.x
create f1_out.x from f1_in.x
""")

test.run(arguments = '--implicit-cache .', stdout = expect)

# Run it again, and the output must contain only the "up to date" message,
# *not* the line printed by the XScanner function.

test.up_to_date(options = '--implicit-cache', arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
