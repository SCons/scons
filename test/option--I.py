#!/usr/bin/env python

__revision__ = "test/option--I.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-I foo')

test.fail_test(test.stderr() !=
		"Warning:  the -I option is not yet implemented\n")

test.run(chdir = '.', arguments = '--include-dir=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --include-dir option is not yet implemented\n")

test.pass_test()
 
