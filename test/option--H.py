#!/usr/bin/env python

__revision__ = "test/option--H.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-H')

test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

test.pass_test()
 
