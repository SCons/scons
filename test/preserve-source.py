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

import os.path

import TestSCons

test = TestSCons.TestSCons()

#
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

#
test.run(arguments = '.')

test.fail_test(test.read('aaa.out') != b"aaa.in\n")

#
test.run(arguments = "aaa.in",
         stdout = test.wrap_stdout("scons: Nothing to be done for `aaa.in'.\n"))

test.fail_test(not os.path.exists('aaa.in'))

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
