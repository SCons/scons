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
Verify that when an option is specified which takes args,
those do not end up treated as targets.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=1,
    dest='extra',
    action='store',
    type='string',
    metavar='ARG1',
    default=(),
    help='An argument to the option',
)
print(str(GetOption('extra')))
print(COMMAND_LINE_TARGETS)
""",
)

# arg using =
test.run('-Q -q --extra=A TARG', status=1, stdout=r"A\n\['TARG'\]\n")
# arg not using =
test.run('-Q -q --extra A TARG', status=1, stdout=r"A\n\['TARG'\]\n")
# short arg with space
test.run('-Q -q -x A TARG', status=1, stdout=r"A\n\['TARG'\]\n")
# short arg with no space
test.run('-Q -q -xA TARG', status=1, stdout=r"A\n\['TARG'\]\n")

test.write('SConstruct1', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=2,
    dest='extra',
    action='append',
    type='string',
    metavar='ARG1',
    default=[],
    help='An argument to the option',
)
print(str(GetOption('extra')))
print(COMMAND_LINE_TARGETS)
""",
)

# many args and opts
test.run(
    '-f SConstruct1 -Q -q --extra=A B TARG1 -x C D TARG2 -xE F TARG3 --extra G H TARG4',
    status=1,
    stdout=r"\[\('A', 'B'\), \('C', 'D'\), \('E', 'F'\), \('G', 'H'\)\]\n\['TARG1', 'TARG2', 'TARG3', 'TARG4'\]\n",
)

test.write('SConstruct2', """\
DefaultEnvironment(tools=[])
AddOption('-x', '--extra',
          nargs=1,
          dest='extra',
          action='store',
          type='string',
          metavar='ARG1',
          default=(),
          help='An argument to the option')
print(str(GetOption('extra')))
print(COMMAND_LINE_TARGETS)
print(ARGUMENTS.get('A', None))
""",
)

