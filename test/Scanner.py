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

import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
input = open(sys.argv[1], 'rb')
output = open(sys.argv[2], 'wb')

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            process(open(file, 'rb'), outfp)
        else:
            outfp.write(line)

process(input, output)

sys.exit(0)
""")

# Execute a subsidiary SConscript just to make sure we can
# get at the Scanner keyword from there.

test.write('SConstruct', """
SConscript('SConscript')
""")

test.write('SConscript', """
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def kfile_scan(node, env, target, arg):
    contents = node.get_contents()
    includes = include_re.findall(contents)
    return includes

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'])
scanners = Environment().Dictionary('SCANNERS')
env = Environment(SCANNERS = scanners + [kscan])

env.Command('foo', 'foo.k', r'%s build.py $SOURCES $TARGET')

bar_in = File('bar.in')
env.Command('bar', bar_in, r'%s build.py $SOURCES  $TARGET')
bar_in.source_scanner = kscan
""" % (python, python))

test.write('foo.k', 
"""foo.k 1 line 1
include xxx
include yyy
foo.k 1 line 4
""")

test.write('bar.in', 
"""include yyy
bar.in 1 line 2
bar.in 1 line 3
include zzz
""")

test.write('xxx', "xxx 1\n")

test.write('yyy', "yyy 1\n")

test.write('zzz', "zzz 1\n")

test.run(arguments = '.')

test.fail_test(test.read('foo') != "foo.k 1 line 1\nxxx 1\nyyy 1\nfoo.k 1 line 4\n")

test.fail_test(test.read('bar') != "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")

test.up_to_date(arguments = '.')

test.write('xxx', "xxx 2\n")

test.run(arguments = '.')

test.fail_test(test.read('foo') != "foo.k 1 line 1\nxxx 2\nyyy 1\nfoo.k 1 line 4\n")

test.fail_test(test.read('bar') != "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")

test.write('yyy', "yyy 2\n")

test.run(arguments = '.')

test.fail_test(test.read('foo') != "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n")

test.fail_test(test.read('bar') != "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")

test.write('zzz', "zzz 2\n")

test.run(arguments = '.')

test.fail_test(test.read('foo') != "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n")

test.fail_test(test.read('bar') != "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 2\n")

test.up_to_date(arguments = 'foo')

test.pass_test()
