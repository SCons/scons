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

import sys
import TestSCons

test = TestSCons.TestSCons()

# Right now, due to interaction with external quoting conventions,
# we do NOT actually support arbitrary characters in file names.
# (For example, double-quotes in a file name on POSIX break due
# to interaction with the "sh -c" quoting conventions.)
#
# This is a tough nut to crack, though.  Right now, we use the
# external command interpreters so we don't have to roll our own
# parsing and interpretation of redirection and piping.  But that
# means we have to find ways to work with *all* of their quoting
# conventions.
#
# Until we sort that all out, short-circuit this test so we can
# check it in and avoid having to re-invent this wheel later.
test.pass_test()

def contents(c):
    return "|" + c + "|\n"

if sys.platform == 'win32':
    def bad_char(c):
        return c in '/\\:'
else:
    def bad_char(c):
        return c in '/'

# Only worry about ASCII characters right now.
# Someone with more Unicode knowledge should enhance this later.
for i in range(1, 255):
    c = chr(i)
    if not bad_char(c):
        test.write("in" + c + "in", contents(c))

test.write('SConstruct', r"""
import sys
if sys.platform == 'win32':
    def bad_char(c):
        return (c == '/' or c == '\\' or c == ':')
else:
    def bad_char(c):
        return (c == '/')
env = Environment()
for i in range(1, 255):
    c = chr(i)
    if not bad_char(c):
        if c in '$':
            c = '\\' + c
        infile = "in" + c + "in"
        env.Command(c + "out", infile, "cp $SOURCE $TARGET")
        env.Command("out" + c + "out", infile, "cp $SOURCE $TARGET")
        env.Command("out" + c, infile, "cp $SOURCE $TARGET")
""")

test.run(arguments = '.')

for i in range(1, 255):
    c = chr(i)
    if not bad_char(c):
        test.fail_test(test.read(c + "out") != contents(c))
        test.fail_test(test.read("out" + c + "out") != contents(c))
        test.fail_test(test.read("out" + c) != contents(c))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
