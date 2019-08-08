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
Verify that use of the FindPathDirs() function (actually a class)
can be used to specify a path_function of a scanner.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('inc1', 'inc2')

test.write('build.py', r"""
import os.path
import sys
path = sys.argv[1].split()

def find_file(f):
    for dir in path:
        p = dir + os.sep + f
        if os.path.exists(p):
            return open(p, 'r')
    return None

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            with find_file(file) as f:
                process(f, outfp)
        else:
            outfp.write(line)

with open(sys.argv[2], 'r') as ifp, open(sys.argv[3], 'w') as ofp:
    process(ifp, ofp)

sys.exit(0)
""")

# Execute a subsidiary SConscript just to make sure we can
# get at the Scanner keyword from there.

test.write('SConstruct', """\
SConscript('SConscript')
""")

test.write('SConscript', r"""
import os.path
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def kfile_scan(node, env, path, arg):
    contents = node.get_text_contents()
    includes = include_re.findall(contents)
    if includes == []:
         return []
    results = []
    for inc in includes:
        for dir in path:
            file = str(dir) + os.sep + inc
            if os.path.exists(file):
                results.append(file)
                break
    return results

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'],
                path_function = FindPathDirs('KPATH'))

##########################################################
# Test scanner as found automatically from the environment
# (backup_source_scanner)

env = Environment(KPATH=['inc1', 'inc2'])
env.Append(SCANNERS = kscan)

env.Command('foo', 'foo.k', r'%(_python_)s build.py "$KPATH" $SOURCES $TARGET')
""" % locals())



test.write('foo.k',
"""foo.k 1 line 1
include xxx
include yyy
foo.k 1 line 4
""")

test.write(['inc1', 'xxx'], "inc1/xxx 1\n")
test.write(['inc2', 'yyy'], "inc2/yyy 1\n")




test.run()

test.must_match('foo', "foo.k 1 line 1\ninc1/xxx 1\ninc2/yyy 1\nfoo.k 1 line 4\n", mode='r')

test.up_to_date(arguments = '.')



test.write(['inc1', 'xxx'], "inc1/xxx 2\n")

test.run()

test.must_match('foo', "foo.k 1 line 1\ninc1/xxx 2\ninc2/yyy 1\nfoo.k 1 line 4\n", mode='r')



test.write(['inc1', 'yyy'], "inc1/yyy 2\n")

test.run()

test.must_match('foo', "foo.k 1 line 1\ninc1/xxx 2\ninc1/yyy 2\nfoo.k 1 line 4\n", mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
