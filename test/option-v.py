#!/usr/bin/env python

__revision__ = "test/option-v.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-v')

expect = r"""SCons version \S+, by Steven Knight et al.
Copyright 2001 Steven Knight
"""

test.fail_test(not test.match_re(test.stdout(), expect))
test.fail_test(test.stderr() != "")

test.run(arguments = '--version')

test.fail_test(not test.match_re(test.stdout(), expect))
test.fail_test(test.stderr() != "")

test.pass_test()
 
