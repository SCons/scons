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

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

not_executable = test.workpath("not_executable")

test.write(not_executable, "\n")

test.write("f1.in", "\n")

bad_command = """\
Bad command or file name
"""

unrecognized = """\
'.+' is not recognized as an internal or external command,
operable program or batch file.
scons: \\*\\*\\* \\[%s\\] Error 1
"""

unspecified = """\
The name specified is not recognized as an
internal or external command, operable program or batch file.
scons: \\*\\*\\* \\[%s\\] Error 1
"""

cannot_execute = """\
(sh: )*.+: cannot execute( \\[Permission denied\\])?
scons: \\*\\*\\* \\[%s\\] Error %s
"""

permission_denied = """\
.+: (p|P)ermission denied
scons: \\*\\*\\* \\[%s\\] Error %s
"""

konnte_nicht_gefunden_werden = """\
Der Befehl ".+" ist entweder falsch geschrieben oder
konnte nicht gefunden werden.
scons: \\*\\*\\* \\[%s\\] Error %s
"""

test.write('SConstruct', r"""
bld = Builder(action = '%s $SOURCES $TARGET')
env = Environment(BUILDERS = { 'bld': bld })
env.bld(target = 'f1', source = 'f1.in')
""" % not_executable.replace('\\', '\\\\'))

test.run(arguments='.',
         stdout = test.wrap_stdout("%s f1.in f1\n" % not_executable, error=1),
         stderr = None,
         status = 2)

test.description_set("Incorrect STDERR:\n%s\n" % test.stderr())
if os.name == 'nt':
    errs = [
        bad_command,
        unrecognized % 'f1',
        konnte_nicht_gefunden_werden % ('f1', 1),
        unspecified % 'f1'
    ]
else:
    errs = [
        cannot_execute % ('f1', 126),
        permission_denied % ('f1', 126),
    ]

test.must_contain_any_line(test.stderr(), errs, find=TestSCons.search_re)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
