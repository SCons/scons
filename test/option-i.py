#!/usr/bin/env python

__revision__ = "test/option-i.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-i',
	 stderr = "Warning:  the -i option is not yet implemented\n")

test.run(arguments = '--ignore-errors',
	 stderr = "Warning:  the --ignore-errors option is not yet implemented\n")

test.pass_test()
 
