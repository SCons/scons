#!/usr/bin/env python

__revision__ = "test/option--cf.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '--cache-force')

test.fail_test(test.stderr() !=
		"Warning:  the --cache-force option is not yet implemented\n")

test.run(chdir = '.', arguments = '--cache-populate')

test.fail_test(test.stderr() !=
		"Warning:  the --cache-populate option is not yet implemented\n")

test.pass_test()
 
