#!/usr/bin/env python

__revision__ = "test/option--ld.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '--list-derived')

test.fail_test(test.stderr() !=
		"Warning:  the --list-derived option is not yet implemented\n")

test.pass_test()
 
