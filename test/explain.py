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
Test the --debug=explain option.
"""

import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('src')

test.write(['src', 'cat.py'], r"""
import sys

def process(outfp, infp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            try:
                fp = open(file, 'rb')
            except IOError:
                import os
                print "os.getcwd() =", os.getcwd()
                raise
            process(outfp, fp)
        else:
            outfp.write(line)

outfp = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    if f != '-':
        process(outfp, open(f, 'rb'))

sys.exit(0)
""")

test.write(['src', 'SConstruct'], """
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

cat = Builder(action = r"%s cat.py $TARGET $SOURCES")

env = Environment()
env.Append(BUILDERS = {'Cat':cat},
           SCANNERS = kscan)

Export("env")
SConscript('SConscript')
env.Install('../inc', 'aaa')
env.InstallAs('../inc/bbb.k', 'bbb.k')
env.Install('../inc', 'ddd')
env.InstallAs('../inc/eee', 'eee.in')
""" % (python,))

test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r"%s cat.py $TARGET - $SOURCES")
env.Cat('file5', 'file5.k')
""" % (python,))

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

args = '--debug=explain .'

#
test.run(chdir='src', arguments=args, stdout=test.wrap_stdout("""\
scons: building `file1' because it doesn't exist
%s cat.py file1 file1.in
scons: building `file2' because it doesn't exist
%s cat.py file2 file2.k
scons: building `file3' because it doesn't exist
%s cat.py file3 xxx yyy zzz
scons: building `file4' because it doesn't exist
%s cat.py file4 - file4.in
scons: building `%s' because it doesn't exist
Install file: "aaa" as "%s"
scons: building `%s' because it doesn't exist
Install file: "ddd" as "%s"
scons: building `%s' because it doesn't exist
Install file: "eee.in" as "%s"
scons: building `%s' because it doesn't exist
Install file: "bbb.k" as "%s"
scons: building `file5' because it doesn't exist
%s cat.py file5 file5.k
""" % (python,
       python,
       python,
       python,
       test.workpath('inc', 'aaa'),
       test.workpath('inc', 'aaa'),
       test.workpath('inc', 'ddd'),
       test.workpath('inc', 'ddd'),
       test.workpath('inc', 'eee'),
       test.workpath('inc', 'eee'),
       test.workpath('inc', 'bbb.k'),
       test.workpath('inc', 'bbb.k'),
       python,)))

test.must_match(['src', 'file1'], "file1.in 1\n")
test.must_match(['src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""")
test.must_match(['src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n")
test.must_match(['src', 'file4'], "file4.in 1\n")
test.must_match(['src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""")

#
test.write(['src', 'file1.in'], "file1.in 2\n")
test.write(['src', 'yyy'], "yyy 2\n")
test.write(['src', 'zzz'], "zzz 2\n")
test.write(['src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test.run(chdir='src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%s cat.py file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%s cat.py file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%s cat.py file3 xxx yyy zzz
scons: rebuilding `%s' because:
           `%s' is no longer a dependency
           `%s' is no longer a dependency
           `bbb.k' changed
Install file: "bbb.k" as "%s"
scons: rebuilding `file5' because `%s' changed
%s cat.py file5 file5.k
""" % (python,
       python,
       python,
       test.workpath('inc', 'bbb.k'),
       test.workpath('inc', 'ddd'),
       test.workpath('inc', 'eee'),
       test.workpath('inc', 'bbb.k'),
       test.workpath('inc', 'bbb.k'),
       python)))

test.must_match(['src', 'file1'], "file1.in 2\n")
test.must_match(['src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 2
file2.k 1 line 4
""")
test.must_match(['src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n")
test.must_match(['src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 2
ccc 1
file5.k 1 line 4
""")

#
test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy'])
""")

test.run(chdir='src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is no longer a dependency
%s cat.py file3 xxx yyy
""" % (python,)))

test.must_match(['src', 'file3'], "xxx 1\nyyy 2\n")

#
test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
""")

test.run(chdir='src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is a new dependency
%s cat.py file3 xxx yyy zzz
""" % (python,)))

test.must_match(['src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n")

#
test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['zzz', 'yyy', 'xxx'])
""")

test.run(chdir='src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because the dependency order changed:
               old: ['xxx', 'yyy', 'zzz']
               new: ['zzz', 'yyy', 'xxx']
%s cat.py file3 zzz yyy xxx
""" % (python,)))

test.must_match(['src', 'file3'], "zzz 2\nyyy 2\nxxx 1\n")

#
test.write(['src', 'SConscript'], """\
Import("env")
env.Command('file4', 'file4.in', r"%s cat.py $TARGET $SOURCES")
""" % (python,))

test.run(chdir='src',arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file4' because the build action changed:
               old: %s cat.py $TARGET - $SOURCES
               new: %s cat.py $TARGET $SOURCES
%s cat.py file4 file4.in
""" % (python, python, python)))

test.must_match(['src', 'file4'], "file4.in 1\n")

test.pass_test()
