#!/usr/bin/env python

__revision__ = "test/option-m.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-m')

test.fail_test(test.stderr() !=
		"Warning:  ignoring -m option\n")

test.pass_test()
 
