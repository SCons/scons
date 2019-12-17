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
# This test exercises the addition operator of Action objects.
# Using Environment.Prepend() and Environment.Append(), you should be
# able to add new actions to existing ones, effectively adding steps
# to a build process.

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import stat
import sys
import TestSCons

_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.dir_fixture('append-fixture')

test.write('SConstruct', """

env=Environment()

def before(env, target, source):
    with open(str(target[0]), "wb") as f:
        f.write(b"Foo\\n")
    with open("before.txt", "wb") as f:
        f.write(b"Bar\\n")

def after(env, target, source):
    with open(str(target[0]), "rb") as fin, open("after%s", "wb") as fout:
        fout.write(fin.read())

env.Prepend(LINKCOM=Action(before))
env.Append(LINKCOM=Action(after))
env.Program(source='foo.c', target='foo')
""" % _exe)

after_exe = test.workpath('after' + _exe)

test.run(arguments='.')
test.must_match('before.txt', 'Bar\n')
os.chmod(after_exe, os.stat(after_exe)[stat.ST_MODE] | stat.S_IXUSR)
test.run(program=after_exe, stdout="Foo\n")
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
