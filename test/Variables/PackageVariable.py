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
Test the PackageVariable canned Variable type.
"""


import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expect):
    result = test.stdout().split('\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)



test.write(SConstruct_path, """\
from SCons.Variables.PackageVariable import PackageVariable
PV = PackageVariable

from SCons.Variables import PackageVariable

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PackageVariable('x11',
                  'use X11 installed here (yes = search some places',
                  'yes'),
    PV('package', 'help for package', 'yes'),
    )

env = Environment(variables=opts)
Help(opts.GenerateHelpText(env))

print(env['x11'])
Default(env.Alias('dummy', None))
""")

test.run()
check([str(True)])

test.run(arguments='x11=no')
check([str(False)])

test.run(arguments='x11=0')
check([str(False)])

test.run(arguments=['x11=%s' % test.workpath()])
check([test.workpath()])

expect_stderr = """
scons: *** Path does not exist for option x11: /non/existing/path/
""" + test.python_file_line(SConstruct_path, 14)

test.run(arguments='x11=/non/existing/path/', stderr=expect_stderr, status=2)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
