#!/usr/bin/env python

__revision__ = "test/option--W.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-W foo')

test.fail_test(test.stderr() !=
		"Warning:  the -W option is not yet implemented\n")

test.run(chdir = '.', arguments = '--what-if=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --what-if option is not yet implemented\n")

test.run(chdir = '.', arguments = '--new-file=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --new-file option is not yet implemented\n")

test.run(chdir = '.', arguments = '--assume-new=foo')

test.fail_test(test.stderr() !=
		"Warning:  the --assume-new option is not yet implemented\n")

test.pass_test()
 
