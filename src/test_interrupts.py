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
Verify that the SCons source code contains only correct handling of
keyboard interrupts (e.g. Ctrl-C).
"""

import os
import os.path
import re
import string
import time

import TestSCons

test = TestSCons.TestSCons()

# We do not want statements of the form:
# try:
#   # do something, e.g.
#   return a['x']
# except:
#   # do the exception handling
#   a['x'] = getx()
#   return a['x']
#
# The code above may catch a KeyboardInterrupt exception, which was not
# intended by the programmer. We check for these situations in all python
# source files.

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    scons_lib_dir = os.environ['SCONS_LIB_DIR']
    MANIFEST = os.path.join(scons_lib_dir, 'MANIFEST.in')
else:
    #cwd = os.getcwd()
    scons_lib_dir = os.path.join(cwd, 'build', 'scons')
    MANIFEST = os.path.join(scons_lib_dir, 'MANIFEST')

files = string.split(open(MANIFEST).read())
files = filter(lambda f: f[-3:] == '.py', files)

# some regexps to parse the python files
tryexc_pat = re.compile(
r'^(?P<try_or_except>(?P<indent> *)(try|except)( [^\n]*)?:.*)',re.MULTILINE)
keyboardint_pat = re.compile(r' *except +([^,],)*KeyboardInterrupt([ ,][^\n]*)?:[^\n]*')
exceptall_pat   = re.compile(r' *except *:[^\n]*')

uncaughtKeyboardInterrupt = 0
for f in files:
    contents = open(os.path.join(scons_lib_dir, f)).read()
    try_except_lines = {}
    lastend = 0
    while 1:
        match = tryexc_pat.search( contents, lastend )
        if match is None:
            break
        #print match.groups()
        lastend = match.end()
        try:
            indent_list = try_except_lines[match.group('indent')]
        except:
            indent_list = []
        line_num = 1 + string.count(contents[:match.start()], '\n')
        indent_list.append( (line_num, match.group('try_or_except') ) )
        try_except_lines[match.group('indent')] = indent_list
    for indent in try_except_lines.keys():
        exc_keyboardint_seen = 0
        exc_all_seen = 0
        for (l,statement) in try_except_lines[indent] + [(-1,indent + 'try')]:
            #print "%4d %s" % (l,statement),
            m1 = keyboardint_pat.match(statement)
            m2 = exceptall_pat.match(statement)
            if string.find(statement, indent + 'try') == 0:
                if exc_all_seen and not exc_keyboardint_seen:
                    uncaughtKeyboardInterrupt = 1
                    print "File %s:%d: Uncaught KeyboardInterrupt!" % (f,line)
                exc_keyboardint_seen = 0
                exc_all_seen = 0
                line = l
                #print " -> reset"
            elif not m1 is None:
                exc_keyboardint_seen = 1
                #print " -> keyboard -> ", m1.groups()
            elif not m2 is None:
                exc_all_seen = 1
                #print " -> all -> ", m2.groups()
            else:
                pass
                #print "Warning: unknown statement %s" % statement

test.fail_test(uncaughtKeyboardInterrupt)

test.pass_test()
