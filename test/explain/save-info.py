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

"""
Verify that the --debug=explain information gets saved by default.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir( 'src', ['src', 'subdir'])

cat_py = test.workpath('cat.py')
inc_bbb_k = test.workpath('inc', 'bbb.k')
inc_ddd = test.workpath('inc', 'ddd')
inc_eee = test.workpath('inc', 'eee')

test.write(cat_py, r"""
import sys

def process(outfp, infp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            try:
                fp = open(file, 'r')
            except IOError:
                import os
                print("os.getcwd() =", os.getcwd())
                raise
            process(outfp, fp)
            fp.close()
        else:
            outfp.write(line)

with open(sys.argv[1], 'w') as ofp:
    for f in sys.argv[2:]:
        if f != '-':
            with open(f, 'r') as ifp:
                process(ofp, ifp)

sys.exit(0)
""")

test.write(['src', 'SConstruct'], r"""
DefaultEnvironment(tools=[])
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def kfile_scan(node, env, target, arg):
    contents = node.get_text_contents()
    includes = include_re.findall(contents)
    return includes

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'])

cat = Builder(action = r'%(_python_)s %(cat_py)s $TARGET $SOURCES')

env = Environment(tools=[])
env.Append(BUILDERS = {'Cat':cat},
           SCANNERS = kscan)

Export("env")
SConscript('SConscript')
env.Install('../inc', 'aaa')
env.InstallAs('../inc/bbb.k', 'bbb.k')
env.Install('../inc', 'ddd')
env.InstallAs('../inc/eee', 'eee.in')
""" % locals())

test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r'%(_python_)s %(cat_py)s $TARGET - $SOURCES')
env.Cat('file5', 'file5.k')
env.Cat('subdir/file6', 'subdir/file6.in')
""" % locals())

test.write(['src', 'aaa'], "aaa 1\n")
test.write(['src', 'bbb.k'], """\
bbb.k 1
include ccc
include ../inc/ddd
include ../inc/eee
""")
test.write(['src', 'ccc'], "ccc 1\n")
test.write(['src', 'ddd'], "ddd 1\n")
test.write(['src', 'eee.in'], "eee.in 1\n")

test.write(['src', 'file1.in'], "file1.in 1\n")

test.write(['src', 'file2.k'], """\
file2.k 1 line 1
include xxx
include yyy
file2.k 1 line 4
""")

test.write(['src', 'file4.in'], "file4.in 1\n")

test.write(['src', 'xxx'], "xxx 1\n")
test.write(['src', 'yyy'], "yyy 1\n")
test.write(['src', 'zzz'], "zzz 1\n")

test.write(['src', 'file5.k'], """\
file5.k 1 line 1
include ../inc/aaa
include ../inc/bbb.k
file5.k 1 line 4
""")

test.write(['src', 'subdir', 'file6.in'], "subdir/file6.in 1\n")

#
test.run(chdir='src', arguments='..')

test.must_match(['src', 'file1'], "file1.in 1\n", mode='r')
test.must_match(['src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""", mode='r')
test.must_match(['src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n", mode='r')
test.must_match(['src', 'file4'], "file4.in 1\n", mode='r')
test.must_match(['src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""", mode='r')

test.write(['src', 'file1.in'], "file1.in 2\n")
test.write(['src', 'yyy'], "yyy 2\n")
test.write(['src', 'zzz'], "zzz 2\n")
test.write(['src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

expect = test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%(_python_)s %(cat_py)s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%(_python_)s %(cat_py)s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%(_python_)s %(cat_py)s file3 xxx yyy zzz
scons: rebuilding `%(inc_bbb_k)s' because `bbb.k' changed
Install file: "bbb.k" as "%(inc_bbb_k)s"
scons: rebuilding `file5' because `%(inc_bbb_k)s' changed
%(_python_)s %(cat_py)s file5 file5.k
""" % locals())

test.run(chdir='src', arguments='--debug=explain .', stdout=expect)

test.must_match(['src', 'file1'], "file1.in 2\n", mode='r')
test.must_match(['src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 2
file2.k 1 line 4
""", mode='r')
test.must_match(['src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n", mode='r')
test.must_match(['src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 2
ccc 1
file5.k 1 line 4
""", mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
