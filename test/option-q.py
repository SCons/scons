#!/usr/bin/env python

__revision__ = "test/option-q.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-q')

test.fail_test(test.stderr() !=
		"Warning:  the -q option is not yet implemented\n")

test.run(chdir = '.', arguments = '--question')

test.fail_test(test.stderr() !=
		"Warning:  the --question option is not yet implemented\n")

test.pass_test()
 
