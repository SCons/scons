#!/usr/bin/env python

__revision__ = "test/option-t.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-t')

test.fail_test(test.stderr() !=
		"Warning:  ignoring -t option\n")

test.run(chdir = '.', arguments = '--touch')

test.fail_test(test.stderr() !=
		"Warning:  ignoring --touch option\n")

test.pass_test()
 
