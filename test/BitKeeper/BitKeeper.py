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
Test fetching source files from BitKeeper.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

bk = test.where_is('bk')
if not bk:
    print "Could not find BitKeeper, skipping test(s)."
    test.pass_test(1)

try:
    login = os.getlogin()
except (AttributeError, OSError):
    try:
        login = os.environ['USER']
    except KeyError:
        login = 'USER'

host = os.uname()[1]

email = "%s@%s" % (login, host)

test.subdir('BK', 'import', ['import', 'sub'])

# Test using BitKeeper to fetch from SCCS/s.file files.
sccs = test.where_is('sccs')
if not sccs:
    print "Could not find SCCS, skipping sub-test of BitKeeper using SCCS files."
else:
    test.subdir('work1',
                ['work1', 'SCCS'],
                ['work1', 'sub'],
                ['work1', 'sub', 'SCCS'])
    
    for file in ['aaa.in', 'bbb.in', 'ccc.in']:
        test.write(['work1', file], "work1/%s\n" % file)
        args = "create %s" % file
        test.run(chdir = 'work1', program = sccs, arguments = args, stderr = None)
        test.unlink(['work1', file])
        test.unlink(['work1', ','+file])
    
    test.write(['work1', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
    args = "create SConscript"
    test.run(chdir = 'work1/sub', program = sccs, arguments = args, stderr = None)
    test.unlink(['work1', 'sub', 'SConscript'])
    test.unlink(['work1', 'sub', ',SConscript'])
    
    for file in ['ddd.in', 'eee.in', 'fff.in']:
        test.write(['work1', 'sub', file], "work1/sub/%s\n" % file)
        args = "create %s" % file
        test.run(chdir = 'work1/sub', program = sccs, arguments = args, stderr = None)
        test.unlink(['work1', 'sub', file])
        test.unlink(['work1', 'sub', ','+file])

    test.write(['work1', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  BITKEEPERGETFLAGS='-e')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.BitKeeper())
SConscript('sub/SConscript', "env")
""")

    test.write(['work1', 'bbb.in'], "checked-out work1/bbb.in\n")

    test.write(['work1', 'sub', 'eee.in'], "checked-out work1/sub/eee.in\n")

    test.run(chdir = 'work1',
             arguments = '.',
             stdout = test.wrap_stdout(read_str = """\
bk get -e sub/SConscript
""",
                                       build_str = """\
bk get -e aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
bk get -e ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
bk get -e sub/ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
bk get -e sub/fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""),
             stderr = """\
sub/SConscript 1.1 -> 1.2: 5 lines
aaa.in 1.1 -> 1.2: 1 lines
ccc.in 1.1 -> 1.2: 1 lines
sub/ddd.in 1.1 -> 1.2: 1 lines
sub/fff.in 1.1 -> 1.2: 1 lines
""")

    test.must_match(['work1', 'all'], "work1/aaa.in\nchecked-out work1/bbb.in\nwork1/ccc.in\n")

    test.must_be_writable(test.workpath('work1', 'sub', 'SConscript'))
    test.must_be_writable(test.workpath('work1', 'aaa.in'))
    test.must_be_writable(test.workpath('work1', 'ccc.in'))
    test.must_be_writable(test.workpath('work1', 'sub', 'ddd.in'))
    test.must_be_writable(test.workpath('work1', 'sub', 'fff.in'))

# Test using BitKeeper to fetch from RCS/file,v files.
rcs = test.where_is('rcs')
ci = test.where_is('ci')
if not rcs:
    print "Could not find RCS,\nskipping sub-test of BitKeeper using RCS files."
elif not ci:
    print "Could not find the RCS ci command,\nskipping sub-test of BitKeeper using RCS files."
