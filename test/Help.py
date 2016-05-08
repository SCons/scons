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

test = TestSCons.TestSCons()

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text\ngoes here.\n")
""")

expect = """scons: Reading SConscript files ...
scons: done reading SConscript files.
Help text
goes here.

Use scons -H for help about command-line options.
"""

test.run(arguments = '-h', stdout = expect)

test.write('SConstruct', r"""
env = Environment(MORE='more', HELP='help')
env.Help("\nEven $MORE\n$HELP text!\n")
""")

expect = """scons: Reading SConscript files ...
scons: done reading SConscript files.

Even more
help text!

Use scons -H for help about command-line options.
"""

test.run(arguments = '-h', stdout = expect)

test.write('SConstruct', r"""
Help('\nMulti')
Help('line\n')
Help('''\
help
text!
''')
""")

expect = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.

Multiline
help
text!

Use scons -H for help about command-line options.
"""

test.run(arguments = '-h', stdout = expect)

# Bug #2831 - append flag to Help doesn't wipe out addoptions and variables used together
test.write('SConstruct', r"""

AddOption('--debugging',
	dest='debugging',
	action='store_true',
	default=False,
	metavar='BDEBUGGING',
	help='Compile with debugging symbols')

vars = Variables()
vars.Add(ListVariable('buildmod', 'List of modules to build', 'none',
                    ['python']))

env = Environment()

Help(vars.GenerateHelpText(env),append=True)
""")

expect = ".*--debugging.*Compile with debugging symbols.*buildmod: List of modules to build.*"

test.run(arguments = '-h', stdout = expect, match=TestSCons.match_re_dotall)


# Bug 2831
# This test checks to verify that append=False doesn't include anything
# but the expected help for the specified Variable()

test.write('SConstruct', r"""

AddOption('--debugging',
	dest='debugging',
	action='store_true',
	default=False,
	metavar='BDEBUGGING',
	help='Compile with debugging symbols')

vars = Variables()
vars.Add(ListVariable('buildmod', 'List of modules to build', 'none',
                    ['python']))

env = Environment()

Help(vars.GenerateHelpText(env),append=False)
""")

expect = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.

buildmod: List of modules to build
    (all|none|comma-separated list of names)
    allowed names: python
    default: none
    actual: None

Use scons -H for help about command-line options.
"""

test.run(arguments = '-h', stdout = expect)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
