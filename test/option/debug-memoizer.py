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
Test calling the --debug=memoizer option.
"""

import os
import string

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def cat(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

# The banner, and a list of representative method names that we expect
# to show up in the output.  Of course, this depends on keeping those
# names in the implementation, so if we change them, we'll have to
# change this test...
expect = [
    "Memoizer (memory cache) hits and misses",
    "Dir.exists()",
    "File.exists()",
    "SConsEnvironment.Detect()",
]

for args in ['-h --debug=memoizer', '--debug=memoizer']:
    test.run(arguments = args)
    stdout = test.stdout()
    missing = filter(lambda e, s=stdout: string.find(s, e) == -1, expect)
    if missing:
        print "Missing the following strings in the command line '%s' output:" % args
        print "    " + string.join(missing, "\n    ")
        print "STDOUT ============"
        print stdout
        test.fail_test(1)

test.must_match('file.out', "file.in\n")



test.unlink("file.out")

os.environ['SCONSFLAGS'] = '--debug=memoizer'

test.run()
stdout = test.stdout()
missing = filter(lambda e, s=stdout: string.find(s, e) == -1, expect)
if missing:
    print "Missing the following strings in the SCONSFLAGS=--debug=memoizer output:"
    print "    " + string.join(missing, "\n    ")
    print "STDOUT ============"
    print stdout
    test.fail_test(1)



test.pass_test()
