#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--no-print-directory',
	 stderr = "Warning:  the --no-print-directory option is not yet implemented\n")

test.pass_test()
 
