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
Test that setting illegal construction variables fails in ways that are
useful to the user.
"""

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')
SConscript_path = test.workpath('SConscript')

test.write(SConstruct_path, """\
env = Environment()
env['foo-bar'] = 1
""")

expect_stderr = """
scons: *** Illegal construction variable `foo-bar'
""" + test.python_file_line(SConstruct_path, 2)

test.run(arguments='.', status=2, stderr=expect_stderr)



test.write(SConstruct_path, """\
SConscript('SConscript')
""")

test.write('SConscript', """\
env = Environment()
env['foo(bar)'] = 1
""")


expect_stderr = """
scons: *** Illegal construction variable `foo(bar)'
""" + test.python_file_line(SConscript_path, 2)

test.run(arguments='.', status=2, stderr=expect_stderr)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