else:
    test.subdir('work2',
                ['work2', 'RCS'],
                ['work2', 'sub'],
                ['work2', 'sub', 'RCS'])

    for file in ['aaa.in', 'bbb.in', 'ccc.in']:
        test.write(['work2', file], "work2/%s\n" % file)
        args = "-f -t%s %s" % (file, file)
        test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

    test.write(['work2', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
    args = "-f -tsub/SConscript sub/SConscript"
    test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

    for file in ['ddd.in', 'eee.in', 'fff.in']:
        test.write(['work2', 'sub', file], "work2/sub/%s\n" % file)
        args = "-f -tsub/%s sub/%s" % (file, file)
        test.run(chdir = 'work2', program = ci, arguments = args, stderr = None)

    test.no_result(os.path.exists(test.workpath('work2', 'aaa.in')))
    test.no_result(os.path.exists(test.workpath('work2', 'bbb.in')))
    test.no_result(os.path.exists(test.workpath('work2', 'ccc.in')))

    test.no_result(os.path.exists(test.workpath('work2', 'sub', 'SConscript')))

    test.no_result(os.path.exists(test.workpath('work2', 'sub', 'ddd.in')))
    test.no_result(os.path.exists(test.workpath('work2', 'sub', 'eee.in')))
    test.no_result(os.path.exists(test.workpath('work2', 'sub', 'fff.in')))

    test.write(['work2', 'SConstruct'], """\
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  BITKEEPERGET='$BITKEEPER co',
                  BITKEEPERGETFLAGS='-q')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.BitKeeper())
SConscript('sub/SConscript', "env")
""")

    test.write(['work2', 'bbb.in'], "checked-out work2/bbb.in\n")

    test.write(['work2', 'sub', 'eee.in'], "checked-out work2/sub/eee.in\n")

    test.run(chdir = 'work2',
             arguments = '.',
             stdout = test.wrap_stdout(read_str = """\
bk co -q sub/SConscript
""",
                                       build_str = """\
bk co -q aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
bk co -q ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
bk co -q sub/ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
bk co -q sub/fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
"""))

    test.must_match(['work2', 'all'], "work2/aaa.in\nchecked-out work2/bbb.in\nwork2/ccc.in\n")

    test.must_match(['work2', 'sub', 'all'], "work2/sub/ddd.in\nchecked-out work2/sub/eee.in\nwork2/sub/fff.in\n")

    test.must_not_be_writable(test.workpath('work2', 'sub', 'SConscript'))
    test.must_not_be_writable(test.workpath('work2', 'aaa.in'))
    test.must_not_be_writable(test.workpath('work2', 'ccc.in'))
    test.must_not_be_writable(test.workpath('work2', 'sub', 'ddd.in'))
    test.must_not_be_writable(test.workpath('work2', 'sub', 'fff.in'))

# Set up a "pure" BitKeeper hierarchy.
# BitKeeper's licensing restrictions require a configuration file that
# specifies you're not using it multi-user.  This seems to be the
# minimal configuration that satisfies these requirements.
test.write('bk.conf', """\
description:test project 'foo'
logging:none
email:%s
single_user:%s
single_host:%s
""" % (email, login, host))

# Plus, we need to set the external environment variable that gets it to
# shut up and not prompt us to accept the license.
os.environ['BK_LICENSE'] = 'ACCEPTED'

test.write(['import', 'aaa.in'], "import/aaa.in\n")
test.write(['import', 'bbb.in'], "import/bbb.in\n")
test.write(['import', 'ccc.in'], "import/ccc.in\n")

test.write(['import', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")

test.write(['import', 'sub', 'ddd.in'], "import/sub/ddd.in\n")
test.write(['import', 'sub', 'eee.in'], "import/sub/eee.in\n")
test.write(['import', 'sub', 'fff.in'], "import/sub/fff.in\n")

# Test transparent source file checkouts using BitKeeper, by overriding
# the 'SCCS' construction variable in the default Environment.
work3 = test.workpath('work3')

test.run(program = bk,
         arguments = 'setup -f -c bk.conf work3')

test.run(chdir = 'import',
         program = bk,
         arguments = 'import -q -f -tplain . %s' % test.workpath('work3'))

test.write(['work3', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
DefaultEnvironment(tools=['SCCS'])['SCCS'] = r'%s'
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
SConscript('sub/SConscript', "env")
""" % bk)

test.write(['work3', 'bbb.in'], "work3/bbb.in\n")

test.subdir(['work3', 'sub'])
test.write(['work3', 'sub', 'eee.in'], "work3/sub/eee.in\n")

test.run(chdir = 'work3',
         arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
%s get sub/SConscript
""" % bk,
                                   build_str = """\
%s get aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
%s get ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
%s get sub/ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
%s get sub/fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
""" % (bk, bk, bk, bk)),
         stderr = """\
sub/SConscript 1.1: 5 lines
aaa.in 1.1: 1 lines
ccc.in 1.1: 1 lines
sub/ddd.in 1.1: 1 lines
sub/fff.in 1.1: 1 lines
""")

test.must_match(['work3', 'all'], "import/aaa.in\nwork3/bbb.in\nimport/ccc.in\n")

test.must_match(['work3', 'sub', 'all'], "import/sub/ddd.in\nwork3/sub/eee.in\nimport/sub/fff.in\n")

test.must_not_be_writable(test.workpath('work3', 'sub', 'SConscript'))
test.must_not_be_writable(test.workpath('work3', 'aaa.in'))
test.must_not_be_writable(test.workpath('work3', 'ccc.in'))
test.must_not_be_writable(test.workpath('work3', 'sub', 'ddd.in'))
test.must_not_be_writable(test.workpath('work3', 'sub', 'fff.in'))

test.pass_test()
