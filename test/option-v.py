#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import TestSCons
import string
import sys

test = TestSCons.TestSCons(match = TestCmd.match_re)

test.write('SConstruct', "")

expect = r"""SCons version \S+, by Steven Knight et al.
Copyright 2001 Steven Knight
"""

test.run(arguments = '-v', stdout = expect)

test.run(arguments = '--version', stdout = expect)

test.pass_test()
 
