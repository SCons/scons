#!/usr/bin/env python

__revision__ = "test/option--R.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-R',
	 stderr = "Warning:  the -R option is not yet implemented\n")

test.run(arguments = '--no-builtin-variables',
	 stderr = "Warning:  the --no-builtin-variables option is not yet implemented\n")

test.pass_test()
 
