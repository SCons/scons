#!/usr/bin/env python

__revision__ = "test/option-c.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-c')

test.fail_test(test.stderr() !=
		"Warning:  the -c option is not yet implemented\n")

test.run(chdir = '.', arguments = '--clean')

test.fail_test(test.stderr() !=
		"Warning:  the --clean option is not yet implemented\n")

test.run(chdir = '.', arguments = '--remove')

test.fail_test(test.stderr() !=
		"Warning:  the --remove option is not yet implemented\n")

test.pass_test()
 
