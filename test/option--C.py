#!/usr/bin/env python

__revision__ = "test/option--C.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-C foo')

test.fail_test(test.stderr() !=
		"Warning:  the -C option is not yet implemented\n")

test.run(chdir = '.', arguments = '--directory=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --directory option is not yet implemented\n")

test.pass_test()
 
