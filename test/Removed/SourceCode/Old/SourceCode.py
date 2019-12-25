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
Test fetching source files using the SourceCode() method.
"""

import os

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConscript', """
SourceCode('.', None)
""")

msg = """SourceCode() has been deprecated and there is no replacement.
\tIf you need this function, please contact scons-dev@scons.org"""
warning = test.deprecated_warning('deprecated-source-code', msg)

test.subdir('sub', 'sub2')

test.write('SConstruct', """\
SetOption('warn', 'deprecated-source-code')
import os

def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as ofp:
        for src in source:
            with open(str(src), "rb") as ifp:
                ofp.write(ifp.read())

def sc_cat(env, source, target):
    source = []
    for t in target:
        head, tail = os.path.split(str(t))
        source.append(os.path.join(head, 'sc-' + tail))
    cat(env, source, target)

env = Environment(BUILDERS={'Cat':Builder(action=cat)}, SUBDIR='sub')
env.SourceCode('$SUBDIR', Builder(action=sc_cat, env=env))
env.Cat('aaa.out', 'sub/aaa.in')
bbb_in = File('sub/bbb.in')
bbb_in.is_derived()
env.Cat('bbb.out', bbb_in)
env.Cat('ccc.out', 'sub/ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
SConscript('sub/SConscript', "env")

SourceCode('sub2', Builder(action=sc_cat, env=env))
env.Cat('ddd.out', 'sub2/ddd.in')
""")

test.write(['sub', 'sc-aaa.in'], "sub/sc-aaa.in\n")
test.write(['sub', 'sc-bbb.in'], "sub/sc-bbb.in\n")
test.write(['sub', 'sc-ccc.in'], "sub/sc-ccc.in\n")
test.write(['sub2', 'sc-ddd.in'], "sub2/sc-ddd.in\n")

test.write(['sub', 'sc-SConscript'], "'sub/sc-SConscript'\n")

read_str = """\
sc_cat(["%s"], [])
""" % (os.path.join('sub', 'SConscript'))

build_str = """\
sc_cat(["%s"], [])
cat(["aaa.out"], ["%s"])
sc_cat(["%s"], [])
cat(["bbb.out"], ["%s"])
sc_cat(["%s"], [])
cat(["ccc.out"], ["%s"])
cat(["all"], ["aaa.out", "bbb.out", "ccc.out"])
sc_cat(["%s"], [])
cat(["ddd.out"], ["%s"])
""" % (os.path.join('sub', 'aaa.in'),
       os.path.join('sub', 'aaa.in'),
       os.path.join('sub', 'bbb.in'),
       os.path.join('sub', 'bbb.in'),
       os.path.join('sub', 'ccc.in'),
       os.path.join('sub', 'ccc.in'),
       os.path.join('sub2', 'ddd.in'),
       os.path.join('sub2', 'ddd.in'))

stdout = TestSCons.re_escape(test.wrap_stdout(read_str = read_str,
                                              build_str = build_str))

test.run(arguments = '.', stdout = stdout, stderr = 2*warning)

test.must_match(['sub', 'SConscript'], "'sub/sc-SConscript'\n")
test.must_match('all', "sub/sc-aaa.in\nsub/sc-bbb.in\nsub/sc-ccc.in\n")
test.must_match('ddd.out', "sub2/sc-ddd.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
