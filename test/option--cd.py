#!/usr/bin/env python

__revision__ = "test/option--cd.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--cache-disable')

test.fail_test(test.stderr() !=
		"Warning:  the --cache-disable option is not yet implemented\n")

test.run(arguments = '--no-cache')

test.fail_test(test.stderr() !=
		"Warning:  the --no-cache option is not yet implemented\n")

test.pass_test()
 
