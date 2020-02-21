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
Verify a lot of the basic operation of the --debug=explain option.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir(['src'], ['src', 'subdir'])

python = TestSCons.python
_python_ = TestSCons._python_

subdir_file7 = os.path.join('subdir', 'file7')
subdir_file7_in = os.path.join('subdir', 'file7.in')
subdir_file8 = os.path.join('subdir', 'file8')
subdir_file9 = os.path.join('subdir', 'file9')

cat_py = test.workpath('cat.py')
inc_aaa = test.workpath('inc', 'aaa')
inc_ddd = test.workpath('inc', 'ddd')
inc_eee = test.workpath('inc', 'eee')
inc_bbb_k = test.workpath('inc', 'bbb.k')



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


SConstruct_contents = r"""
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

cat = Builder(action = [[r'%(python)s', r'%(cat_py)s', '$TARGET', '$SOURCES']])
one_cat = Builder( action = [[r'%(python)s', r'%(cat_py)s', '$TARGET', '${SOURCES[0]}']])

env = Environment(tools=[])
env.Append(BUILDERS = {'Cat':cat, 'OneCat':one_cat},
           SCANNERS = kscan)
env.PrependENVPath('PATHEXT', '.PY')

Export("env")
SConscript('SConscript')
env.Install('../inc', 'aaa')
env.InstallAs('../inc/bbb.k', 'bbb.k')
env.Install('../inc', 'ddd')
env.InstallAs('../inc/eee', 'eee.in')
""" % locals()

test.write(['src', 'SConstruct'], SConstruct_contents)

def WriteInitialTest( valueDict ) :
    test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('file2', 'file2.k')
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
env.Command('file4', 'file4.in',
             r'%(_python_)s %(cat_py)s $TARGET $FILE4FLAG $SOURCES',
             FILE4FLAG='-')
env.Cat('file5', 'file5.k')
file6 = env.Cat('file6', 'file6.in')
AlwaysBuild(file6)
env.Cat('subdir/file7', 'subdir/file7.in')
env.OneCat('subdir/file8', ['subdir/file7.in', env.Value(%(test_value)s)] )
env.OneCat('subdir/file9', ['subdir/file7.in', env.Value(7)] )
""" % valueDict)

test_value = '"first"'
WriteInitialTest( locals() )

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

test.write(['src', 'file6.in'], "file6.in 1\n")

test.write(['src', 'subdir', 'file7.in'], "subdir/file7.in 1\n")


args = '--debug=explain ..'


expect = test.wrap_stdout("""\
scons: building `%(inc_aaa)s' because it doesn't exist
Install file: "aaa" as "%(inc_aaa)s"
scons: building `%(inc_bbb_k)s' because it doesn't exist
Install file: "bbb.k" as "%(inc_bbb_k)s"
scons: building `%(inc_ddd)s' because it doesn't exist
Install file: "ddd" as "%(inc_ddd)s"
scons: building `%(inc_eee)s' because it doesn't exist
Install file: "eee.in" as "%(inc_eee)s"
scons: building `file1' because it doesn't exist
%(_python_)s %(cat_py)s file1 file1.in
scons: building `file2' because it doesn't exist
%(_python_)s %(cat_py)s file2 file2.k
scons: building `file3' because it doesn't exist
%(_python_)s %(cat_py)s file3 xxx yyy zzz
scons: building `file4' because it doesn't exist
%(_python_)s %(cat_py)s file4 - file4.in
scons: building `file5' because it doesn't exist
%(_python_)s %(cat_py)s file5 file5.k
scons: building `file6' because it doesn't exist
%(_python_)s %(cat_py)s file6 file6.in
scons: building `%(subdir_file7)s' because it doesn't exist
%(_python_)s %(cat_py)s %(subdir_file7)s %(subdir_file7_in)s
scons: building `%(subdir_file8)s' because it doesn't exist
%(_python_)s %(cat_py)s %(subdir_file8)s %(subdir_file7_in)s
scons: building `%(subdir_file9)s' because it doesn't exist
%(_python_)s %(cat_py)s %(subdir_file9)s %(subdir_file7_in)s
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

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
test.must_match(['src', 'file6'], "file6.in 1\n", mode='r')



test.write(['src', 'file1.in'], "file1.in 2\n")
test.write(['src', 'yyy'], "yyy 2\n")
test.write(['src', 'zzz'], "zzz 2\n")
test.write(['src', 'bbb.k'], "bbb.k 2\ninclude ccc\n")

test_value = '"second"'
WriteInitialTest( locals() )

expect = test.wrap_stdout("""\
scons: rebuilding `%(inc_bbb_k)s' because `bbb.k' changed
Install file: "bbb.k" as "%(inc_bbb_k)s"
scons: rebuilding `file1' because `file1.in' changed
%(_python_)s %(cat_py)s file1 file1.in
scons: rebuilding `file2' because `yyy' changed
%(_python_)s %(cat_py)s file2 file2.k
scons: rebuilding `file3' because:
           `yyy' changed
           `zzz' changed
%(_python_)s %(cat_py)s file3 xxx yyy zzz
scons: rebuilding `file5' because `%(inc_bbb_k)s' changed
%(_python_)s %(cat_py)s file5 file5.k
scons: rebuilding `file6' because AlwaysBuild() is specified
%(_python_)s %(cat_py)s file6 file6.in
scons: rebuilding `%(subdir_file8)s' because:
           `first' is no longer a dependency
           `second' is a new dependency
