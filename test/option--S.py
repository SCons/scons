#!/usr/bin/env python

__revision__ = "test/option--S.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-S')

test.fail_test(test.stderr() !=
		"Warning:  ignoring -S option\n")

test.run(chdir = '.', arguments = '--no-keep-going')

test.fail_test(test.stderr() !=
		"Warning:  ignoring --no-keep-going option\n")

test.run(chdir = '.', arguments = '--stop')

test.fail_test(test.stderr() !=
		"Warning:  ignoring --stop option\n")

test.pass_test()
 
