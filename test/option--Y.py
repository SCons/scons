#!/usr/bin/env python

__revision__ = "test/option--Y.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-Y foo')

test.fail_test(test.stderr() !=
		"Warning:  the -Y option is not yet implemented\n")

test.run(chdir = '.', arguments = '--repository=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --repository option is not yet implemented\n")

test.pass_test()
 
