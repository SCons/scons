#!/usr/bin/env python

__revision__ = "test/option-k.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-k')

test.fail_test(test.stderr() !=
		"Warning:  the -k option is not yet implemented\n")

test.run(chdir = '.', arguments = '--keep-going')

test.fail_test(test.stderr() !=
		"Warning:  the --keep-going option is not yet implemented\n")

test.pass_test()
 
