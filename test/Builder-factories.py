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
Test the ability to specify the target_factory and source_factory
of a Builder.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src')

test.write('SConstruct', """
import os
import os.path
def mkdir(env, source, target):
    t = str(target[0])
    os.makedirs(t)
    with open(os.path.join(t, 'marker'), 'wb') as f:
        f.write(b"MakeDirectory\\n")
MakeDirectory = Builder(action=mkdir, target_factory=Dir)
def collect(env, source, target):
    with open(str(target[0]), 'wb') as out:
        dir = str(source[0])
        for f in sorted(os.listdir(dir)):
            f = os.path.join(dir, f)
            with open(f, 'rb') as infp:
                out.write(infp.read())
Collect = Builder(action=collect, source_factory=Dir)
env = Environment(BUILDERS = {'MakeDirectory':MakeDirectory,
                              'Collect':Collect})
env.MakeDirectory('foo', [])
env.Collect('output', 'src')
""")

test.write(['src', 'file1'], "src/file1\n")
test.write(['src', 'file2'], "src/file2\n")
test.write(['src', 'file3'], "src/file3\n")

test.run(arguments = '.')

test.fail_test(not os.path.isdir(test.workpath('foo')))
test.must_match(["foo", "marker"], "MakeDirectory\n")
test.must_match("output", "src/file1\nsrc/file2\nsrc/file3\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
