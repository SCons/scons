#!/usr/bin/env python

__revision__ = "test/option-c.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-c')

test.fail_test(test.stderr() !=
		"Warning:  the -c option is not yet implemented\n")

test.run(arguments = '--clean')

test.fail_test(test.stderr() !=
		"Warning:  the --clean option is not yet implemented\n")

test.run(arguments = '--remove')

test.fail_test(test.stderr() !=
		"Warning:  the --remove option is not yet implemented\n")

test.pass_test()
 
