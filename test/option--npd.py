#!/usr/bin/env python

__revision__ = "test/option--npd.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '--no-print-directory')

test.fail_test(test.stderr() !=
		"Warning:  the --no-print-directory option is not yet implemented\n")

test.pass_test()
 
