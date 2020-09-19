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
Verify that when an option is specified which takes args,
those do not end up treated as targets.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()
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
""")

# arg using =
test.run('-Q -q --extra=A TARG', status=1, stdout="A\n['TARG']\n")
# arg not using =
test.run('-Q -q --extra A TARG', status=1, stdout="A\n['TARG']\n")
# short arg with space
test.run('-Q -q -x A TARG', status=1, stdout="A\n['TARG']\n")
# short arg with no space
test.run('-Q -q -xA TARG', status=1, stdout="A\n['TARG']\n")

test.write('SConstruct', """\
env = Environment()
AddOption('-x', '--extra',
          nargs=2,
          dest='extra',
          action='append',
          type='string',
          metavar='ARG1',
          default=[],
          help='An argument to the option')
print(str(GetOption('extra')))
print(COMMAND_LINE_TARGETS)
""")

# many args and opts
test.run('-Q -q --extra=A B TARG1 -x C D TARG2 -xE F TARG3 --extra G H TARG4', 
        status=1, stdout="[('A', 'B'), ('C', 'D'), ('E', 'F'), ('G', 'H')]\n['TARG1', 'TARG2', 'TARG3', 'TARG4']\n")

test.write('SConstruct', """\
env = Environment()
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
""")

# opt value and target are same name
test.run('-Q -q --extra=TARG1 TARG1', status=1, stdout="TARG1\n['TARG1']\n")
test.run('-Q -q --extra TARG1 TARG1', status=1, stdout="TARG1\n['TARG1']\n")
test.run('-Q -q -xTARG1 TARG1', status=1, stdout="TARG1\n['TARG1']\n")
test.run('-Q -q -x TARG1 TARG1', status=1, stdout="TARG1\n['TARG1']\n")

# equals in opt value
test.run('-Q -q --extra=A=B TARG1', status=1, stdout="A=B\n['TARG1']\n")
test.run('-Q -q --extra A=B TARG1', status=1, stdout="A=B\n['TARG1']\n")
test.run('-Q -q -xA=B TARG1', status=1, stdout="A=B\n['TARG1']\n")
test.run('-Q -q -x A=B TARG1', status=1, stdout="A=B\n['TARG1']\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4: