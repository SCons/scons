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
Verify that we use a default target of the current directory when there
is no Default() in the SConstruct file and there are no command-line
arguments, or a null command-line argument.
"""


import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', r"""
def cat(env, source, target):
    target = str(target[0])
    source = list(map(str, source))
    print('cat(%s) > %s' % (source, target))
    with open(target, "wb") as f:
        for src in source:
            with open(src, "rb") as ifp:
                f.write(ifp.read())

env = Environment(BUILDERS={'Build':Builder(action=cat)})
env.Build('aaa.out', 'aaa.in')
""")

test.write('aaa.in', "aaa.in\n")

up_to_date = test.wrap_stdout("scons: `.' is up to date.\n")

#
test.run()
test.must_match('aaa.out', "aaa.in\n")
test.run(stdout=up_to_date)

#
test.unlink('aaa.out')
test.must_not_exist('aaa.out')

#
test.run([''])
test.must_match('aaa.out', "aaa.in\n")
test.run([''], stdout=up_to_date)

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
