#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.pass_test()	#XXX Short-circuit until this is implemented.

test.write('SConstruct', """
""")

test.run(arguments = '.')

test.pass_test()
