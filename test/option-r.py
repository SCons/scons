#!/usr/bin/env python

__revision__ = "test/option-r.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-r')

test.fail_test(test.stderr() !=
		"Warning:  the -r option is not yet implemented\n")

test.run(chdir = '.', arguments = '--no-builtin-rules')

test.fail_test(test.stderr() !=
		"Warning:  the --no-builtin-rules option is not yet implemented\n")

test.pass_test()
 
