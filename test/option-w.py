#!/usr/bin/env python

__revision__ = "test/option-w.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-w')

test.fail_test(test.stderr() !=
		"Warning:  the -w option is not yet implemented\n")

test.run(chdir = '.', arguments = '--print-directory')

test.fail_test(test.stderr() !=
		"Warning:  the --print-directory option is not yet implemented\n")

test.pass_test()
 
