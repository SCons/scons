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
Verify added options give the expected default/command line values
when fetched with GetOption.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
from SCons.Script.SConsOptions import SConsOption

DefaultEnvironment(tools=[])
env = Environment(tools=[])
AddOption(
    '-F', '--force',
    action="store_true",
    help='force installation (overwrite any existing files)',
)
AddOption(
    '--prefix',
    nargs=1,
    dest='prefix',
    action='store',
    type='string',
    metavar='DIR',
    settable=True,
    help='installation prefix',
)
AddOption(
    '--set',
    action="store_true",
    help="try SetOption of 'prefix' to '/opt/share'"
)
z_opt = SConsOption("--zcount", type="int", nargs=1, settable=True)
AddOption(z_opt)

f = GetOption('force')
if f:
    f = "True"
print(f)
print(GetOption('prefix'))
if GetOption('set'):
    SetOption('prefix', '/opt/share')
    print(GetOption('prefix'))
if GetOption('zcount'):
    print(GetOption('zcount'))
""")

test.run('-Q -q .', stdout="None\nNone\n")
test.run('-Q -q . --force', stdout="True\nNone\n")
test.run('-Q -q . -F', stdout="True\nNone\n")
test.run('-Q -q . --prefix=/home/foo', stdout="None\n/home/foo\n")
test.run('-Q -q . -- --prefix=/home/foo --force', status=1, stdout="None\nNone\n")
# check that SetOption works on prefix...
test.run('-Q -q . --set', stdout="None\nNone\n/opt/share\n")
# but the "command line wins" rule is not violated
test.run('-Q -q . --set --prefix=/home/foo', stdout="None\n/home/foo\n/home/foo\n")
# also try in case we pass a premade option object to AddOption
test.run('-Q -q . --zcount=22', stdout="None\nNone\n22\n")

test.pass_test()
