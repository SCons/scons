#!/usr/bin/env python

__revision__ = "test/option-q.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-q')

test.fail_test(test.stderr() !=
		"Warning:  the -q option is not yet implemented\n")

test.run(arguments = '--question')

test.fail_test(test.stderr() !=
		"Warning:  the --question option is not yet implemented\n")

test.pass_test()
 
