#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-l 1',
	 stderr = "Warning:  the -l option is not yet implemented\n")

test.run(arguments = '--load-average=1',
	 stderr = "Warning:  the --load-average option is not yet implemented\n")

test.run(arguments = '--max-load=1',
	 stderr = "Warning:  the --max-load option is not yet implemented\n")

test.pass_test()
 
