#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons
import os.path
import string
import sys

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
B = Builder(name = "B", action = "python build.py %(target)s %(source)s")
env = Environment(BUILDERS = [B])
env.B(target = 'f1.out', source = 'f1.in')
env.B(target = 'f2.out', source = 'f2.in')
env.B(target = 'f3.out', source = 'f3.in')
env.B(target = 'f4.out', source = 'f4.in')
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

test.run(arguments = 'f1.out f3.out')

test.run(arguments = 'f1.out f2.out f3.out f4.out', stdout =
"""scons: "f1.out" is up to date.
python build.py f2.out f2.in
scons: "f3.out" is up to date.
python build.py f4.out f4.in
""")

test.pass_test()

