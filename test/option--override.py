#!/usr/bin/env python

__revision__ = "test/option--override.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--override=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --override option is not yet implemented\n")

test.pass_test()
 
