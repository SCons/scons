#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text\ngoes here.\n")
""")

expect = "Help text\ngoes here.\n\nUse scons -H for help about command-line options.\n"

test.run(arguments = '-h', stdout = expect)

test.pass_test()
