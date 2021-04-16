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
Verify that use of long command lines correctly excludes arguments
surrounded by $( $) from the signature calculation.
"""

import os
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

build_py = test.workpath('build.py')

# create a dummy command which understands a tempfile syntax
# so it doesn't have to be that platform/compiler's specific syntax.
test.write(build_py, """\
#!%(_python_)s
import sys
if sys.argv[1].startswith('@'):
    tempfile = sys.argv[1][1:]
    with open(tempfile, 'r') as tmp:
        args = tmp.read().split()
else:
    args = sys.argv[1:]

with open(args[0], 'w') as ofp, open(args[1], 'r') as ifp:
    ofp.write(ifp.read())
    ofp.write('FILEFLAG=%%s\\n' %% args[2])
    ofp.write('TIMESTAMP=%%s\\n' %% args[3])
""" % locals())

os.chmod(build_py, 0o755)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
arg = 'a_long_ignored_argument'
extra_arguments = arg
MAXLINE=1024
while len(extra_arguments) <= MAXLINE:
    extra_arguments = extra_arguments + ' ' + arg
env = Environment(
    tools=[],
    FILECOM=[
        r'%(build_py)s',
        '$TARGET',
        '$SOURCE',
        '$FILEFLAG',
        '$(',
        '$TIMESTAMP',
        '$)',
        '$EXTRA_ARGUMENTS',
    ],
    FILEFLAG=ARGUMENTS.get('FILEFLAG'),
    TIMESTAMP=ARGUMENTS.get('TIMESTAMP'),
    EXTRA_ARGUMENTS=extra_arguments,
    MAXLINELENGTH=MAXLINE,
    TEMPFILEPREFIX='@',
)
env.PrependENVPath('PATHEXT', '.PY')
env.Command('file.out', 'file.in', r'%(_python_)s ${TEMPFILE(FILECOM)}')
""" % locals())

test.write('file.in', "file.in\n", mode='w')

test.run(arguments='FILEFLAG=first TIMESTAMP=20090207 .')

test.must_match('file.out', "file.in\nFILEFLAG=first\nTIMESTAMP=20090207\n", mode='r')

test.up_to_date(options='FILEFLAG=first TIMESTAMP=20090208', arguments = '.')

test.run(arguments='FILEFLAG=second TIMESTAMP=20090208 .')

test.must_match('file.out', "file.in\nFILEFLAG=second\nTIMESTAMP=20090208\n", mode='r')

test.up_to_date(options='FILEFLAG=second TIMESTAMP=20090209', arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
