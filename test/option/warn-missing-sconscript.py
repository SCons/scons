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
Verify use of the --warn=missing-sconscript option.
"""

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)


test.write("SConstruct", """\
def build(target, source, env):
    pass

env=Environment()
env['BUILDERS']['test'] = Builder(action=build)
env.test(target='foo', source='foo.c')
WARN = ARGUMENTS.get('WARN')
if WARN:
    SetOption('warn', WARN)
SConscript('no_such_file')
""")

test.write("foo.c","""
#include "not_there.h"
""")

expect = r"""
scons: warning: Calling missing SConscript without error is deprecated.
Transition by adding must_exist=0 to SConscript calls.
Missing SConscript 'no_such_file'
""" + TestSCons.file_expr

# this is the old message:
#expect = r"""
#scons: warning: Ignoring missing SConscript 'no_such_file'
"" + TestSCons.file_expr

test.run(arguments = '--warn=missing-sconscript .', stderr = expect)

test.run(arguments = '--warn=no-missing-sconscript .', stderr = "")

test.run(arguments = 'WARN=missing-sconscript .', stderr = expect)

test.run(arguments = 'WARN=no-missing-sconscript .', stderr = "")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
