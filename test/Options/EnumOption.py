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
Test the EnumOption canned Option type.
"""

import os.path
import string

import TestSCons

test = TestSCons.TestSCons()

def check(expect):
    result = string.split(test.stdout(), '\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)



test.write('SConstruct', """
from SCons.Options import EnumOption

list_of_libs = Split('x11 gl qt ical')

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    EnumOption('debug', 'debug output and symbols', 'no',
               allowed_values=('yes', 'no', 'full'),
               map={}, ignorecase=0),  # case sensitive
    EnumOption('guilib', 'gui lib to use', 'gtk',
               allowed_values=('motif', 'gtk', 'kde'),
               map={}, ignorecase=1), # case insensitive
    EnumOption('some', 'some option', 'xaver',
               allowed_values=('xaver', 'eins'),
               map={}, ignorecase=2), # make lowercase
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['debug']
print env['guilib']
print env['some']

Default(env.Alias('dummy', None))
""")


test.run(); check(['no', 'gtk', 'xaver'])
test.run(arguments='debug=yes guilib=Motif some=xAVER')
check(['yes', 'Motif', 'xaver'])
test.run(arguments='debug=full guilib=KdE some=EiNs')
check(['full', 'KdE', 'eins'])

test.run(arguments='debug=FULL',
         stderr = """
scons: *** Invalid value for option debug: FULL
File "SConstruct", line 19, in ?
""", status=2)

test.run(arguments='guilib=IrGeNdwas',
         stderr = """
scons: *** Invalid value for option guilib: irgendwas
File "SConstruct", line 19, in ?
""", status=2)

test.run(arguments='some=IrGeNdwas',
         stderr = """
scons: *** Invalid value for option some: irgendwas
File "SConstruct", line 19, in ?
""", status=2)


test.pass_test()
