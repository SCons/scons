#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import string
import TestSCons

test = TestSCons.TestSCons()

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text.\n")
""")

expect = "Help text.\n\nUse scons -H for help about command-line options.\n"

os.environ['SCONSFLAGS'] = ''

test.run(arguments = '-h', stdout = expect)

os.environ['SCONSFLAGS'] = '-h'

test.run(stdout = expect)

test.run(arguments = "-H")

test.fail_test(string.find(test.stdout(), 'Help text.') >= 0)
test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

os.environ['SCONSFLAGS'] = '-Z'

test.run(arguments = "-H", stderr = r"""
SCons warning: SCONSFLAGS option -Z not recognized
File "[^"]*", line \d+, in \S+
""")

test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

test.pass_test()
