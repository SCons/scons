#!/usr/bin/env python

__revision__ = "test/option-e.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-e')

test.fail_test(test.stderr() !=
		"Warning:  the -e option is not yet implemented\n")

test.run(chdir = '.', arguments = '--environment-overrides')

test.fail_test(test.stderr() !=
		"Warning:  the --environment-overrides option is not yet implemented\n")

test.pass_test()
 
