#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.run(arguments = '-h')

test.fail_test(string.find(test.stdout(), '-h, --help') == -1)

test.write('SConstruct', "")

test.run(arguments = '-h')

test.fail_test(string.find(test.stdout(), '-h, --help') == -1)

test.pass_test()
 
