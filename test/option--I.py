#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import string
import sys

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

test.write(['sub1', 'foo.py'], """
variable = "sub1/foo"
""")

test.write(['sub2', 'foo.py'], """
variable = "sub2/foo"
""")

test.write(['sub2', 'bar.py'], """
variable = "sub2/bar"
""")

test.write('SConstruct', """
import foo
print foo.variable
import bar
print bar.variable
""")

test.run(arguments = '-I sub1 -I sub2', stdout = "sub1/foo\nsub2/bar\n")

test.run(arguments = '--include-dir=sub2 --include-dir=sub1',
	 stdout = "sub2/foo\nsub2/bar\n")

test.pass_test()
 
