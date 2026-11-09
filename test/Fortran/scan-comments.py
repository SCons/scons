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

"""Fortran comments must not introduce dependencies or unnecessary rebuilds."""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
from pathlib import Path
import SCons.Scanner.Fortran

DefaultEnvironment(tools=[])
env = Environment(tools=[], FORTRANMODSUFFIX='.mod', FORTRANPATH=[])

# Keep fixture output independent of platform newline translation.
def build(target, source, env):
    Path(str(target[0])).write_bytes(
        Path('real.mod').read_bytes() + Path('real.inc').read_bytes())

def copy_include(target, source, env):
    Path(str(target[0])).write_bytes(Path('real!file.inc').read_bytes())

env.Command('result', 'main.f90', build,
            source_scanner=SCons.Scanner.Fortran.FortranScan())
env.Command('quoted-result', 'quoted.f90', copy_include,
            source_scanner=SCons.Scanner.Fortran.FortranScan())
""")

test.write('main.f90', """\
! USE real; USE phantom
! INCLUDE 'real.inc'; INCLUDE 'phantom.inc'
USE real !; USE phantom
INCLUDE 'real.inc' !; INCLUDE 'phantom.inc'
""")

for filename in ['real.mod', 'real.inc', 'phantom.mod', 'phantom.inc']:
    test.write(filename, filename + ' 1\n')

test.run(arguments='result')
test.must_match('result', 'real.mod 1\nreal.inc 1\n')

# Existing files are essential: missing phantom files hide false dependencies.
for filename in ['phantom.mod', 'phantom.inc']:
    test.write(filename, filename + ' 2\n')
    test.up_to_date(arguments='result')

test.write('real.mod', 'real.mod 2\n')
test.run(arguments='result')
test.must_match('result', 'real.mod 2\nreal.inc 1\n')

test.write('real.inc', 'real.inc 2\n')
test.run(arguments='result')
test.must_match('result', 'real.mod 2\nreal.inc 2\n')
test.up_to_date(arguments='result')

test.write('quoted.f90', """\
program p
print *, &
     'a'
     include 'real!file.inc'
end
""")
test.write('real!file.inc', 'real include 1\n')
test.run(arguments='quoted-result')
test.must_match('quoted-result', 'real include 1\n')
test.write('real!file.inc', 'real include 2\n')
test.run(arguments='quoted-result')
test.must_match('quoted-result', 'real include 2\n')
test.up_to_date(arguments='quoted-result')

test.pass_test()
