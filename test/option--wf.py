#!/usr/bin/env python

__revision__ = "test/option--wf.py __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.write('SConstruct', "")

test.run(arguments = '--write-filenames=FILE',
	 stderr = "Warning:  the --write-filenames option is not yet implemented\n")

test.pass_test()
 
