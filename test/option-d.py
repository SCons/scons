#!/usr/bin/env python

__revision__ = "test/option-d.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-d')

test.fail_test(test.stderr() !=
		"Warning:  the -d option is not yet implemented\n")

test.pass_test()
 
