#!/usr/bin/env python

__revision__ = "test/option--cf.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--cache-force',
	 stderr = "Warning:  the --cache-force option is not yet implemented\n")

test.run(arguments = '--cache-populate',
	 stderr = "Warning:  the --cache-populate option is not yet implemented\n")

test.pass_test()
 
