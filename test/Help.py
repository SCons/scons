#!/usr/bin/env python

__revision__ = "test/SConstruct.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

wpath = test.workpath()

test.write('SConstruct', r"""
Help("Help text\ngoes here.\n")
""")

test.run(chdir = '.', arguments = '-h')

test.fail_test(test.stdout() != "Help text\ngoes here.\n\nUse scons -H for help about command-line options.\n")
test.fail_test(test.stderr() != "")

test.pass_test()
