#!/usr/bin/env python

__revision__ = "test/option-h.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

test.run(chdir = '.', arguments = '-h')

test.fail_test(string.find(test.stdout(), '-h, --help') == -1)

test.write('SConstruct', "")

test.run(chdir = '.', arguments = '-h')

test.fail_test(string.find(test.stdout(), '-h, --help') == -1)

test.pass_test()
 
