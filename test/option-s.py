#!/usr/bin/env python

__revision__ = "test/option-s.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-s')

test.fail_test(test.stderr() !=
		"Warning:  the -s option is not yet implemented\n")

test.run(chdir = '.', arguments = '--silent')

test.fail_test(test.stderr() !=
		"Warning:  the --silent option is not yet implemented\n")

test.run(chdir = '.', arguments = '--quiet')

test.fail_test(test.stderr() !=
		"Warning:  the --quiet option is not yet implemented\n")

test.pass_test()
 
