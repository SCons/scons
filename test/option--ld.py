#!/usr/bin/env python

__revision__ = "test/option--ld.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--list-derived')

test.fail_test(test.stderr() !=
		"Warning:  the --list-derived option is not yet implemented\n")

test.pass_test()
 
