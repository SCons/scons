#!/usr/bin/env python

__revision__ = "test/option-b.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-b',
	 stderr = "Warning:  ignoring -b option\n")

test.pass_test()
 
