#!/usr/bin/env python

__revision__ = "test/option-k.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-k',
	 stderr = "Warning:  the -k option is not yet implemented\n")

test.run(arguments = '--keep-going',
	 stderr = "Warning:  the --keep-going option is not yet implemented\n")

test.pass_test()
 
