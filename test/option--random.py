#!/usr/bin/env python

__revision__ = "test/option--random.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--random',
	 stderr = "Warning:  the --random option is not yet implemented\n")

test.pass_test()
 
