#!/usr/bin/env python

__revision__ = "test/option--Y.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-Y foo')

test.fail_test(test.stderr() !=
		"Warning:  the -Y option is not yet implemented\n")

test.run(arguments = '--repository=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --repository option is not yet implemented\n")

test.pass_test()
 
