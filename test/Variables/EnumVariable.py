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
Test the EnumVariable canned Variable type.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expect):
    result = test.stdout().split('\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)



test.write(SConstruct_path, """\
from SCons.Variables.EnumVariable import EnumVariable
EV = EnumVariable

from SCons.Variables import EnumVariable

list_of_libs = Split('x11 gl qt ical')

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    EnumVariable('debug', 'debug output and symbols', 'no',
               allowed_values=('yes', 'no', 'full'),
               map={}, ignorecase=0),  # case sensitive
    EnumVariable('guilib', 'gui lib to use', 'gtk',
               allowed_values=('motif', 'gtk', 'kde'),
               map={}, ignorecase=1), # case insensitive
    EV('some', 'some option', 'xaver',
       allowed_values=('xaver', 'eins'),
       map={}, ignorecase=2), # make lowercase
    )

env = Environment(variables=opts)
Help(opts.GenerateHelpText(env))

print(env['debug'])
print(env['guilib'])
print(env['some'])

Default(env.Alias('dummy', None))
""")


test.run(); check(['no', 'gtk', 'xaver'])

test.run(arguments='debug=yes guilib=Motif some=xAVER')
check(['yes', 'Motif', 'xaver'])

test.run(arguments='debug=full guilib=KdE some=EiNs')
check(['full', 'KdE', 'eins'])

expect_stderr = """
scons: *** Invalid value for option debug: FULL.  Valid values are: ('yes', 'no', 'full')
""" + test.python_file_line(SConstruct_path, 21)

test.run(arguments='debug=FULL', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Invalid value for option guilib: irgendwas.  Valid values are: ('motif', 'gtk', 'kde')
""" + test.python_file_line(SConstruct_path, 21)

test.run(arguments='guilib=IrGeNdwas', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Invalid value for option some: irgendwas.  Valid values are: ('xaver', 'eins')
""" + test.python_file_line(SConstruct_path, 21)

test.run(arguments='some=IrGeNdwas', stderr=expect_stderr, status=2)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
