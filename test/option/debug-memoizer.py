#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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

"""Test calling the --debug=memoizer option."""

import os

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

test.write('SConstruct', """
def cat(target, source, env):
    with open(target[0], 'wb') as f, open(source[0], 'rb') as infp:
        f.write(infp.read())

DefaultEnvironment(tools=[])
env = Environment(tools=[], BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

# The banner, and a list of representative method names that we expect
# to show up in the output.  Of course, this depends on keeping those
# names in the implementation, so if we change them, we'll have to
# change this test...
expect = [
    # "Memoizer (memory cache) hits and misses",
    "Dir.srcdir_list()",
    "File.stat()",
    "File.exists()",
    "Node._children_get()",
]

test.run(arguments='--debug=memoizer')
test.must_contain_any_line(test.stdout(), expect)
test.must_match('file.out', "file.in\n")
test.unlink("file.out")

# make sure it also works if memoizer is not the only debug flag
test.run(arguments='--debug=sconscript,memoizer')
test.must_contain_any_line(test.stdout(), expect)
test.must_match('file.out', "file.in\n")
test.unlink("file.out")

# memoization should still report even in help mode
test.run(arguments='-h --debug=memoizer')
test.must_contain_any_line(test.stdout(), expect)
test.must_not_exist("file.out")

# also try setting in SCONSFLAGS
os.environ['SCONSFLAGS'] = '--debug=memoizer'
test.run(arguments='.')
test.must_contain_any_line(test.stdout(), expect)
test.must_match('file.out', "file.in\n")

test.pass_test()
