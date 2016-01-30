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
Test the PRINT_CMD_LINE_FUNC construction variable.
"""

import TestSCons

_exe = TestSCons._exe
_obj = TestSCons._obj

test = TestSCons.TestSCons(match = TestSCons.match_re)


test.write('SConstruct', r"""
import sys
def print_cmd_line(s, target, source, env):
    sys.stdout.write("BUILDING %s from %s with %s\n"%
                     (str(target[0]), str(source[0]), s))

e = Environment(PRINT_CMD_LINE_FUNC=print_cmd_line)
e.Program(target = 'prog', source = 'prog.c')
""")

test.write('prog.c', r"""
int main(int argc, char *argv[]) { return 0; }
""")

test.run(arguments = '-Q .')

expected_lines = [
    "BUILDING prog%s from prog.c with" % (_obj,),
    "BUILDING prog%s from prog%s with" % (_exe, _obj),
]

test.must_contain_all_lines(test.stdout(), expected_lines)

test.run(arguments = '-c .')

# Just make sure it doesn't blow up when PRINT_CMD_LINE_FUNC
# is explicity initialized to None.
test.write('SConstruct', r"""
e = Environment(PRINT_CMD_LINE_FUNC=None)
e.Program(target = 'prog', source = 'prog.c')
""")

test.run(arguments = '-Q .')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
