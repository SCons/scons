#!/usr/bin/env python

__revision__ = "test/option--S.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-S')

test.fail_test(test.stderr() !=
		"Warning:  ignoring -S option\n")

test.run(arguments = '--no-keep-going')

test.fail_test(test.stderr() !=
		"Warning:  ignoring --no-keep-going option\n")

test.run(arguments = '--stop')

test.fail_test(test.stderr() !=
		"Warning:  ignoring --stop option\n")

test.pass_test()
 
