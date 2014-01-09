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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test customizing the output with the the $CVSCOMSTR variable.
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConscript', """
Environment(tools = ['CVS']).CVS('')
""")

msg_cvs = """The CVS() factory is deprecated and there is no replacement."""
warn_cvs = test.deprecated_fatal('deprecated-build-dir', msg_cvs)
msg_sc = """SourceCode() has been deprecated and there is no replacement.
\tIf you need this function, please contact dev@scons.tigris.org."""
warn_sc = test.deprecated_wrap(msg_sc)

test.subdir('CVS', ['CVS', 'sub'], 'sub')

sub_CVS = os.path.join('sub', 'CVS')
sub_SConscript = os.path.join('sub', 'SConscript')
sub_all = os.path.join('sub', 'all')
sub_ddd_in = os.path.join('sub', 'ddd.in')
sub_ddd_out = os.path.join('sub', 'ddd.out')
sub_eee_in = os.path.join('sub', 'eee.in')
sub_eee_out = os.path.join('sub', 'eee.out')
sub_fff_in = os.path.join('sub', 'fff.in')
sub_fff_out = os.path.join('sub', 'fff.out')

test.write('my-cvs-co.py', """
import shutil
import sys
for f in sys.argv[1:]:
    shutil.copy('CVS/'+f, f)
""")

test.write('SConstruct', """
SetOption('warn', 'deprecated-source-code')
def cat(env, source, target):
    target = str(target[0])
    f = open(target, "wb")
    for src in source:
        f.write(open(str(src), "rb").read())
    f.close()
env = Environment(TOOLS = ['default', 'CVS'],
                  BUILDERS={'Cat':Builder(action=cat)},
                  CVSCOM='%(_python_)s my-cvs-co.py $TARGET',
                  CVSCOMSTR='Checking out $TARGET from our fake CVS')
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.CVS(None))
SConscript('sub/SConscript', "env")
""" % locals())

test.write(['CVS', 'sub', 'SConscript'], """\
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")

test.write(['CVS', 'aaa.in'], "CVS/aaa.in\n")
test.write('bbb.in', "checked-out bbb.in\n")
test.write(['CVS', 'ccc.in'], "CVS/ccc.in\n")

test.write(['CVS', 'sub', 'ddd.in'], "CVS/sub/ddd.in\n")
test.write(['sub', 'eee.in'], "checked-out sub/eee.in\n")
test.write(['CVS', 'sub', 'fff.in'], "CVS/sub/fff.in\n")

read_str = """\
Checking out %(sub_SConscript)s from our fake CVS
""" % locals()

build_str = """\
Checking out aaa.in from our fake CVS
cat(["aaa.out"], ["aaa.in"])
cat(["bbb.out"], ["bbb.in"])
Checking out ccc.in from our fake CVS
cat(["ccc.out"], ["ccc.in"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
Checking out %(sub_ddd_in)s from our fake CVS
cat(["%(sub_ddd_out)s"], ["%(sub_ddd_in)s"])
cat(["%(sub_eee_out)s"], ["%(sub_eee_in)s"])
Checking out %(sub_fff_in)s from our fake CVS
cat(["%(sub_fff_out)s"], ["%(sub_fff_in)s"])
cat(["%(sub_all)s"], ["%(sub_ddd_out)s", "%(sub_eee_out)s", "%(sub_fff_out)s"])
""" % locals()

stdout = test.wrap_stdout(read_str = read_str, build_str = build_str)

test.run(arguments = '.',
         stdout = TestSCons.re_escape(stdout),
         stderr = warn_cvs + warn_sc)

test.must_match('all',
                "CVS/aaa.in\nchecked-out bbb.in\nCVS/ccc.in\n")

test.must_match(['sub', 'all'],
                "CVS/sub/ddd.in\nchecked-out sub/eee.in\nCVS/sub/fff.in\n")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
