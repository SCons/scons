#!/usr/bin/env python

__revision__ = "test/option--cs.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--cache-show',
	 stderr = "Warning:  the --cache-show option is not yet implemented\n")

test.pass_test()
 
