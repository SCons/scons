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
Verify that the sconsign script works with files generated when
using the signatures in an SConsignFile().
"""

import TestSCons
import TestSConsign

_python_ = TestSCons._python_

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

test.subdir('sub1', 'sub2')

test.write('fake_cc.py', r"""
import os.path
import re
import string
import sys

path = string.split(sys.argv[1])
output = open(sys.argv[2], 'wb')
input = open(sys.argv[3], 'rb')

output.write('fake_cc.py:  %s\n' % sys.argv)

def find_file(f):
    for dir in path:
        p = dir + os.sep + f
        if os.path.exists(p):
            return open(p, 'rb')
    return None

def process(infp, outfp):
    for line in infp.readlines():
        m = re.match('#include <(.*)>', line)
        if m:
            file = m.group(1)
            process(find_file(file), outfp)
        else:
            outfp.write(line)

process(input, output)

sys.exit(0)
""")

test.write('fake_link.py', r"""
import sys

output = open(sys.argv[1], 'wb')
input = open(sys.argv[2], 'rb')

output.write('fake_link.py:  %s\n' % sys.argv)

output.write(input.read())

sys.exit(0)
""")

# Note:  We don't use os.path.join() representations of the file names
# in the expected output because paths in the .sconsign files are
# canonicalized to use / as the separator.

sub1_hello_c    = 'sub1/hello.c'
sub1_hello_obj  = 'sub1/hello.obj'
sub2_hello_c    = 'sub2/hello.c'
sub2_hello_obj  = 'sub2/hello.obj'
sub2_inc1_h     = 'sub2/inc1.h'
sub2_inc2_h     = 'sub2/inc2.h'

test.write(['SConstruct'], """\
SConsignFile()
env1 = Environment(PROGSUFFIX = '.exe',
                   OBJSUFFIX = '.obj',
                   CCCOM = r'%(_python_)s fake_cc.py sub2 $TARGET $SOURCE',
                   LINKCOM = r'%(_python_)s fake_link.py $TARGET $SOURCE')
env1.Program('sub1/hello.c')
env2 = env1.Clone(CPPPATH = ['sub2'])
env2.Program('sub2/hello.c')
""" % locals())

test.write(['sub1', 'hello.c'], r"""
sub1/hello.c
""")

test.write(['sub2', 'hello.c'], r"""
#include <inc1.h>
#include <inc2.h>
int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("sub2/goodbye.c\n");
        exit (0);
}
""")

test.write(['sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.run(arguments = '--implicit-cache .')

sig_re = r'[0-9a-fA-F]{32}'

test.run_sconsign(arguments = ".sconsign",
         stdout = r"""=== .:
SConstruct: None \d+ \d+
=== sub1:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        %(sub2_hello_obj)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
inc1.h: %(sig_re)s \d+ \d+
inc2.h: %(sig_re)s \d+ \d+
""" % locals())

test.run_sconsign(arguments = "--raw .sconsign",
         stdout = r"""=== .:
SConstruct: {'csig': None, 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
=== sub1:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub1_hello_obj)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub1_hello_c)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sig_re)s \[.*\]
=== sub2:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub2_hello_obj)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub2_hello_c)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub2_inc1_h)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sub2_inc2_h)s: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
        %(sig_re)s \[.*\]
inc1.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
inc2.h: {'csig': '%(sig_re)s', 'timestamp': \d+, 'size': \d+L?, '_version_id': 1}
""" % locals())

expect = r"""=== .:
SConstruct:
    csig: None
    timestamp: \d+
    size: \d+
=== sub1:
hello.c:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
hello.exe:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        %(sub1_hello_obj)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
hello.obj:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        %(sub1_hello_c)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
=== sub2:
hello.c:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
hello.exe:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        %(sub2_hello_obj)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
hello.obj:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
    implicit:
        %(sub2_hello_c)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
        %(sub2_inc1_h)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
        %(sub2_inc2_h)s:
            csig: %(sig_re)s
            timestamp: \d+
            size: \d+
    action: %(sig_re)s \[.*\]
inc1.h:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
inc2.h:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
""" % locals()

test.run_sconsign(arguments = "-v .sconsign", stdout=expect)

test.run_sconsign(arguments = "-c -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    csig: None
=== sub1:
hello.c:
    csig: %(sig_re)s
hello.exe:
    csig: %(sig_re)s
hello.obj:
    csig: %(sig_re)s
=== sub2:
hello.c:
    csig: %(sig_re)s
hello.exe:
    csig: %(sig_re)s
hello.obj:
    csig: %(sig_re)s
inc1.h:
    csig: %(sig_re)s
inc2.h:
    csig: %(sig_re)s
""" % locals())

test.run_sconsign(arguments = "-s -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    size: \d+
=== sub1:
hello.c:
    size: \d+
hello.exe:
    size: \d+
hello.obj:
    size: \d+
=== sub2:
hello.c:
    size: \d+
hello.exe:
    size: \d+
hello.obj:
    size: \d+
inc1.h:
    size: \d+
inc2.h:
    size: \d+
""" % locals())

test.run_sconsign(arguments = "-t -v .sconsign",
         stdout = r"""=== .:
SConstruct:
    timestamp: \d+
=== sub1:
hello.c:
    timestamp: \d+
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
=== sub2:
hello.c:
    timestamp: \d+
hello.exe:
    timestamp: \d+
hello.obj:
    timestamp: \d+
inc1.h:
    timestamp: \d+
inc2.h:
    timestamp: \d+
""" % locals())

test.run_sconsign(arguments = "-e hello.obj .sconsign",
         stdout = r"""=== .:
=== sub1:
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
         stderr = r"""sconsign: no entry `hello.obj' in `\.'
""")

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj .sconsign",
         stdout = r"""=== .:
=== sub1:
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        %(sub2_hello_obj)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
        stderr = r"""sconsign: no entry `hello.obj' in `\.'
sconsign: no entry `hello.exe' in `\.'
sconsign: no entry `hello.obj' in `\.'
""" % locals())

#test.run_sconsign(arguments = "-i -v .sconsign",
#         stdout = r"""=== sub1:
#hello.exe:
#    implicit:
#        hello.obj: %(sig_re)s
#hello.obj:
#    implicit:
#        hello.c: %(sig_re)s
#=== sub2:
#hello.exe:
#    implicit:
#        hello.obj: %(sig_re)s
#hello.obj:
#    implicit:
#        hello.c: %(sig_re)s
#        inc1.h: %(sig_re)s
#        inc2.h: %(sig_re)s
#inc1.h: %(sig_re)s
#inc2.h: %(sig_re)s
#""" % locals())

test.pass_test()
