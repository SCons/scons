#!/usr/bin/env python

__revision__ = "test/option-o.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-o foo')

test.fail_test(test.stderr() !=
		"Warning:  the -o option is not yet implemented\n")

test.run(chdir = '.', arguments = '--old-file=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --old-file option is not yet implemented\n")

test.run(chdir = '.', arguments = '--assume-old=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --assume-old option is not yet implemented\n")

test.pass_test()
 
