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

import re
import TestSCons
import TestSConsign

_python_ = TestSCons._python_

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)
test.subdir('sub1', 'sub2')

fake_cc_py = test.workpath('fake_cc.py')
fake_link_py = test.workpath('fake_link.py')

test.write(fake_cc_py, r"""#!%(_python_)s
import os
import re
import sys

path = sys.argv[1].split()

def find_file(f):
    for dir in path:
        p = dir + os.sep + f
        if os.path.exists(p):
            return open(p, 'r')
    return None

def process(infp, outfp):
    for line in infp.readlines():
        m = re.match(r'#include <(.*)>', line)
        if m:
            file = m.group(1)
            found = find_file(file)
            process(found, outfp)
            if found:
                found.close()
        else:
            outfp.write(line)

with open(sys.argv[2], 'w') as outf, open(sys.argv[3], 'r') as ifp:
    outf.write('fake_cc.py:  %%s\n' %% sys.argv)
    process(ifp, outf)

sys.exit(0)
""" % locals())

test.write(fake_link_py, r"""#!%(_python_)s
import sys

with open(sys.argv[1], 'w') as outf, open(sys.argv[2], 'r') as ifp:
    outf.write('fake_link.py:  %%s\n' %% sys.argv)
    outf.write(ifp.read())

sys.exit(0)
""" % locals())

test.chmod(fake_cc_py, 0o755)
test.chmod(fake_link_py, 0o755)

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
                   CCCOM = [[r'%(fake_cc_py)s', 'sub2', '$TARGET', '$SOURCE']],
                   LINKCOM = [[r'%(fake_link_py)s', '$TARGET', '$SOURCE']])
env1.PrependENVPath('PATHEXT', '.PY')
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
fake_cc\.py: %(sig_re)s \d+ \d+
fake_link\.py: %(sig_re)s \d+ \d+
=== sub1:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        fake_link\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.c: %(sig_re)s \d+ \d+
hello.exe: %(sig_re)s \d+ \d+
        %(sub2_hello_obj)s: %(sig_re)s \d+ \d+
        fake_link\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
inc1.h: %(sig_re)s \d+ \d+
inc2.h: %(sig_re)s \d+ \d+
""" % locals())

test.run_sconsign(arguments = "--raw .sconsign",
         stdout = r"""=== .:
SConstruct: {'csig': None, 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
fake_cc\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
fake_link\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
=== sub1:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub1_hello_obj)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        fake_link\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub1_hello_c)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        fake_cc\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sig_re)s \[.*\]
=== sub2:
hello.c: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
hello.exe: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub2_hello_obj)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        fake_link\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sig_re)s \[.*\]
hello.obj: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub2_hello_c)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub2_inc1_h)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sub2_inc2_h)s: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        fake_cc\.py: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
        %(sig_re)s \[.*\]
inc1.h: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
inc2.h: {'csig': '%(sig_re)s', 'timestamp': \d+L?, 'size': \d+L?, '_version_id': 2}
""" % locals())

expect = r"""=== .:
SConstruct:
    csig: None
    timestamp: \d+
    size: \d+
fake_cc\.py:
    csig: %(sig_re)s
    timestamp: \d+
    size: \d+
fake_link\.py:
    csig: %(sig_re)s
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
        fake_link\.py:
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
        fake_cc\.py:
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
        fake_link\.py:
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
        fake_cc\.py:
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
fake_cc\.py:
    csig: %(sig_re)s
fake_link\.py:
    csig: %(sig_re)s
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
fake_cc\.py:
    size: \d+
fake_link\.py:
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
fake_cc\.py:
    timestamp: \d+
fake_link\.py:
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
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
         stderr = r"""sconsign: no entry `hello\.obj' in `\.'
""" % locals())

test.run_sconsign(arguments = "-e hello.obj -e hello.exe -e hello.obj .sconsign",
         stdout = r"""=== .:
=== sub1:
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        fake_link\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
=== sub2:
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.exe: %(sig_re)s \d+ \d+
        %(sub2_hello_obj)s: %(sig_re)s \d+ \d+
        fake_link\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub2_hello_c)s: %(sig_re)s \d+ \d+
        %(sub2_inc1_h)s: %(sig_re)s \d+ \d+
        %(sub2_inc2_h)s: %(sig_re)s \d+ \d+
        fake_cc\.py: %(sig_re)s \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
        stderr = r"""sconsign: no entry `hello\.obj' in `\.'
sconsign: no entry `hello\.exe' in `\.'
sconsign: no entry `hello\.obj' in `\.'
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

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
