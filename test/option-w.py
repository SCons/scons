#!/usr/bin/env python

__revision__ = "test/option-w.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-w',
	 stderr = "Warning:  the -w option is not yet implemented\n")

test.run(arguments = '--print-directory',
	 stderr = "Warning:  the --print-directory option is not yet implemented\n")

test.pass_test()
 
