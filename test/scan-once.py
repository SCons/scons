#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', r"""
import os.path

def scan(node, env, target, arg):
    print 'scanning',node,'for',target
    return []

def exists_check(node):
    return os.path.exists(str(node))

PScanner = Scanner(name = 'PScanner',
                   function = scan,
                   argument = None,
                   scan_check = exists_check,
		   skeys = ['.s'])

def echo(env, target, source):
    print 'create %s from %s' % (str(target[0]), str(source[0]))

Echo = Builder(action = echo,
               src_suffix = '.s',
	       suffix = '.s')

env = Environment(BUILDERS = {'Echo':Echo}, SCANNERS = [PScanner])

f1 = env.Echo(source=['file1'], target=['file2'])
f2 = env.Echo(source=['file2'], target=['file3'])
f3 = env.Echo(source=['file3'], target=['file4'])

Default(f3)
""")

test.write('file1.s', 'file1.s\n')

test.run(arguments = '.',
         stdout = test.wrap_stdout("""scanning file1.s for file2.s
echo("file2.s", "file1.s")
create file2.s from file1.s
scanning file1.s for file2.s
echo("file3.s", "file2.s")
create file3.s from file2.s
echo("file4.s", "file3.s")
create file4.s from file3.s
"""))

test.write('file2.s', 'file2.s\n')

test.run(arguments = '.',
         stdout = test.wrap_stdout("""scanning file1.s for file2.s
scanning file2.s for file3.s
echo("file3.s", "file2.s")
create file3.s from file2.s
scanning file2.s for file3.s
echo("file4.s", "file3.s")
create file4.s from file3.s
"""))

test.write('file3.s', 'file3.s\n')

test.run(arguments = '.',
         stdout = test.wrap_stdout("""scanning file1.s for file2.s
scanning file2.s for file3.s
scanning file3.s for file4.s
echo("file4.s", "file3.s")
create file4.s from file3.s
"""))

test.pass_test()