%(_python_)s %(cat_py)s %(subdir_file8)s %(subdir_file7_in)s
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

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



test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy'])
""")

expect = test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is no longer a dependency
%(_python_)s %(cat_py)s file3 xxx yyy
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file3'], "xxx 1\nyyy 2\n", mode='r')



test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['xxx', 'yyy', 'zzz'])
""")

expect = test.wrap_stdout("""\
scons: rebuilding `file3' because `zzz' is a new dependency
%(_python_)s %(cat_py)s file3 xxx yyy zzz
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file3'], "xxx 1\nyyy 2\nzzz 2\n", mode='r')



test.write(['src', 'SConscript'], """\
Import("env")
env.Cat('file3', ['zzz', 'yyy', 'xxx'])
""")

python_sep = python.replace('\\', '\\\\')

expect = test.wrap_stdout("""\
scons: rebuilding `file3' because:
           the dependency order changed:
           ->Sources
           Old:xxx	New:zzz
           Old:yyy	New:yyy
           Old:zzz	New:xxx
           ->Depends
           ->Implicit
           Old:%(_python_)s	New:%(_python_)s
%(_python_)s %(cat_py)s file3 zzz yyy xxx
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file3'], "zzz 2\nyyy 2\nxxx 1\n", mode='r')



test.write(['src', 'SConscript'], """\
Import("env")
f3 = File('file3')
env.Cat(f3, ['zzz', 'yyy', 'xxx'])
env.AddPostAction(f3, r'%(_python_)s %(cat_py)s ${TARGET}.yyy $SOURCES yyy')
env.AddPreAction(f3, r'%(_python_)s %(cat_py)s ${TARGET}.alt $SOURCES')
""" % locals())

expect = test.wrap_stdout("""\
scons: rebuilding `file3' because the build action changed:
               old: %(python)s %(cat_py)s $TARGET $SOURCES
               new: %(_python_)s %(cat_py)s ${TARGET}.alt $SOURCES
                    %(python)s %(cat_py)s $TARGET $SOURCES
                    %(_python_)s %(cat_py)s ${TARGET}.yyy $SOURCES yyy
%(_python_)s %(cat_py)s file3.alt zzz yyy xxx
%(_python_)s %(cat_py)s file3 zzz yyy xxx
%(_python_)s %(cat_py)s file3.yyy zzz yyy xxx yyy
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file3'], "zzz 2\nyyy 2\nxxx 1\n", mode='r')
test.must_match(['src', 'file3.alt'], "zzz 2\nyyy 2\nxxx 1\n", mode='r')
test.must_match(['src', 'file3.yyy'], "zzz 2\nyyy 2\nxxx 1\nyyy 2\n", mode='r')



test.write(['src', 'SConscript'], """\
Import("env")
f3 = File('file3')
env.Cat(f3, ['zzz', 'yyy', 'xxx'])
env.AddPostAction(f3, r'%(_python_)s %(cat_py)s ${TARGET}.yyy $SOURCES xxx')
env.AddPreAction(f3, r'%(_python_)s %(cat_py)s ${TARGET}.alt $SOURCES')
""" % locals())

expect = test.wrap_stdout("""\
scons: rebuilding `file3' because the build action changed:
               old: %(_python_)s %(cat_py)s ${TARGET}.alt $SOURCES
                    %(python)s %(cat_py)s $TARGET $SOURCES
                    %(_python_)s %(cat_py)s ${TARGET}.yyy $SOURCES yyy
               new: %(_python_)s %(cat_py)s ${TARGET}.alt $SOURCES
                    %(python)s %(cat_py)s $TARGET $SOURCES
                    %(_python_)s %(cat_py)s ${TARGET}.yyy $SOURCES xxx
%(_python_)s %(cat_py)s file3.alt zzz yyy xxx
%(_python_)s %(cat_py)s file3 zzz yyy xxx
%(_python_)s %(cat_py)s file3.yyy zzz yyy xxx xxx
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src', arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file3'], "zzz 2\nyyy 2\nxxx 1\n", mode='r')
test.must_match(['src', 'file3.alt'], "zzz 2\nyyy 2\nxxx 1\n", mode='r')
test.must_match(['src', 'file3.yyy'], "zzz 2\nyyy 2\nxxx 1\nxxx 1\n", mode='r')



test.write(['src', 'SConscript'], """\
Import("env")
env.Command('file4', 'file4.in',
            r'%(_python_)s %(cat_py)s $TARGET $FILE4FLAG $SOURCES',
            FILE4FLAG='')
""" % locals())

expect = test.wrap_stdout("""\
scons: rebuilding `file4' because the contents of the build action changed
               action: %(_python_)s %(cat_py)s $TARGET $FILE4FLAG $SOURCES
%(_python_)s %(cat_py)s file4 file4.in
""" % locals())

test.set_match_function(TestSCons.match_caseinsensitive)
test.run(chdir='src',arguments=args, stdout=expect)
test.set_match_function(TestSCons.match_exact)

test.must_match(['src', 'file4'], "file4.in 1\n", mode='r')

test.up_to_date(chdir='src',arguments='.')



# Test the transition when you turn ON SConsignFile().
# This will (or might) rebuild things, but we don't care what,
# we just want to make sure we don't blow up.
test.write(['src', 'SConstruct'],
           "SConsignFile()\n" + SConstruct_contents)

test.run(chdir='src', arguments=args)

test.up_to_date(chdir='src',arguments='.')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
