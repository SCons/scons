#!/usr/bin/env python

__revision__ = "test/option-d.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-d')

test.fail_test(test.stderr() !=
		"Warning:  the -d option is not yet implemented\n")

test.pass_test()
 
