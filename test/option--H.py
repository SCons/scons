#!/usr/bin/env python

__revision__ = "test/option--H.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-H')

test.fail_test(string.find(test.stdout(), '-H, --help-options') == -1)

test.pass_test()
 
