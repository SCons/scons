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

import os.path
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('work1', ['work1', 'src'], ['work1', 'src', 'subdir'],
            'work2', ['work2', 'src'], ['work2', 'src', 'subdir'],
            'work3', ['work3', 'src'], ['work3', 'src', 'subdir'],
            'work4', ['work4', 'src'], ['work4', 'src', 'subdir'])

subdir_file6 = os.path.join('subdir', 'file6')
subdir_file6_in = os.path.join('subdir', 'file6.in')
cat_py = test.workpath('cat.py')

test.write(cat_py, r"""
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

SConstruct_contents = """\
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

cat = Builder(action = r"%s %s $TARGET $SOURCES")

env = Environment()
env.Append(BUILDERS = {'Cat':cat},
           SCANNERS = kscan)

Export("env")
SConscript('SConscript')
env.Install('../inc', 'aaa')
env.InstallAs('../inc/bbb.k', 'bbb.k')
env.Install('../inc', 'ddd')
env.InstallAs('../inc/eee', 'eee.in')
""" % (python, cat_py)

args = '--debug=explain .'

#############################################################################
test.write(['work1', 'src', 'SConstruct'], SConstruct_contents)

test.write(['work1', 'src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r"%s %s $TARGET - $SOURCES")
env.Cat('file5', 'file5.k')
env.Cat('subdir/file6', 'subdir/file6.in')
""" % (python, cat_py))

test.write(['work1', 'src', 'aaa'], "aaa 1\n")
test.write(['work1', 'src', 'bbb.k'], """\
bbb.k 1
include ccc
include ../inc/ddd
include ../inc/eee
""")
test.write(['work1', 'src', 'ccc'], "ccc 1\n")
test.write(['work1', 'src', 'ddd'], "ddd 1\n")
test.write(['work1', 'src', 'eee.in'], "eee.in 1\n")

test.write(['work1', 'src', 'file1.in'], "file1.in 1\n")

test.write(['work1', 'src', 'file2.k'], """\
file2.k 1 line 1
include xxx
include yyy
file2.k 1 line 4
""")

test.write(['work1', 'src', 'file4.in'], "file4.in 1\n")

test.write(['work1', 'src', 'xxx'], "xxx 1\n")
test.write(['work1', 'src', 'yyy'], "yyy 1\n")
test.write(['work1', 'src', 'zzz'], "zzz 1\n")

test.write(['work1', 'src', 'file5.k'], """\
file5.k 1 line 1
include ../inc/aaa
include ../inc/bbb.k
file5.k 1 line 4
""")

test.write(['work1', 'src', 'subdir', 'file6.in'], "subdir/file6.in 1\n")

