#!/usr/bin/env python

__revision__ = "test/option-i.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-i')

test.fail_test(test.stderr() !=
		"Warning:  the -i option is not yet implemented\n")

test.run(chdir = '.', arguments = '--ignore-errors')

test.fail_test(test.stderr() !=
		"Warning:  the --ignore-errors option is not yet implemented\n")

test.pass_test()
 
