#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-S', stderr = "Warning:  ignoring -S option\n")

test.run(arguments = '--no-keep-going',
	 stderr = "Warning:  ignoring --no-keep-going option\n")

test.run(arguments = '--stop', stderr = "Warning:  ignoring --stop option\n")

test.pass_test()
 
