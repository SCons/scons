#!/usr/bin/env python

__revision__ = "test/option-e.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-e',
	 stderr = "Warning:  the -e option is not yet implemented\n")

test.run(arguments = '--environment-overrides',
	 stderr = "Warning:  the --environment-overrides option is not yet implemented\n")

test.pass_test()
 