#
test.run(chdir='work1/src', arguments=args, stdout=test.wrap_stdout("""\
scons: building `file1' because it doesn't exist
%s %s file1 file1.in
scons: building `file2' because it doesn't exist
%s %s file2 file2.k
scons: building `file3' because it doesn't exist
%s %s file3 xxx yyy zzz
scons: building `file4' because it doesn't exist
%s %s file4 - file4.in
scons: building `%s' because it doesn't exist
Install file: "aaa" as "%s"
scons: building `%s' because it doesn't exist
Install file: "ddd" as "%s"
scons: building `%s' because it doesn't exist
Install file: "eee.in" as "%s"
scons: building `%s' because it doesn't exist
Install file: "bbb.k" as "%s"
scons: building `file5' because it doesn't exist
%s %s file5 file5.k
scons: building `%s' because it doesn't exist
%s %s %s %s
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work1', 'inc', 'aaa'),
       test.workpath('work1', 'inc', 'aaa'),
       test.workpath('work1', 'inc', 'ddd'),
       test.workpath('work1', 'inc', 'ddd'),
       test.workpath('work1', 'inc', 'eee'),
       test.workpath('work1', 'inc', 'eee'),
       test.workpath('work1', 'inc', 'bbb.k'),
       test.workpath('work1', 'inc', 'bbb.k'),
       python, cat_py,
       subdir_file6,
       python, cat_py, subdir_file6, subdir_file6_in)))

test.must_match(['work1', 'src', 'file1'], "file1.in 1\n")
test.must_match(['work1', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""")
test.must_match(['work1', 'src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n")
test.must_match(['work1', 'src', 'file4'], "file4.in 1\n")
test.must_match(['work1', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""")

#
test.write(['work1', 'src', 'file1.in'], "file1.in 2\n")
test.write(['work1', 'src', 'yyy'], "yyy 2\n")
test.write(['work1', 'src', 'zzz'], "zzz 2\n")
test.write(['work1', 'src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test.run(chdir='work1/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%s %s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%s %s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%s %s file3 xxx yyy zzz
scons: rebuilding `%s' because:
           `%s' is no longer a dependency
           `%s' is no longer a dependency
           `bbb.k' changed
Install file: "bbb.k" as "%s"
scons: rebuilding `file5' because `%s' changed
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work1', 'inc', 'bbb.k'),
       test.workpath('work1', 'inc', 'ddd'),
       test.workpath('work1', 'inc', 'eee'),
       test.workpath('work1', 'inc', 'bbb.k'),
       test.workpath('work1', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work1', 'src', 'file1'], "file1.in 2\n")
test.must_match(['work1', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 2
file2.k 1 line 4
""")
test.must_match(['work1', 'src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n")
test.must_match(['work1', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 2
ccc 1
file5.k 1 line 4
""")

#
test.write(['work1', 'src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy'])
""")

test.run(chdir='work1/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is no longer a dependency
%s %s file3 xxx yyy
""" % (python, cat_py)))

test.must_match(['work1', 'src', 'file3'], "xxx 1\nyyy 2\n")

#
test.write(['work1', 'src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
""")

test.run(chdir='work1/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is a new dependency
%s %s file3 xxx yyy zzz
""" % (python, cat_py)))

test.must_match(['work1', 'src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n")

#
test.write(['work1', 'src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['zzz', 'yyy', 'xxx'])
""")

test.run(chdir='work1/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file3' because the dependency order changed:
               old: ['xxx', 'yyy', 'zzz']
               new: ['zzz', 'yyy', 'xxx']
%s %s file3 zzz yyy xxx
""" % (python, cat_py)))

test.must_match(['work1', 'src', 'file3'], "zzz 2\nyyy 2\nxxx 1\n")

#
test.write(['work1', 'src', 'SConscript'], """\
Import("env")
env.Command('file4', 'file4.in', r"%s %s $TARGET $SOURCES")
""" % (python, cat_py))

test.run(chdir='work1/src',arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file4' because the build action changed:
               old: %s %s $TARGET - $SOURCES
               new: %s %s $TARGET $SOURCES
%s %s file4 file4.in
""" % (python, cat_py,
       python, cat_py,
       python, cat_py)))

test.must_match(['work1', 'src', 'file4'], "file4.in 1\n")

test.up_to_date(chdir='work1/src',arguments='.')

# Test the transition when you turn ON SConsignFile().
# This will (or might) rebuild things, but we don't care what,
# we just want to make sure we don't blow up.
test.write(['work1', 'src', 'SConstruct'],
           "SConsignFile()\n" + SConstruct_contents)

test.run(chdir='work1/src', arguments=args)

test.up_to_date(chdir='work1/src',arguments='.')

#############################################################################
# Now test (in a separate workspace) how things function when
# we tell SCons to not save the --debug=explain info
# using SetOption('save_explain_info').
test.write(['work2', 'src', 'SConstruct'],
           "SetOption('save_explain_info', 0)\n" + SConstruct_contents)

test.write(['work2', 'src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r"%s %s $TARGET - $SOURCES")
env.Cat('file5', 'file5.k')
env.Cat('subdir/file6', 'subdir/file6.in')
""" % (python, cat_py))

test.write(['work2', 'src', 'aaa'], "aaa 1\n")
test.write(['work2', 'src', 'bbb.k'], """\
bbb.k 1
include ccc
include ../inc/ddd
include ../inc/eee
""")
test.write(['work2', 'src', 'ccc'], "ccc 1\n")
test.write(['work2', 'src', 'ddd'], "ddd 1\n")
test.write(['work2', 'src', 'eee.in'], "eee.in 1\n")

test.write(['work2', 'src', 'file1.in'], "file1.in 1\n")

test.write(['work2', 'src', 'file2.k'], """\
file2.k 1 line 1
include xxx
include yyy
file2.k 1 line 4
""")

test.write(['work2', 'src', 'file4.in'], "file4.in 1\n")

test.write(['work2', 'src', 'xxx'], "xxx 1\n")
test.write(['work2', 'src', 'yyy'], "yyy 1\n")
test.write(['work2', 'src', 'zzz'], "zzz 1\n")

test.write(['work2', 'src', 'file5.k'], """\
file5.k 1 line 1
include ../inc/aaa
include ../inc/bbb.k
file5.k 1 line 4
""")

test.write(['work2', 'src', 'subdir', 'file6.in'], "subdir/file6.in 1\n")

# First, even without build info, we can tell the user that things
# are being built because they don't exist.
test.run(chdir='work2/src', arguments=args, stdout=test.wrap_stdout("""\
scons: building `file1' because it doesn't exist
%s %s file1 file1.in
scons: building `file2' because it doesn't exist
%s %s file2 file2.k
scons: building `file3' because it doesn't exist
%s %s file3 xxx yyy zzz
scons: building `file4' because it doesn't exist
%s %s file4 - file4.in
scons: building `%s' because it doesn't exist
Install file: "aaa" as "%s"
scons: building `%s' because it doesn't exist
Install file: "ddd" as "%s"
scons: building `%s' because it doesn't exist
Install file: "eee.in" as "%s"
scons: building `%s' because it doesn't exist
Install file: "bbb.k" as "%s"
scons: building `file5' because it doesn't exist
%s %s file5 file5.k
scons: building `%s' because it doesn't exist
%s %s %s %s
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work2', 'inc', 'aaa'),
       test.workpath('work2', 'inc', 'aaa'),
       test.workpath('work2', 'inc', 'ddd'),
       test.workpath('work2', 'inc', 'ddd'),
       test.workpath('work2', 'inc', 'eee'),
       test.workpath('work2', 'inc', 'eee'),
       test.workpath('work2', 'inc', 'bbb.k'),
       test.workpath('work2', 'inc', 'bbb.k'),
       python, cat_py,
       subdir_file6,
       python, cat_py, subdir_file6, subdir_file6_in)))

test.must_match(['work2', 'src', 'file1'], "file1.in 1\n")
test.must_match(['work2', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""")
test.must_match(['work2', 'src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n")
test.must_match(['work2', 'src', 'file4'], "file4.in 1\n")
test.must_match(['work2', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""")

# Using --debug=explain above will have actually saved the build info;
# run again to clear it out.
test.write(['work2', 'src', 'file1.in'], "file1.in 2\n")
test.write(['work2', 'src', 'yyy'], "yyy 2\n")
test.write(['work2', 'src', 'zzz'], "zzz 2\n")
test.write(['work2', 'src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test.run(chdir='work2/src', arguments='.')

# Now, it should tell us that it can't explain why the files are
# being rebuilt.  It should also *store* the build info because
# we're using --debug=explain...
test.write(['work2', 'src', 'file1.in'], "file1.in 3\n")
test.write(['work2', 'src', 'yyy'], "yyy 3\n")
test.write(['work2', 'src', 'zzz'], "zzz 3\n")
test.write(['work2', 'src', 'bbb.k'], "bbb.k 3\ninclude ccc\n")

test.run(chdir='work2/src', arguments=args, stdout=test.wrap_stdout("""\
scons: Cannot explain why `file1' is being rebuilt: No previous build information found
%s %s file1 file1.in
scons: Cannot explain why `file2' is being rebuilt: No previous build information found
%s %s file2 file2.k
scons: Cannot explain why `file3' is being rebuilt: No previous build information found
%s %s file3 xxx yyy zzz
scons: Cannot explain why `%s' is being rebuilt: No previous build information found
Install file: "bbb.k" as "%s"
scons: Cannot explain why `file5' is being rebuilt: No previous build information found
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work2', 'inc', 'bbb.k'),
       test.workpath('work2', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work2', 'src', 'file1'], "file1.in 3\n")
test.must_match(['work2', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 3
file2.k 1 line 4
""")
test.must_match(['work2', 'src', 'file3'], "xxx 1\nyyy 3\nzzz 3\n")
test.must_match(['work2', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 3
ccc 1
file5.k 1 line 4
""")

# ...so if we now update the files again, it should be able to tell
# us why the files changed.
test.write(['work2', 'src', 'file1.in'], "file1.in 4\n")
test.write(['work2', 'src', 'yyy'], "yyy 4\n")
test.write(['work2', 'src', 'zzz'], "zzz 4\n")
test.write(['work2', 'src', 'bbb.k'], "bbb.k 4\ninclude ccc\n")

test.run(chdir='work2/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%s %s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%s %s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%s %s file3 xxx yyy zzz
scons: rebuilding `%s' because `bbb.k' changed
Install file: "bbb.k" as "%s"
scons: rebuilding `file5' because `%s' changed
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work2', 'inc', 'bbb.k'),
       test.workpath('work2', 'inc', 'bbb.k'),
       test.workpath('work2', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work2', 'src', 'file1'], "file1.in 4\n")
test.must_match(['work2', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 4
file2.k 1 line 4
""")
test.must_match(['work2', 'src', 'file3'], "xxx 1\nyyy 4\nzzz 4\n")
test.must_match(['work2', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 4
ccc 1
file5.k 1 line 4
""")

#############################################################################
# Now test (in a separate workspace) how things function when
# we tell SCons to not save the --debug=explain info
# using --save-explain-info=0'.
test.write(['work3', 'src', 'SConstruct'], SConstruct_contents)

test.write(['work3', 'src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r"%s %s $TARGET - $SOURCES")
env.Cat('file5', 'file5.k')
env.Cat('subdir/file6', 'subdir/file6.in')
""" % (python, cat_py))

test.write(['work3', 'src', 'aaa'], "aaa 1\n")
test.write(['work3', 'src', 'bbb.k'], """\
bbb.k 1
include ccc
include ../inc/ddd
include ../inc/eee
""")
test.write(['work3', 'src', 'ccc'], "ccc 1\n")
test.write(['work3', 'src', 'ddd'], "ddd 1\n")
test.write(['work3', 'src', 'eee.in'], "eee.in 1\n")

test.write(['work3', 'src', 'file1.in'], "file1.in 1\n")

test.write(['work3', 'src', 'file2.k'], """\
file2.k 1 line 1
include xxx
include yyy
file2.k 1 line 4
""")

test.write(['work3', 'src', 'file4.in'], "file4.in 1\n")

test.write(['work3', 'src', 'xxx'], "xxx 1\n")
test.write(['work3', 'src', 'yyy'], "yyy 1\n")
test.write(['work3', 'src', 'zzz'], "zzz 1\n")

test.write(['work3', 'src', 'file5.k'], """\
file5.k 1 line 1
include ../inc/aaa
include ../inc/bbb.k
file5.k 1 line 4
""")

test.write(['work3', 'src', 'subdir', 'file6.in'], "subdir/file6.in 1\n")

# First, even without build info and regardless of storage option,
# we can tell the user that things are being built because they don't exist.
test.run(chdir='work3/src',
         arguments='--debug=explain --save-explain-info=0 .',
         stdout=test.wrap_stdout("""\
scons: building `file1' because it doesn't exist
%s %s file1 file1.in
scons: building `file2' because it doesn't exist
%s %s file2 file2.k
scons: building `file3' because it doesn't exist
%s %s file3 xxx yyy zzz
scons: building `file4' because it doesn't exist
%s %s file4 - file4.in
scons: building `%s' because it doesn't exist
Install file: "aaa" as "%s"
scons: building `%s' because it doesn't exist
Install file: "ddd" as "%s"
scons: building `%s' because it doesn't exist
Install file: "eee.in" as "%s"
scons: building `%s' because it doesn't exist
Install file: "bbb.k" as "%s"
scons: building `file5' because it doesn't exist
%s %s file5 file5.k
scons: building `%s' because it doesn't exist
%s %s %s %s
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work3', 'inc', 'aaa'),
       test.workpath('work3', 'inc', 'aaa'),
       test.workpath('work3', 'inc', 'ddd'),
       test.workpath('work3', 'inc', 'ddd'),
       test.workpath('work3', 'inc', 'eee'),
       test.workpath('work3', 'inc', 'eee'),
       test.workpath('work3', 'inc', 'bbb.k'),
       test.workpath('work3', 'inc', 'bbb.k'),
       python, cat_py,
       subdir_file6,
       python, cat_py, subdir_file6, subdir_file6_in)))

test.must_match(['work3', 'src', 'file1'], "file1.in 1\n")
test.must_match(['work3', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""")
test.must_match(['work3', 'src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n")
test.must_match(['work3', 'src', 'file4'], "file4.in 1\n")
test.must_match(['work3', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""")

# Using --debug=explain above will have actually saved the build info;
# run again to clear it out.
test.write(['work3', 'src', 'file1.in'], "file1.in 2\n")
test.write(['work3', 'src', 'yyy'], "yyy 2\n")
test.write(['work3', 'src', 'zzz'], "zzz 2\n")
test.write(['work3', 'src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test.run(chdir='work3/src', arguments='--save-explain-info=0 .')

# Now, it should tell us that it can't explain why the files are
# being rebuilt.  It should also *store* the build info because
# we're using --debug=explain...
test.write(['work3', 'src', 'file1.in'], "file1.in 3\n")
test.write(['work3', 'src', 'yyy'], "yyy 3\n")
test.write(['work3', 'src', 'zzz'], "zzz 3\n")
test.write(['work3', 'src', 'bbb.k'], "bbb.k 3\ninclude ccc\n")

test.run(chdir='work3/src',
         arguments='--debug=explain .',
         stdout=test.wrap_stdout("""\
scons: Cannot explain why `file1' is being rebuilt: No previous build information found
%s %s file1 file1.in
scons: Cannot explain why `file2' is being rebuilt: No previous build information found
%s %s file2 file2.k
scons: Cannot explain why `file3' is being rebuilt: No previous build information found
%s %s file3 xxx yyy zzz
scons: Cannot explain why `%s' is being rebuilt: No previous build information found
Install file: "bbb.k" as "%s"
scons: Cannot explain why `file5' is being rebuilt: No previous build information found
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work3', 'inc', 'bbb.k'),
       test.workpath('work3', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work3', 'src', 'file1'], "file1.in 3\n")
test.must_match(['work3', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 3
file2.k 1 line 4
""")
test.must_match(['work3', 'src', 'file3'], "xxx 1\nyyy 3\nzzz 3\n")
test.must_match(['work3', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 3
ccc 1
file5.k 1 line 4
""")

# ...so if we now update the files again, it should be able to tell
# us why the files changed.
test.write(['work3', 'src', 'file1.in'], "file1.in 4\n")
test.write(['work3', 'src', 'yyy'], "yyy 4\n")
test.write(['work3', 'src', 'zzz'], "zzz 4\n")
test.write(['work3', 'src', 'bbb.k'], "bbb.k 4\ninclude ccc\n")

test.run(chdir='work3/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%s %s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%s %s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%s %s file3 xxx yyy zzz
scons: rebuilding `%s' because `bbb.k' changed
Install file: "bbb.k" as "%s"
scons: rebuilding `file5' because `%s' changed
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work3', 'inc', 'bbb.k'),
       test.workpath('work3', 'inc', 'bbb.k'),
       test.workpath('work3', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work3', 'src', 'file1'], "file1.in 4\n")
test.must_match(['work3', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 4
file2.k 1 line 4
""")
test.must_match(['work3', 'src', 'file3'], "xxx 1\nyyy 4\nzzz 4\n")
test.must_match(['work3', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 4
ccc 1
file5.k 1 line 4
""")

#############################################################################
# Test that the --debug=explain information gets saved by default.
test.write(['work4', 'src', 'SConstruct'], SConstruct_contents)

test.write(['work4', 'src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in', r"%s %s $TARGET - $SOURCES")
env.Cat('file5', 'file5.k')
env.Cat('subdir/file6', 'subdir/file6.in')
""" % (python, cat_py))

test.write(['work4', 'src', 'aaa'], "aaa 1\n")
test.write(['work4', 'src', 'bbb.k'], """\
bbb.k 1
include ccc
include ../inc/ddd
include ../inc/eee
""")
test.write(['work4', 'src', 'ccc'], "ccc 1\n")
test.write(['work4', 'src', 'ddd'], "ddd 1\n")
test.write(['work4', 'src', 'eee.in'], "eee.in 1\n")

test.write(['work4', 'src', 'file1.in'], "file1.in 1\n")

test.write(['work4', 'src', 'file2.k'], """\
file2.k 1 line 1
include xxx
include yyy
file2.k 1 line 4
""")

test.write(['work4', 'src', 'file4.in'], "file4.in 1\n")

test.write(['work4', 'src', 'xxx'], "xxx 1\n")
test.write(['work4', 'src', 'yyy'], "yyy 1\n")
test.write(['work4', 'src', 'zzz'], "zzz 1\n")

test.write(['work4', 'src', 'file5.k'], """\
file5.k 1 line 1
include ../inc/aaa
include ../inc/bbb.k
file5.k 1 line 4
""")

test.write(['work4', 'src', 'subdir', 'file6.in'], "subdir/file6.in 1\n")

#
test.run(chdir='work4/src', arguments='.')

test.must_match(['work4', 'src', 'file1'], "file1.in 1\n")
test.must_match(['work4', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 1
file2.k 1 line 4
""")
test.must_match(['work4', 'src', 'file3'], "xxx 1\nyyy 1\nzzz 1\n")
test.must_match(['work4', 'src', 'file4'], "file4.in 1\n")
test.must_match(['work4', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 1
ccc 1
ddd 1
eee.in 1
file5.k 1 line 4
""")

#
test.write(['work4', 'src', 'file1.in'], "file1.in 2\n")
test.write(['work4', 'src', 'yyy'], "yyy 2\n")
test.write(['work4', 'src', 'zzz'], "zzz 2\n")
test.write(['work4', 'src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test.run(chdir='work4/src', arguments=args, stdout=test.wrap_stdout("""\
scons: rebuilding `file1' because `file1.in' changed
%s %s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%s %s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%s %s file3 xxx yyy zzz
scons: rebuilding `%s' because:
           `%s' is no longer a dependency
           `%s' is no longer a dependency
           `bbb.k' changed
Install file: "bbb.k" as "%s"
scons: rebuilding `file5' because `%s' changed
%s %s file5 file5.k
""" % (python, cat_py,
       python, cat_py,
       python, cat_py,
       test.workpath('work4', 'inc', 'bbb.k'),
       test.workpath('work4', 'inc', 'ddd'),
       test.workpath('work4', 'inc', 'eee'),
       test.workpath('work4', 'inc', 'bbb.k'),
       test.workpath('work4', 'inc', 'bbb.k'),
       python, cat_py)))

test.must_match(['work4', 'src', 'file1'], "file1.in 2\n")
test.must_match(['work4', 'src', 'file2'], """\
file2.k 1 line 1
xxx 1
yyy 2
file2.k 1 line 4
""")
test.must_match(['work4', 'src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n")
test.must_match(['work4', 'src', 'file5'], """\
file5.k 1 line 1
aaa 1
bbb.k 2
ccc 1
file5.k 1 line 4
""")

test.pass_test()
