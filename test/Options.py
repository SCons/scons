#!/usr/bin/env python
#
# Copyright (c) 2001, 2002 Steven Knight
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

import TestSCons
import string

test = TestSCons.TestSCons()

test.write('SConstruct', """
env = Environment()
print env['CC']
print env['CCFLAGS']
Default(env.Alias('dummy'))
""")
test.run()
cc, ccflags = string.split(test.stdout(), '\n')[1:3]

test.write('SConstruct', """
opts = Options('custom.py')
opts.Add('RELEASE_BUILD',
         'Set to 1 to build a release build',
         0,
         None,
         int)

opts.Add('DEBUG_BUILD',
         'Set to 1 to build a debug build',
         1,
         None,
         int)

opts.Add('CC',
         'The C compiler')

def test_tool(env, platform):
    if env['RELEASE_BUILD']:
        env['CCFLAGS'] = env['CCFLAGS'] + ' -O'
    if env['DEBUG_BUILD']:
        env['CCFLAGS'] = env['CCFLAGS'] + ' -g'
    

env = Environment(options=opts, tools=['default', test_tool])

Help('Variables settable in custom.py or on the command line:\\n' + opts.GenerateHelpText(env))

print env['RELEASE_BUILD']
print env['DEBUG_BUILD']
print env['CC']
print env['CCFLAGS']

Default(env.Alias('dummy'))
        
""")

def check(expect):
    result = string.split(test.stdout(), '\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

test.run()
check(['0', '1', cc, ccflags + ' -g'])

test.run(arguments='"RELEASE_BUILD=1"')
check(['1', '1', cc, ccflags + ' -O -g'])

test.run(arguments='"RELEASE_BUILD=1" "DEBUG_BUILD=0"')
check(['1', '0', cc, ccflags + ' -O'])

test.run(arguments='"CC=not_a_c_compiler"')
check(['0', '1', 'not_a_c_compiler', ccflags + ' -g'])

test.write('custom.py', """
DEBUG_BUILD=0
RELEASE_BUILD=1
""")

test.run()
check(['1', '0', cc, ccflags + ' -O'])

test.run(arguments='"DEBUG_BUILD=1"')
check(['1', '1', cc, ccflags + ' -O -g'])
   
test.run(arguments='-h',
         stdout = """scons: Reading SConscript files ...
scons: done reading SConscript files.
Variables settable in custom.py or on the command line:

RELEASE_BUILD: Set to 1 to build a release build
    default: 0
    actual: 1

DEBUG_BUILD: Set to 1 to build a debug build
    default: 1
    actual: 0

CC: The C compiler
    default: None
    actual: %s

Use scons -H for help about command-line options.
"""%cc)

test.pass_test()
