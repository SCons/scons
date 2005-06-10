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
Test transparent checkouts from SCCS files in an SCCS subdirectory.
"""

import string

import TestSCons

test = TestSCons.TestSCons()

sccs = test.where_is('sccs')
if not sccs:
    print "Could not find SCCS, skipping test(s)."
    test.pass_test(1)



test.subdir('SCCS', 'sub', ['sub', 'SCCS'])

for f in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(f, "%%F%% %s\n" % f)
    args = "create %s" % f
    test.run(program = sccs, arguments = args, stderr = None)
    test.unlink(f)
    test.unlink(','+f)

test.write(['sub', 'SConscript'], """\
# %%F%%
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "create SConscript"
test.run(chdir = 'sub', program = sccs, arguments = args, stderr = None)
test.unlink(['sub', 'SConscript'])
test.unlink(['sub', ',SConscript'])

for f in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['sub', f], "%%F%% sub/%s\n" % f)
    args = "create %s" % f
    test.run(chdir = 'sub', program = sccs, arguments = args, stderr = None)
    test.unlink(['sub', f])
    test.unlink(['sub', ','+f])

test.write(['SConstruct'], """
DefaultEnvironment()['SCCSCOM'] = 'cd ${TARGET.dir} && $SCCS get ${TARGET.file}'
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  SCCSFLAGS='-k')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
SConscript('sub/SConscript', "env")
""")

test.write(['bbb.in'], "checked-out bbb.in\n")

test.write(['sub', 'eee.in'], "checked-out sub/eee.in\n")

test.run(arguments = '.', stderr = None)

lines = string.split("""
sccs get SConscript
sccs get aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
sccs get ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
sccs get ddd.in
cat(["sub/ddd.out"], ["sub/ddd.in"])
cat(["sub/eee.out"], ["sub/eee.in"])
sccs get fff.in
cat(["sub/fff.out"], ["sub/fff.in"])
cat(["sub/all"], ["sub/ddd.out", "sub/eee.out", "sub/fff.out"])
""", '\n')

stdout = test.stdout()
missing = filter(lambda l, s=stdout: string.find(s, l) == -1, lines)
if missing:
    print "Missing the following output lines:"
    print string.join(missing, '\n')
    print "Actual STDOUT =========="
    print stdout
    test.fail_test(1)

test.must_match('all', """\
s.aaa.in aaa.in
checked-out bbb.in
s.ccc.in ccc.in
""")

test.must_not_be_writable(test.workpath('sub', 'SConscript'))
test.must_not_be_writable(test.workpath('aaa.in'))
test.must_not_be_writable(test.workpath('ccc.in'))
test.must_not_be_writable(test.workpath('sub', 'ddd.in'))
test.must_not_be_writable(test.workpath('sub', 'fff.in'))



test.pass_test()