# opt value and target are same name
test.run(
    arguments='-f SConstruct2 -Q -q --extra=TARG1 TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q --extra TARG1 TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -xTARG1 TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -x TARG1 TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)

# target first
test.run(
    arguments='-f SConstruct2 -Q -q TARG1 --extra=TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q TARG1 --extra TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q TARG1 -xTARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q TARG1 -x TARG1',
    status=1,
    stdout=r"TARG1\n\['TARG1'\]\nNone\n",
)

# equals in opt value
test.run(
    arguments='-f SConstruct2 -Q -q --extra=A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q --extra A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -xA=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nNone\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -x A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nNone\n",
)

# equals in opt value and a different argument
test.run(
    arguments='-f SConstruct2 -Q -q --extra=A=B A=C TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q --extra A=B A=C TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -xA=B A=C TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -x A=B A=C TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)

# different argument first
test.run(
    arguments='-f SConstruct2 -Q -q A=C --extra=A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=C --extra A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=C -xA=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=C -x A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nC\n",
)

# equals in opt value and the same as an argument
test.run(
    arguments='-f SConstruct2 -Q -q --extra=A=B A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q --extra A=B A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -xA=B A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q -x A=B A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)

# same argument first
test.run(
    arguments='-f SConstruct2 -Q -q A=B --extra=A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=B --extra A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=B -xA=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)
test.run(
    arguments='-f SConstruct2 -Q -q A=B -x A=B TARG1',
    status=1,
    stdout=r"A=B\n\['TARG1'\]\nB\n",
)

test.write('SConstruct3', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=1,
    dest='extra',
    action='store',
    type='string',
    metavar='ARG1',
    default=(),
    help='An argument to the option',
)
if 'A' in BUILD_TARGETS:
    BUILD_TARGETS.append('B')
print(str(GetOption('extra')))
print(BUILD_TARGETS)
""",
)

# Nested target
test.run(
    arguments='-f SConstruct3 -Q -q -x A TARG1', status=1, stdout=r"A\n\['TARG1'\]\n"
)
test.run(
    arguments='-f SConstruct3 -Q -q -x A A TARG1',
    status=1,
    stdout=r"A\n\['A', 'TARG1', 'B'\]\n",
)
test.run(
    arguments='-f SConstruct3 -Q -q A -x A TARG1',
    status=1,
    stdout=r"A\n\['A', 'TARG1', 'B'\]\n",
)

test.write('SConstruct4', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=1,
    dest='extra',
    action='store',
    type='string',
    metavar='ARG1',
    default=(),
    help='An argument to the option',
)
if 'A' in BUILD_TARGETS:
    AddOption(
        '--foo',
        nargs=1,
        dest='foo',
        action='store',
        type='string',
        metavar='FOO1',
        default=(),
        help='An argument to the option',
    )
print(str(GetOption('extra')))
print(str(GetOption('foo')))
print(COMMAND_LINE_TARGETS)
""",
)

# nested option
expect = r"""AttributeError: 'Values' object has no attribute 'foo':
  File ".+SConstruct4", line \d+:
    print\(str\(GetOption\('foo'\)\)\)
  File "[^"]+Main.py", line \d+:
    return getattr\(OptionsParser.values, name\)
  File "[^"]+SConsOptions.py", line \d+:
    return getattr\(self.__dict__\['__defaults__'\], attr\)
"""
test.run(
    arguments='-f SConstruct4 -Q -q -x A --foo=C TARG1',
    status=2,
    stdout=r"A\n",
    stderr=expect,
)
test.run(
    arguments='-f SConstruct4 -Q -q -x A A --foo=C TARG1',
    status=1,
    stdout=r"A\nC\n\['A', 'TARG1'\]\n",
)
test.run(
    arguments='-f SConstruct4 -Q -q A -x A --foo=C TARG1',
    status=1,
    stdout=r"A\nC\n\['A', 'TARG1'\]\n",
)

############################################
################ Fail Case #################
############################################

test.write('SConstruct5', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=1,
    dest='extra',
    action='store',
    type='string',
    metavar='ARG1',
    default=(),
    help='An argument to the option',
)
if 'A' in BUILD_TARGETS:
    BUILD_TARGETS.append('B')
print(str(GetOption('extra')))
print(BUILD_TARGETS)
""")

# Nested target
test.run(
    arguments='-f SConstruct5 -Q -q -x A TARG1', status=1, stdout=r"A\n\['TARG1'\]\n"
)
test.run(
    arguments='-f SConstruct5 -Q -q -x A A TARG1',
    status=1,
    stdout=r"A\n\['A', 'TARG1', 'B'\]\n",
)
test.run(
    arguments='-f SConstruct5 -Q -q A -x A TARG1',
    status=1,
    stdout=r"A\n\['A', 'TARG1', 'B'\]\n",
)

test.write('SConstruct6', """\
DefaultEnvironment(tools=[])
AddOption(
    '-x',
    '--extra',
    nargs=1,
    dest='extra',
    action='store',
    type='string',
    metavar='ARG1',
    default=(),
    help='An argument to the option',
)
if 'A' in BUILD_TARGETS:
    AddOption(
        '--foo',
        nargs=1,
        dest='foo',
        action='store',
        type='string',
        metavar='FOO1',
        default=(),
        help='An argument to the option',
    )
print(str(GetOption('extra')))
print(str(GetOption('foo')))
print(COMMAND_LINE_TARGETS)
""")

# nested option
expect=r"""AttributeError: 'Values' object has no attribute 'foo':
  File ".+SConstruct6", line \d+:
    print\(str\(GetOption\('foo'\)\)\)
  File "[^"]+Main.py", line \d+:
    return getattr\(OptionsParser.values, name\)
  File "[^"]+SConsOptions.py", line \d+:
    return getattr\(self.__dict__\['__defaults__'\], attr\)
"""
test.run(
    arguments='-f SConstruct6 -Q -q -x A --foo=C TARG1',
    status=2,
    stdout=r"A\n",
    stderr=expect,
)
test.run(
    arguments='-f SConstruct6 -Q -q -x A A --foo=C TARG1',
    status=1,
    stdout=r"A\nC\n\['A', 'TARG1'\]\n",
)
test.run(
    arguments='-f SConstruct6 -Q -q A -x A --foo=C TARG1',
    status=1,
    stdout=r"A\nC\n\['A', 'TARG1'\]\n",
)

test.pass_test()
