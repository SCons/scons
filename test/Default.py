#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir('one', 'two', 'three')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write(contents)
file.close()
""")

test.write(['one', 'SConstruct'], """
B = Builder(name = 'B', action = "python ../build.py %(target)s %(source)s")
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out')
""")

test.write(['two', 'SConstruct'], """
B = Builder(name = 'B', action = "python ../build.py %(target)s %(source)s")
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out', 'bar.out')
""")

test.write(['three', 'SConstruct'], """
B = Builder(name = 'B', action = "python ../build.py %(target)s %(source)s")
env = Environment(BUILDERS = [B])
env.B(target = 'foo.out', source = 'foo.in')
env.B(target = 'bar.out', source = 'bar.in')
Default('foo.out bar.out')
""")

for dir in ['one', 'two', 'three']:

    foo_in = os.path.join(dir, 'foo.in')
    bar_in = os.path.join(dir, 'bar.in')

    test.write(foo_in, foo_in + "\n");

    test.write(bar_in, bar_in + "\n");

    test.run(chdir = dir)	# no arguments, use the Default

test.fail_test(test.read(test.workpath('one', 'foo.out')) != "one/foo.in\n")
test.fail_test(os.path.exists(test.workpath('one', 'bar')))

test.fail_test(test.read(test.workpath('two', 'foo.out')) != "two/foo.in\n")
test.fail_test(test.read(test.workpath('two', 'bar.out')) != "two/bar.in\n")

test.fail_test(test.read(test.workpath('three', 'foo.out')) != "three/foo.in\n")
test.fail_test(test.read(test.workpath('three', 'bar.out')) != "three/bar.in\n")

test.pass_test()
