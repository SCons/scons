#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '-Z',
	 stderr = '\nSCons error: option -Z not recognized\nFile "\S+", line \d+, in short_has_arg\n')

test.run(arguments = '--ZizzerZazzerZuzz',
	 stderr = '\nSCons error: option --ZizzerZazzerZuzz not recognized\nFile "\S+", line \d+, in long_has_args\n')

test.pass_test()
 
