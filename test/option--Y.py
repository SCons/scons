#!/usr/bin/env python

__revision__ = "test/option--Y.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-Y foo',
	 stderr = "Warning:  the -Y option is not yet implemented\n")

test.run(arguments = '--repository=foo',
	 stderr = "Warning:  the --repository option is not yet implemented\n")

test.pass_test()
 
