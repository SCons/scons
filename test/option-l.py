#!/usr/bin/env python

__revision__ = "test/option-l.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-l 1')

test.fail_test(test.stderr() !=
		"Warning:  the -l option is not yet implemented\n")

test.run(chdir = '.', arguments = '--load-average=1')

test.fail_test(test.stderr() !=
		"Warning:  the --load-average option is not yet implemented\n")

test.run(chdir = '.', arguments = '--max-load=1')

test.fail_test(test.stderr() !=
		"Warning:  the --max-load option is not yet implemented\n")

test.pass_test()
 
