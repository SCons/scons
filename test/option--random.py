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
Verify that we build correctly using the --random option.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConscript', """\
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
""")

test.write('aaa.in', "aaa.in\n")
test.write('bbb.in', "bbb.in\n")
test.write('ccc.in', "ccc.in\n")



test.write('SConstruct', """\
SetOption('random', 1)
SConscript('SConscript')
""")

test.run(arguments = '-n -Q')
non_random_output = test.stdout()

tries = 0
max_tries = 10
while test.stdout() == non_random_output:
    if tries >= max_tries:
        print("--random generated the non-random output %s times!" % max_tries)
        test.fail_test()
    tries = tries + 1
    test.run(arguments = '-n -Q --random')



test.write('SConstruct', """\
SConscript('SConscript')
""")

test.run(arguments = '-n -Q')
non_random_output = test.stdout()

tries = 0
max_tries = 10
while test.stdout() == non_random_output:
    if tries >= max_tries:
        print("--random generated the non-random output %s times!" % max_tries)
        test.fail_test()
    tries = tries + 1
    test.run(arguments = '-n -Q --random')



test.run(arguments = '-Q --random')

test.must_match('all', "aaa.in\nbbb.in\nccc.in\n")

test.run(arguments = '-q --random .')

test.run(arguments = '-c --random .')

test.must_not_exist(test.workpath('aaa.out'))
test.must_not_exist(test.workpath('bbb.out'))
test.must_not_exist(test.workpath('ccc.out'))
test.must_not_exist(test.workpath('all'))

test.run(arguments = '-q --random .', status = 1)

test.run(arguments = '--random .')

test.must_match('all', "aaa.in\nbbb.in\nccc.in\n")

test.run(arguments = '-c --random .')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
