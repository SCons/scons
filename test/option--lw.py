#!/usr/bin/env python

__revision__ = "test/option--lw.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--list-where')

test.fail_test(test.stderr() !=
		"Warning:  the --list-where option is not yet implemented\n")

test.pass_test()
 
