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
Verify that a source_scanner that uses a dictionary to select more
specific scanners for source file suffixes works correctly, even
when it's handed a file suffix that it doesn't know how to scan
(i.e., for which it doesn't have a specific scanner in its dictionary).
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'w') as ofp:
    for infile in sys.argv[2:]:
        with open(infile, 'r') as ifp:
            include_prefix = 'include%s ' % infile[-1]

            def process(infp, outfp, include_prefix=include_prefix):
                for line in infp.readlines():
                    if line[:len(include_prefix)] == include_prefix:
                        file = line[len(include_prefix):-1]
                        with open(file, 'r') as f:
                            process(f, outfp)
                    else:
                        outfp.write(line)

            process(ifp, ofp)

sys.exit(0)
""")

# Execute a subsidiary SConscript just to make sure we can
# get at the Scanner keyword from there.

test.write('SConstruct', """
SConscript('SConscript')
""")

test.write('SConscript', r"""
import re

include1_re = re.compile(r'^include1\s+(\S+)$', re.M)
include2_re = re.compile(r'^include2\s+(\S+)$', re.M)
include3_re = re.compile(r'^include3\s+(\S+)$', re.M)

def k1_scan(node, env, scanpaths, arg=None):
    contents = node.get_text_contents()
    includes = include1_re.findall(contents)
    return includes

def k2_scan(node, env, scanpaths, arg=None):
    contents = node.get_text_contents()
    includes = include2_re.findall(contents)
    return includes

def k3_scan(node, env, scanpaths, arg=None):
    contents = node.get_text_contents()
    includes = include3_re.findall(contents)
    return includes

kscanner = Scanner({'.k1' : Scanner(k1_scan), '.k2': Scanner(k2_scan)})

b = Builder(action=r'%(_python_)s build.py $TARGET $SOURCES',
            source_scanner=kscanner)
env = Environment(BUILDERS={'Build':b})

kscanner.add_scanner('.k3', Scanner(k3_scan))

env.Build('aaa', 'aaa.k1')
env.Build('bbb', 'bbb.k2')
env.Build('ccc', 'ccc.k3')
env.Build('ddd', ['ddd.k4', 'aaa.k1', 'bbb.k2', 'ccc.k3'])
""" % locals())

test.write('aaa.k1',
"""aaa.k1 1
line 2
include1 xxx
include2 yyy
include3 zzz
line 6
""")

test.write('bbb.k2',
"""bbb.k2 1
line 2
include1 xxx
include2 yyy
include3 zzz
line 6
""")

test.write('ccc.k3',
"""ccc.k3 1
line 2
include1 xxx
include2 yyy
include3 zzz
line 6
""")

test.write('ddd.k4',
"""ddd.k4 1
line 2
line 3
""")

test.write('xxx', "xxx 1\n")
test.write('yyy', "yyy 1\n")
test.write('zzz', "zzz 1\n")




expect = test.wrap_stdout("""\
%(_python_)s build.py aaa aaa.k1
%(_python_)s build.py bbb bbb.k2
%(_python_)s build.py ccc ccc.k3
%(_python_)s build.py ddd ddd.k4 aaa.k1 bbb.k2 ccc.k3
""" % locals())

test.run(stdout=expect)

expect_aaa = 'aaa.k1 1\nline 2\nxxx 1\ninclude2 yyy\ninclude3 zzz\nline 6\n'
expect_bbb = 'bbb.k2 1\nline 2\ninclude1 xxx\nyyy 1\ninclude3 zzz\nline 6\n'
expect_ccc = 'ccc.k3 1\nline 2\ninclude1 xxx\ninclude2 yyy\nzzz 1\nline 6\n'
expect_ddd = 'ddd.k4 1\nline 2\nline 3\n' + expect_aaa + expect_bbb + expect_ccc

test.must_match('aaa', expect_aaa, mode='r')
test.must_match('bbb', expect_bbb, mode='r')
test.must_match('ccc', expect_ccc, mode='r')
test.must_match('ddd', expect_ddd, mode='r')

test.up_to_date(arguments = '.')



test.write('zzz', "zzz 2\n")

expect = test.wrap_stdout("""\
%(_python_)s build.py ccc ccc.k3
%(_python_)s build.py ddd ddd.k4 aaa.k1 bbb.k2 ccc.k3
""" % locals())

test.run(stdout=expect)

expect_ccc = 'ccc.k3 1\nline 2\ninclude1 xxx\ninclude2 yyy\nzzz 2\nline 6\n'
expect_ddd = 'ddd.k4 1\nline 2\nline 3\n' + expect_aaa + expect_bbb + expect_ccc

test.must_match('bbb', expect_bbb, mode='r')
test.must_match('ddd', expect_ddd, mode='r')



test.write('yyy', "yyy 2\n")

expect = test.wrap_stdout("""\
%(_python_)s build.py bbb bbb.k2
%(_python_)s build.py ddd ddd.k4 aaa.k1 bbb.k2 ccc.k3
""" % locals())

test.run(stdout=expect)

expect_bbb = 'bbb.k2 1\nline 2\ninclude1 xxx\nyyy 2\ninclude3 zzz\nline 6\n'
expect_ddd = 'ddd.k4 1\nline 2\nline 3\n' + expect_aaa + expect_bbb + expect_ccc

test.must_match('bbb', expect_bbb, mode='r')
test.must_match('ddd', expect_ddd, mode='r')



test.write('xxx', "xxx 2\n")

expect = test.wrap_stdout("""\
%(_python_)s build.py aaa aaa.k1
%(_python_)s build.py ddd ddd.k4 aaa.k1 bbb.k2 ccc.k3
""" % locals())

test.run(stdout=expect)

expect_aaa = 'aaa.k1 1\nline 2\nxxx 2\ninclude2 yyy\ninclude3 zzz\nline 6\n'
expect_ddd = 'ddd.k4 1\nline 2\nline 3\n' + expect_aaa + expect_bbb + expect_ccc

test.must_match('aaa', expect_aaa, mode='r')
test.must_match('ddd', expect_ddd, mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
