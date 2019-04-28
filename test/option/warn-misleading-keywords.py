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
Verify use of the --warn=misleading-keywords option.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)


test.write('SConstruct', """
DefaultEnvironment(tools=[])
def build(env, target, source):
    with open(str(target[0]), 'wb') as f:
        for s in source:
            with open(str(s), 'rb') as infp:
                f.write(infp.read())

WARN = ARGUMENTS.get('WARN')
if WARN:
    SetOption('warn', WARN)

B = Builder(action=build, multi=1)
env = Environment(tools=[], BUILDERS = { 'B' : B })
env.B(targets = 'file3a.out', source = 'file3a.in')
env.B(target = 'file3b.out', sources = 'file3b.in')
""")

test.write('file3a.in', 'file3a.in\n')
test.write('file3b.out', 'file3b.out\n')

expect = r"""
scons: warning: Did you mean to use `(target|source)' instead of `(targets|sources)'\?
""" + TestSCons.file_expr

test.run(arguments='.', 
         stderr=expect + expect)

test.must_match(['file3a'], 'file3a.in\n')
test.must_match(['file3b'], 'file3b.out\n')

test.run(arguments='--warn=misleading-keywords .', stderr=expect + expect)

test.run(arguments='--warn=no-misleading-keywords .')

test.run(arguments='WARN=misleading-keywords .', stderr=expect + expect)

test.run(arguments='WARN=no-misleading-keywords .')


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
