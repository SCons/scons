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
Test the ListVariable canned Variable type.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expect):
    result = test.stdout().split('\n')
    r = result[1:len(expect)+1]
    assert r == expect, (r, expect)



test.write(SConstruct_path, """\
from SCons.Variables.ListVariable import ListVariable
LV = ListVariable

from SCons.Variables import ListVariable

list_of_libs = Split('x11 gl qt ical')

optsfile = 'scons.variables'
opts = Variables(optsfile, args=ARGUMENTS)
opts.AddVariables(
    ListVariable('shared',
               'libraries to build as shared libraries',
               'all',
               names = list_of_libs,
               map = {'GL':'gl', 'QT':'qt'}),
    LV('listvariable', 'listvariable help', 'all', names=['l1', 'l2', 'l3'])
    )

env = Environment(variables=opts)
opts.Save(optsfile, env)
Help(opts.GenerateHelpText(env))

print(env['shared'])

if 'ical' in env['shared']:
    print('1')
else:
    print('0')

print(" ".join(env['shared']))

print(env.subst('$shared'))
# Test subst_path() because it's used in $CPPDEFINES expansions.
print(env.subst_path('$shared'))
Default(env.Alias('dummy', None))
""")

test.run()
check(['all', '1', 'gl ical qt x11', 'gl ical qt x11',
       "['gl ical qt x11']"])

expect = "shared = 'all'"+os.linesep+"listvariable = 'all'"+os.linesep
test.must_match(test.workpath('scons.variables'), expect)

check(['all', '1', 'gl ical qt x11', 'gl ical qt x11',
       "['gl ical qt x11']"])

test.run(arguments='shared=none')
check(['none', '0', '', '', "['']"])

test.run(arguments='shared=')
check(['none', '0', '', '', "['']"])

test.run(arguments='shared=x11,ical')
check(['ical,x11', '1', 'ical x11', 'ical x11',
       "['ical x11']"])

test.run(arguments='shared=x11,,ical,,')
check(['ical,x11', '1', 'ical x11', 'ical x11',
       "['ical x11']"])

test.run(arguments='shared=GL')
check(['gl', '0', 'gl', 'gl'])

test.run(arguments='shared=QT,GL')
check(['gl,qt', '0', 'gl qt', 'gl qt', "['gl qt']"])


expect_stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
""" + test.python_file_line(SConstruct_path, 19)

test.run(arguments='shared=foo', stderr=expect_stderr, status=2)

# be paranoid in testing some more combinations

expect_stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
""" + test.python_file_line(SConstruct_path, 19)

test.run(arguments='shared=foo,ical', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
""" + test.python_file_line(SConstruct_path, 19)

test.run(arguments='shared=ical,foo', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
""" + test.python_file_line(SConstruct_path, 19)

test.run(arguments='shared=ical,foo,x11', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo,bar
""" + test.python_file_line(SConstruct_path, 19)

test.run(arguments='shared=foo,x11,,,bar', stderr=expect_stderr, status=2)



test.write('SConstruct', """
from SCons.Variables import ListVariable

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    ListVariable('gpib',
               'comment',
               ['ENET', 'GPIB'],
               names = ['ENET', 'GPIB', 'LINUX_GPIB', 'NO_GPIB']),
    )

env = Environment(variables=opts)
Help(opts.GenerateHelpText(env))

print(env['gpib'])
Default(env.Alias('dummy', None))
""")

test.run(stdout=test.wrap_stdout(read_str="ENET,GPIB\n", build_str="""\
scons: Nothing to be done for `dummy'.
"""))



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
