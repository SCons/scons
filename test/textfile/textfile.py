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

import TestSCons

import os

test = TestSCons.TestSCons()

foo1 = test.workpath('foo1.txt')
# foo2  = test.workpath('foo2.txt')
# foo1a = test.workpath('foo1a.txt')
# foo2a = test.workpath('foo2a.txt')

match_mode = 'r'

test.file_fixture('fixture/SConstruct', 'SConstruct')

test.run(arguments='.')

linesep = '\n'

textparts = ['lalala', '42',
             'Goethe', 'Schiller',
             'tanteratei']
foo1Text = linesep.join(textparts)
foo2Text = '|*'.join(textparts)
foo1aText = foo1Text + linesep
foo2aText = foo2Text + '|*'

test.up_to_date(arguments='.')

files = list(map(test.workpath, (
    'foo1.txt', 'foo2.txt', 'foo1a.txt', 'foo2a.txt',
    'bar1', 'bar2', 'bar1a.txt', 'bar2a.txt',
)))


def check_times():
    """
    make sure the files didn't get rewritten, because nothing changed:
    """
    before = list(map(os.path.getmtime, files))
    # introduce a small delay, to make the test valid
    test.sleep()
    # should still be up-to-date
    test.up_to_date(arguments='.')
    after = list(map(os.path.getmtime, files))
    test.fail_test(before != after)


# make sure that the file content is as expected
test.must_match('foo1.txt', foo1Text, mode=match_mode)
test.must_match('bar1', foo1Text, mode=match_mode)
test.must_match('foo2.txt', foo2Text, mode=match_mode)
test.must_match('bar2', foo2Text, mode=match_mode)
test.must_match('foo1a.txt', foo1aText, mode=match_mode)
test.must_match('bar1a.txt', foo1aText, mode=match_mode)
test.must_match('foo2a.txt', foo2aText, mode=match_mode)
test.must_match('bar2a.txt', foo2aText, mode=match_mode)
check_times()

# write the contents and make sure the files
# didn't get rewritten, because nothing changed:
test.write('foo1.txt', foo1Text)
test.write('bar1', foo1Text)
test.write('foo2.txt', foo2Text)
test.write('bar2', foo2Text)
test.write('foo1a.txt', foo1aText)
test.write('bar1a.txt', foo1aText)
test.write('foo2a.txt', foo2aText)
test.write('bar2a.txt', foo2aText)
check_times()

# now that textfile is part of default tool list, run one testcase
# without adding it explicitly as a tool to make sure.
test.file_fixture('fixture/SConstruct.2', 'SConstruct.2')

test.run(options='-f SConstruct.2', arguments='.')

line1 = 'This line has no substitutions'
line2a = 'This line has @subst@ substitutions'
line2b = 'This line has most substitutions'
line3a = 'This line has %subst% substitutions'
line3b = 'This line has many substitutions'


def matchem(match_file, lines):
    """
    Join all the lines with correct line separator,
    then compare
    """
    lines = linesep.join(lines)
    test.must_match(match_file, lines, mode=match_mode, message="Expected:\n%s\n" % lines)


matchem('text.txt', [line1, line2a, line3a])
matchem('sub1', [line1, line2a, line3a])
matchem('sub2', [line1, line2b, line3a])
matchem('sub3', [line1, line2b, line3b])
matchem('sub4', [line1, line2a, line3b])
matchem('sub5', [line1, line2b, line3b])
matchem('sub6', [line1, line2b, line3b])

test.up_to_date(options='-f SConstruct.2', arguments='.')

test.pass_test()
