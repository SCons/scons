#!/usr/bin/env python

__revision__ = "test/Help.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text\ngoes here.\n")
""")

test.run(arguments = '-h')

test.fail_test(test.stdout() != "Help text\ngoes here.\n\nUse scons -H for help about command-line options.\n")
test.fail_test(test.stderr() != "")

test.pass_test()
