#!/usr/bin/env python

__revision__ = "test/option-r.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-r',
	 stderr = "Warning:  the -r option is not yet implemented\n")

test.run(arguments = '--no-builtin-rules',
	 stderr = "Warning:  the --no-builtin-rules option is not yet implemented\n")

test.pass_test()
 
