#!/usr/bin/env python

__revision__ = "test/option--W.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-W foo',
	 stderr = "Warning:  the -W option is not yet implemented\n")

test.run(arguments = '--what-if=foo',
	 stderr = "Warning:  the --what-if option is not yet implemented\n")

test.run(arguments = '--new-file=foo',
	 stderr = "Warning:  the --new-file option is not yet implemented\n")

test.run(arguments = '--assume-new=foo',
	 stderr = "Warning:  the --assume-new option is not yet implemented\n")

test.pass_test()
 
