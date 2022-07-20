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
Test that detection of file-writing options in LEXFLAGS works.
Also test that construction vars for the same purpose work.
"""

import sysconfig
from pathlib import Path

import TestSCons
from TestCmd import IS_WINDOWS

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir('sub1')
test.subdir('sub2')

test.file_fixture('mylex.py')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
SConscript(dirs=['sub1', 'sub2'])
""")

# this SConscript is for the options-in-flags version
test.write(['sub1', 'SConscript'], f"""\
import sys

env = Environment(
    LEX=r'{_python_} mylex.py',
    LEXFLAGS='-x --header-file=header.h --tables-file=tables.t',
    tools=['default', 'lex'],
)
targs = env.CFile(target='aaa', source='aaa.l')
t = [str(target) for target in targs]
# fail ourselves if the two extra files were not detected
if not all((len(t) == 3, "header.h" in t, "tables.t" in t)):
    sys.exit(1)
""")
test.write(['sub1', 'aaa.l'], "aaa.l\nLEXFLAGS\n")

# this SConscript is for the construction var version
test.write(['sub2', 'SConscript'], f"""\
import sys

env = Environment(
    LEX=r'{_python_} mylex.py',
    LEXFLAGS='-x',
    tools=['default', 'lex'],
)
env.CFile(
    target='aaa',
    source='aaa.l',
    LEX_HEADER_FILE='header.h',
    LEX_TABLES_FILE='tables.t',
)
""")
test.write(['sub2', 'aaa.l'], "aaa.l\nLEXFLAGS\n")

test.run('.', stderr=None)

lexflags = ' -x --header-file=header.h --tables-file=tables.t -t'
if IS_WINDOWS and not sysconfig.get_platform() in ("mingw",):
    lexflags = ' --nounistd' + lexflags
# Read in with mode='r' because mylex.py implicitly wrote to stdout
# with mode='w'.
test.must_match(['sub1', 'aaa.c'], "aaa.l\n%s\n" % lexflags, mode='r')

# NOTE: this behavior is "wrong" but we're keeping it for compat.
# the generated files should go into 'sub1', not the topdir.
test.must_match(['header.h'], 'lex header\n')
test.must_match(['tables.t'], 'lex table\n')

# To confirm the files from the file-output options were tracked,
# we should do a clean and make sure they got removed.
# As noted, they currently don't go into the tracked location,
# so using the check in the SConscript instead.
#test.run(arguments='-c .')
#test.must_not_exist(test.workpath(['sub1', 'header.h']))
#test.must_not_exist(test.workpath(['sub1', 'tables.t']))

sub2 = Path('sub2')
headerfile = sub2 / 'header.h'
tablefile = sub2 / 'tables.t'
lexflags = f' -x --header-file={headerfile} --tables-file={tablefile} -t'
if IS_WINDOWS and not sysconfig.get_platform() in ("mingw",):
    lexflags = ' --nounistd' + lexflags
# Read in with mode='r' because mylex.py implicitly wrote to stdout
# with mode='w'.
test.must_match(['sub2', 'aaa.c'], "aaa.l\n%s\n" % lexflags, mode='r')
test.must_match(['sub2', 'header.h'], 'lex header\n')
test.must_match(['sub2', 'tables.t'], 'lex table\n')

# To confirm the files from the file-output options were tracked,
# do a clean and make sure they got removed.
test.run(arguments='-c .', stderr=None)
test.must_not_exist(test.workpath('sub2', 'header.h'))
test.must_not_exist(test.workpath('sub2', 'tables.t'))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
