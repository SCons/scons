#!/usr/bin/env python

__revision__ = "test/option-t.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-t',
	 stderr = "Warning:  ignoring -t option\n")

test.run(arguments = '--touch',
	 stderr = "Warning:  ignoring --touch option\n")

test.pass_test()
 
