#!/usr/bin/env python

__revision__ = "test/option-v.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-v')

expect = r"""SCons version \S+, by Steven Knight et al.
Copyright 2001 Steven Knight
"""

test.fail_test(not test.match_re(test.stdout(), expect))
test.fail_test(test.stderr() != "")

test.run(chdir = '.', arguments = '--version')

test.fail_test(not test.match_re(test.stdout(), expect))
test.fail_test(test.stderr() != "")

test.pass_test()
 
