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
Test explicit checkouts from local RCS files.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

rcs = test.where_is('rcs')
if not rcs:
    test.skip_test("Could not find 'rcs'; skipping test(s).\n")

ci = test.where_is('ci')
if not ci:
    test.skip_test("Could not find `ci' command, skipping test(s).\n")



test.subdir('sub')

sub_RCS = os.path.join('sub', 'RCS')
sub_SConscript = os.path.join('sub', 'SConscript')
sub_all = os.path.join('sub', 'all')
sub_ddd_in = os.path.join('sub', 'ddd.in')
sub_ddd_out = os.path.join('sub', 'ddd.out')
sub_eee_in = os.path.join('sub', 'eee.in')
sub_eee_out = os.path.join('sub', 'eee.out')
sub_fff_in = os.path.join('sub', 'fff.in')
sub_fff_out = os.path.join('sub', 'fff.out')

for f in ['aaa.in', 'bbb.in', 'ccc.in']:
    test.write(f, "%s\n" % f)
    args = "-f -t%s %s" % (f, f)
    test.run(program = ci, arguments = args, stderr = None)

test.write(['sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")
args = "-f -tsub/SConscript sub/SConscript"
test.run(program = ci, arguments = args, stderr = None)

for f in ['ddd.in', 'eee.in', 'fff.in']:
    test.write(['sub', f], "sub/%s\n" % f)
    args = "-f -tsub/%s sub/%s" % (f, f)
    test.run(program = ci, arguments = args, stderr = None)

test.no_result(os.path.exists(test.workpath('aaa.in')))
test.no_result(os.path.exists(test.workpath('bbb.in')))
test.no_result(os.path.exists(test.workpath('ccc.in')))

test.no_result(os.path.exists(test.workpath('sub', 'SConscript')))

test.no_result(os.path.exists(test.workpath('sub', 'ddd.in')))
test.no_result(os.path.exists(test.workpath('sub', 'eee.in')))
test.no_result(os.path.exists(test.workpath('sub', 'fff.in')))

test.write('SConstruct', """
import os
for key in ['LOGNAME', 'USERNAME', 'USER']:
    logname = os.environ.get(key)
    if logname: break
ENV = {'PATH' : os.environ['PATH'],
       'LOGNAME' : logname}
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(ENV=ENV,
                  BUILDERS={'Cat':Builder(action=cat)},
                  RCS_COFLAGS='-q')
DefaultEnvironment()['ENV'] = ENV
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.RCS())
SConscript('sub/SConscript', "env")
""")

test.write('bbb.in', "checked-out bbb.in\n")

test.write(['sub', 'eee.in'], "checked-out sub/eee.in\n")

test.run(arguments = '.',
         stdout = test.wrap_stdout(read_str = """\
co -q %(sub_SConscript)s
""" % locals(),
                                   build_str = """\
co -q aaa.in
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
co -q ccc.in
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
co -q %(sub_ddd_in)s
cat(["%(sub_ddd_out)s"], ["%(sub_ddd_in)s"])
cat(["%(sub_eee_out)s"], ["%(sub_eee_in)s"])
co -q %(sub_fff_in)s
cat(["%(sub_fff_out)s"], ["%(sub_fff_in)s"])
cat(["%(sub_all)s"], ["%(sub_ddd_out)s", "%(sub_eee_out)s", "%(sub_fff_out)s"])
""" % locals()))

# Checking things back out of RCS apparently messes with the line
# endings, so read the result files in non-binary mode.

test.must_match('all',
                "aaa.in\nchecked-out bbb.in\nccc.in\n",
                mode='r')

test.must_match(['sub', 'all'],
                "sub/ddd.in\nchecked-out sub/eee.in\nsub/fff.in\n",
                mode='r')

test.must_not_be_writable(test.workpath('sub', 'SConscript'))
test.must_not_be_writable(test.workpath('aaa.in'))
test.must_not_be_writable(test.workpath('ccc.in'))
test.must_not_be_writable(test.workpath('sub', 'ddd.in'))
test.must_not_be_writable(test.workpath('sub', 'fff.in'))



#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
