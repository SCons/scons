#!/usr/bin/env python

__revision__ = "test/option-v.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

expect = r"""SCons version \S+, by Steven Knight et al.
Copyright 2001 Steven Knight
"""

test.run(arguments = '-v', stdout = expect)

test.run(arguments = '--version', stdout = expect)

test.pass_test()
 
