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

"""
Verify that the sconsign script works when using a .sconsign file in
each subdirectory (SConsignFile(None)) written with the non-default
value of Decider('timestamp-newer').
"""

import TestSCons
import TestSConsign

from TestSCons import _python_
from TestCmd import NEED_HELPER

test = TestSConsign.TestSConsign(match = TestSConsign.match_re)

if NEED_HELPER:
    test.skip_test("Test host cannot directly execute scripts, skipping test\n")

# Note:  We don't use os.path.join() representations of the file names
# in the expected output because paths in the .sconsign files are
# canonicalized to use / as the separator.

sub1_hello_c = 'sub1/hello.c'
sub1_hello_obj = 'sub1/hello.obj'

test.subdir('sub1', 'sub2')

# Because this test sets SConsignFile(None), we execute our fake
# scripts directly, not by feeding them to the Python executable.
# That is, we chmod 0o755 and use a "#!/usr/bin/env python" first
# line for POSIX systems, and add .PY to the %PATHEXT% variable on
# Windows.  If we didn't do this, then running this script with
# suitable prileveges would create a .sconsign file in the directory
# where the Python executable lives.  This can happen out of the
# box on Mac OS X, with the result that the .sconsign statefulness
# can mess up other tests.

fake_cc_py = test.workpath('fake_cc.py')
fake_link_py = test.workpath('fake_link.py')

test.write(
    fake_cc_py,
    fr"""#!{_python_}
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
        m = re.match('#include <(.*)>', line)
        if m:
            file = m.group(1)
            found = find_file(file)
            process(found, outfp)
            if found:
                found.close()
        else:
            outfp.write(line)

with open(sys.argv[2], 'w') as outf, open(sys.argv[3], 'r') as ifp:
    outf.write('fake_cc.py:  %s\n' % sys.argv)
    process(ifp, outf)

sys.exit(0)
""",
)

test.write(
    fake_link_py,
    fr"""#!{_python_}
import sys

with open(sys.argv[1], 'w') as outf, open(sys.argv[2], 'r') as ifp:
    outf.write('fake_link.py:  %s\n' % sys.argv)
    outf.write(ifp.read())

sys.exit(0)
""",
)

test.chmod(fake_cc_py, 0o755)
test.chmod(fake_link_py, 0o755)

test.write(
    'SConstruct',
    f"""
SConsignFile(None)
Decider('timestamp-newer')
env1 = Environment(
    PROGSUFFIX='.exe',
    OBJSUFFIX='.obj',
    # Specify the command lines with lists-of-lists so
    # finding the implicit dependencies works even with
    # spaces in the fake_*_py path names.
    CCCOM=[[r'{fake_cc_py}', 'sub2', '$TARGET', '$SOURCE']],
    LINKCOM=[[r'{fake_link_py}', '$TARGET', '$SOURCE']],
)
env1.PrependENVPath('PATHEXT', '.PY')
env1.Program('sub1/hello.c')
env2 = env1.Clone(CPPPATH=['sub2'])
env2.Program('sub2/hello.c')
""",
)
# TODO in the above, we would normally want to run a python program
# using "our Python" like this:
#    CCCOM=[[r'{_python_}', r'{fake_cc_py}', 'sub2', '$TARGET', '$SOURCE']],
#    LINKCOM=[[r'{_python_}', r'{fake_link_py}', '$TARGET', '$SOURCE']],
# however we're looking at dependencies with sconsign, so that breaks things.
# It still breaks things on Windows if something else is registered as the
# handler for .py files, as Visual Studio Code installs itself.

test.write(['sub1', 'hello.c'], r"""\
sub1/hello.c
""")

test.write(['sub2', 'hello.c'], r"""\
#include <inc1.h>
#include <inc2.h>
sub2/hello.c
""")

test.write(['sub2', 'inc1.h'], r"""\
#define STRING1 "inc1.h"
""")

test.write(['sub2', 'inc2.h'], r"""\
#define STRING2 "inc2.h"
""")

test.sleep()  # delay for timestamps
test.run(arguments = '. --max-drift=1')

sig_re = r'[0-9a-fA-F]{32,64}'
date_re = r'\S+ \S+ [ \d]\d \d\d:\d\d:\d\d \d\d\d\d'
database_name = test.get_sconsignname()

test.run_sconsign(
    arguments=f"-e hello.exe -e hello.obj sub1/{database_name}",
    stdout=r"""hello.exe: %(sig_re)s \d+ \d+
        %(sub1_hello_obj)s: %(sig_re)s \d+ \d+
        fake_link\.py: None \d+ \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s \d+ \d+
        %(sub1_hello_c)s: None \d+ \d+
        fake_cc\.py: None \d+ \d+
        %(sig_re)s \[.*\]
""" % locals(),
)

test.run_sconsign(
    arguments=f"-e hello.exe -e hello.obj -r sub1/{database_name}",
    stdout=r"""hello.exe: %(sig_re)s '%(date_re)s' \d+
        %(sub1_hello_obj)s: %(sig_re)s '%(date_re)s' \d+
        fake_link\.py: None '%(date_re)s' \d+
        %(sig_re)s \[.*\]
hello.obj: %(sig_re)s '%(date_re)s' \d+
        %(sub1_hello_c)s: None '%(date_re)s' \d+
        fake_cc\.py: None '%(date_re)s' \d+
        %(sig_re)s \[.*\]
""" % locals(),
)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
