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
Test the ListVariable canned Variable type.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expected):
    result = test.stdout().split('\n')
    r = result[1 : len(expected) + 1]
    assert r == expected, (r, expected)


test.write(SConstruct_path, """\
from SCons.Variables.ListVariable import ListVariable as LV
from SCons.Variables import ListVariable

list_of_libs = Split('x11 gl qt ical') + ["with space"]

optsfile = 'scons.variables'
opts = Variables(optsfile, args=ARGUMENTS)
opts.AddVariables(
    ListVariable(
        'shared',
        'libraries to build as shared libraries',
        default='all',
        names=list_of_libs,
        map={'GL': 'gl', 'QT': 'qt'},
    ),
    LV(
        'listvariable',
        'listvariable help',
        default='all',
        names=['l1', 'l2', 'l3'],
    ),
)

_ = DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts, tools=[])
opts.Save(optsfile, env)
Help(opts.GenerateHelpText(env))

print(env['shared'])

if 'ical' in env['shared']:
    print('1')
else:
    print('0')

print(",".join(env['shared']))

print(env.subst('$shared'))
# Test subst_path() because it's used in $CPPDEFINES expansions.
print(env.subst_path('$shared'))
Default(env.Alias('dummy', None))
""")

test.run()
check(
    [
        'all',
        '1',
        'gl,ical,qt,with space,x11',
        'gl ical qt with space x11',
        "['gl ical qt with space x11']",
    ]
)

expect = "shared = 'all'" + os.linesep + "listvariable = 'all'" + os.linesep
test.must_match(test.workpath('scons.variables'), expect)
check(
    [
        'all',
        '1',
        'gl,ical,qt,with space,x11',
        'gl ical qt with space x11',
        "['gl ical qt with space x11']",
    ]
)

test.run(arguments='shared=none')
check(['none', '0', '', '', "['']"])

test.run(arguments='shared=')
check(['none', '0', '', '', "['']"])

test.run(arguments='shared=x11,ical')
check(['ical,x11', '1', 'ical,x11', 'ical x11', "['ical x11']"])

test.run(arguments='shared=x11,,ical,,')
check(['ical,x11', '1', 'ical,x11', 'ical x11', "['ical x11']"])

test.run(arguments='shared=GL')
check(['gl', '0', 'gl', 'gl'])

test.run(arguments='shared=QT,GL')
check(['gl,qt', '0', 'gl,qt', 'gl qt', "['gl qt']"])

#test.run(arguments='shared="with space"')
#check(['with space', '0', 'with space', 'with space', "['with space']"])

expect_stderr = """
scons: *** Invalid value(s) for variable 'shared': 'foo'. Valid values are: gl,ical,qt,with space,x11,all,none
""" + test.python_file_line(SConstruct_path, 25)

test.run(arguments='shared=foo', stderr=expect_stderr, status=2)

# be paranoid in testing some more combinations

expect_stderr = """
scons: *** Invalid value(s) for variable 'shared': 'foo'. Valid values are: gl,ical,qt,with space,x11,all,none
""" + test.python_file_line(SConstruct_path, 25)

test.run(arguments='shared=foo,ical', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Invalid value(s) for variable 'shared': 'foo'. Valid values are: gl,ical,qt,with space,x11,all,none
""" + test.python_file_line(SConstruct_path, 25)

test.run(arguments='shared=ical,foo', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Invalid value(s) for variable 'shared': 'foo'. Valid values are: gl,ical,qt,with space,x11,all,none
""" + test.python_file_line(SConstruct_path, 25)

test.run(arguments='shared=ical,foo,x11', stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Invalid value(s) for variable 'shared': 'foo,bar'. Valid values are: gl,ical,qt,with space,x11,all,none
""" + test.python_file_line(SConstruct_path, 25)

test.run(arguments='shared=foo,x11,,,bar', stderr=expect_stderr, status=2)

test.write('SConstruct2', """\
from SCons.Variables import ListVariable

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    ListVariable(
        'gpib',
        'comment',
        default=['ENET', 'GPIB'],
        names=['ENET', 'GPIB', 'LINUX_GPIB', 'NO_GPIB'],
    ),
)

DefaultEnvironment(tools=[])  # test speedup
env = Environment(tools=[], variables=opts)
Help(opts.GenerateHelpText(env))

print(env['gpib'])
Default(env.Alias('dummy', None))
""")

test.run(
    arguments="-f SConstruct2",
    stdout=test.wrap_stdout(read_str="ENET,GPIB\n",
    build_str="""\
scons: Nothing to be done for `dummy'.
""")
)

test.pass_test()
