#!/usr/bin/env python

__revision__ = "test/option--R.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-R')

test.fail_test(test.stderr() !=
		"Warning:  the -R option is not yet implemented\n")

test.run(chdir = '.', arguments = '--no-builtin-variables')

test.fail_test(test.stderr() !=
		"Warning:  the --no-builtin-variables option is not yet implemented\n")

test.pass_test()
 
