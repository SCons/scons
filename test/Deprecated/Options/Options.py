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

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

test.write('SConstruct', """
env = Environment()
print env['CC']
print " ".join(env['CCFLAGS'])
Default(env.Alias('dummy', None))
""")
test.run()
cc, ccflags = test.stdout().split('\n')[1:3]

test.write('SConstruct', """
# test validator.  Change a key and add a new one to the environment
def validator(key, value, environ):
    environ[key] = "v"
    environ["valid_key"] = "v"


def old_converter (value):
    return "old_converter"

def new_converter (value, env):
    return "new_converter"


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

opts.Add('VALIDATE',
         'An option for testing validation',
         "notset",
         validator,
         None)

opts.Add('OLD_CONVERTER',
         'An option for testing converters that take one parameter',
         "foo",
         None,
         old_converter)

opts.Add('NEW_CONVERTER',
         'An option for testing converters that take two parameters',
         "foo",
         None,
         new_converter)

opts.Add('UNSPECIFIED',
         'An option with no value')

def test_tool(env):
    if env['RELEASE_BUILD']:
        env.Append(CCFLAGS = '-O')
    if env['DEBUG_BUILD']:
        env.Append(CCFLAGS = '-g')


env = Environment(options=opts, tools=['default', test_tool])

Help('Variables settable in custom.py or on the command line:\\n' + opts.GenerateHelpText(env))

print env['RELEASE_BUILD']
print env['DEBUG_BUILD']
print env['CC']
print " ".join(env['CCFLAGS'])
print env['VALIDATE']
print env['valid_key']

# unspecified options should not be set:
assert 'UNSPECIFIED' not in env

# undeclared options should be ignored:
assert 'UNDECLARED' not in env

# calling Update() should not effect options that
# are not declared on the options object:
r = env['RELEASE_BUILD']
opts = Options()
opts.Update(env)
assert env['RELEASE_BUILD'] == r

Default(env.Alias('dummy', None))

""")

warnings = """
scons: warning: The Options class is deprecated; use the Variables class instead.
""" + TestSCons.file_expr


def check(expect):
    result = test.stdout().split('\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

test.run(stderr=warnings)
check(['0', '1', cc, (ccflags + ' -g').strip(), 'v', 'v'])

test.run(arguments='RELEASE_BUILD=1', stderr=warnings)
check(['1', '1', cc, (ccflags + ' -O -g').strip(), 'v', 'v'])

test.run(arguments='RELEASE_BUILD=1 DEBUG_BUILD=0', stderr=warnings)
check(['1', '0', cc, (ccflags + ' -O').strip(), 'v', 'v'])

test.run(arguments='CC=not_a_c_compiler', stderr=warnings)
check(['0', '1', 'not_a_c_compiler', (ccflags + ' -g').strip(), 'v', 'v'])

test.run(arguments='UNDECLARED=foo', stderr=warnings)
check(['0', '1', cc, (ccflags + ' -g').strip(), 'v', 'v'])

test.run(arguments='CCFLAGS=--taco', stderr=warnings)
check(['0', '1', cc, (ccflags + ' -g').strip(), 'v', 'v'])

test.write('custom.py', """
DEBUG_BUILD=0
RELEASE_BUILD=1
""")

test.run(stderr=warnings)
check(['1', '0', cc, (ccflags + ' -O').strip(), 'v', 'v'])

test.run(arguments='DEBUG_BUILD=1', stderr=warnings)
check(['1', '1', cc, (ccflags + ' -O -g').strip(), 'v', 'v'])

test.run(arguments='-h',
         stdout = """\
scons: Reading SConscript files ...
1
0
%s
%s
v
v
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

VALIDATE: An option for testing validation
    default: notset
    actual: v

OLD_CONVERTER: An option for testing converters that take one parameter
    default: foo
    actual: old_converter

NEW_CONVERTER: An option for testing converters that take two parameters
    default: foo
    actual: new_converter

UNSPECIFIED: An option with no value
    default: None
    actual: None

Use scons -H for help about command-line options.
"""%(cc, ccflags and ccflags + ' -O' or '-O', cc),
         stderr=warnings)

# Test saving of options and multi loading
#
test.write('SConstruct', """
opts = Options(['custom.py', 'options.saved'])
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

opts.Add('UNSPECIFIED',
         'An option with no value')

env = Environment(options = opts)

print env['RELEASE_BUILD']
print env['DEBUG_BUILD']

opts.Save('options.saved', env)
""")

# Check the save file by executing and comparing against
# the expected dictionary
def checkSave(file, expected):
    gdict = {}
    ldict = {}
    exec(open(file, 'rU').read(), gdict, ldict)
    assert expected == ldict, "%s\n...not equal to...\n%s" % (expected, ldict)

# First test with no command line options
# This should just leave the custom.py settings
test.run(stderr=warnings)
check(['1','0'])
checkSave('options.saved', { 'RELEASE_BUILD':1, 'DEBUG_BUILD':0})

# Override with command line arguments
test.run(arguments='DEBUG_BUILD=3', stderr=warnings)
check(['1','3'])
checkSave('options.saved', {'RELEASE_BUILD':1, 'DEBUG_BUILD':3})

# Now make sure that saved options are overridding the custom.py
test.run(stderr=warnings)
check(['1','3'])
checkSave('options.saved', {'DEBUG_BUILD':3, 'RELEASE_BUILD':1})

# Load no options from file(s)
# Used to test for correct output in save option file
test.write('SConstruct', """
opts = Options()
opts.Add('RELEASE_BUILD',
         'Set to 1 to build a release build',
         '0',
         None,
         int)

opts.Add('DEBUG_BUILD',
         'Set to 1 to build a debug build',
         '1',
         None,
         int)

opts.Add('UNSPECIFIED',
         'An option with no value')

opts.Add('LISTOPTION_TEST',
         'testing list option persistence',
         'none',
         names = ['a','b','c',])

env = Environment(options = opts)

print env['RELEASE_BUILD']
print env['DEBUG_BUILD']
print env['LISTOPTION_TEST']

opts.Save('options.saved', env)
""")

# First check for empty output file when nothing is passed on command line
test.run(stderr=warnings)
check(['0','1'])
checkSave('options.saved', {})

# Now specify one option the same as default and make sure it doesn't write out
test.run(arguments='DEBUG_BUILD=1', stderr=warnings)
check(['0','1'])
checkSave('options.saved', {})

# Now specify same option non-default and make sure only it is written out
test.run(arguments='DEBUG_BUILD=0 LISTOPTION_TEST=a,b', stderr=warnings)
check(['0','0'])
checkSave('options.saved',{'DEBUG_BUILD':0, 'LISTOPTION_TEST':'a,b'})

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

opts.Add('UNSPECIFIED',
         'An option with no value')

env = Environment(options=opts)

Help('Variables settable in custom.py or on the command line:\\n' + opts.GenerateHelpText(env,sort=cmp))

""")

test.run(arguments='-h',
         stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
Variables settable in custom.py or on the command line:

CC: The C compiler
    default: None
    actual: %s

DEBUG_BUILD: Set to 1 to build a debug build
    default: 1
    actual: 0

RELEASE_BUILD: Set to 1 to build a release build
    default: 0
    actual: 1

UNSPECIFIED: An option with no value
    default: None
    actual: None

Use scons -H for help about command-line options.
"""%cc,
         stderr=warnings)

test.write('SConstruct', """
import SCons.Options
env1 = Environment(options = Options())
env2 = Environment(options = SCons.Options.Options())
""")

test.run(stderr=warnings)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
