#!/usr/bin/env python

__revision__ = "test/option-n.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-n')

test.fail_test(test.stderr() !=
		"Warning:  the -n option is not yet implemented\n")

test.run(chdir = '.', arguments = '--no-exec')

test.fail_test(test.stderr() !=
		"Warning:  the --no-exec option is not yet implemented\n")

test.run(chdir = '.', arguments = '--just-print')

test.fail_test(test.stderr() !=
		"Warning:  the --just-print option is not yet implemented\n")

test.run(chdir = '.', arguments = '--dry-run')

test.fail_test(test.stderr() !=
		"Warning:  the --dry-run option is not yet implemented\n")

test.run(chdir = '.', arguments = '--recon')

test.fail_test(test.stderr() !=
		"Warning:  the --recon option is not yet implemented\n")

test.pass_test()
 
