#!/usr/bin/env python

__revision__ = "test/option-v.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-v')

test.fail_test(test.stderr() !=
		"Warning:  the -v option is not yet implemented\n")

test.run(chdir = '.', arguments = '--version')

test.fail_test(test.stderr() !=
		"Warning:  the --version option is not yet implemented\n")

test.pass_test()
 
