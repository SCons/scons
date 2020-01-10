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

def contents(c):
    return "|" + c + "|\n"

invalid_chars = '/\0'

if sys.platform == 'win32':
    invalid_chars = set(invalid_chars)

    # See the 'naming conventions' section of
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    invalid_chars.update([ chr(c) for c in range(32) ])
    invalid_chars.update(r'\/:*?"<>|')
    invalid_chars.update(chr(127))

    # Win32 filesystems are case insensitive so don't do half the alphabet.
    import string
    invalid_chars.update(string.ascii_lowercase)

    # See the 'naming conventions' section of
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx
    def bad_char(c):
        return c in invalid_chars
    def invalid_leading_char(c):
        # the hash character as a leading character is interpreted to mean the project root
        return c in ' #'
    def invalid_trailing_char(c):
        return c in ' .'
    commandString = "copy $SOURCE $TARGET"
else:
    invalid_chars = set(invalid_chars)
    invalid_chars.add(chr(10))
    invalid_chars.add(chr(13))
    invalid_chars.add(chr(92)) # forward slash (dirsep)
    invalid_chars.add(chr(96)) # backtick

    
    def bad_char(c):
        return c in invalid_chars
    def invalid_leading_char(c):
        # the hash character as a leading character is interpreted to mean the project root
        return c in '#'
    def invalid_trailing_char(c):
        return False
    commandString = "cp $SOURCE $TARGET"

goodChars = [ chr(c) for c in range(1, 128) if not bad_char(chr(c)) ]

def get_filename(ftype,c):
    return ftype+"%d"%ord(c[-1])+c+ftype

for c in goodChars:
    test.write(get_filename("in",c), contents(c))

def create_command(a, b, c):
    a = ('', 'out')[a]
    b = ('', 'out')[b]
    return 'env.Command("' + a + get_filename('',c) + b + '", "'+get_filename("in",c)+ '","' + commandString + '")'

sconstruct = [ 'import sys', 'env = Environment(tools=[])' ]
for c in goodChars:
    if c == '$':
        c = '$$'
    if c == '"':
        c = r'\"'
    infile = get_filename("in",c)
    if not invalid_leading_char(c):
        sconstruct.append(create_command(False, True, c))
    sconstruct.append(create_command(True, True, c))
    if not invalid_trailing_char(c):
        sconstruct.append(create_command(True, False, c))
test.write('SConstruct', '\n'.join(sconstruct))

test.run(arguments = '.')

for c in goodChars:
#    print "Checking %d "%ord(c)

    c_str = ("%d"%ord(c[-1]))+c
    if not invalid_leading_char(c):
        test.must_match(c_str + "out", contents(c))
    test.must_match("out" + c_str + "out", contents(c))
    if not invalid_trailing_char(c):
        test.must_match("out" + c_str, contents(c))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
