#!/usr/bin/env python

__revision__ = "test/option-o.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-o foo',
	 stderr = "Warning:  the -o option is not yet implemented\n")

test.run(arguments = '--old-file=foo',
	 stderr = "Warning:  the --old-file option is not yet implemented\n")

test.run(arguments = '--assume-old=foo',
	 stderr = "Warning:  the --assume-old option is not yet implemented\n")

test.pass_test()
 
