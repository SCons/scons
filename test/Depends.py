#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.subdir('subdir')

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'r').read() + open(sys.argv[3], 'r').read()
file = open(sys.argv[1], 'w')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
Foo = Builder(name = "Foo",
	  action = "python build.py %(target)s %(source)s subdir/foo.dep")
Bar = Builder(name = "Bar",
	  action = "python build.py %(target)s %(source)s subdir/bar.dep")
env = Environment(BUILDERS = [Foo, Bar])
env.Depends(target = ['f1.out', 'f2.out'], dependency = 'subdir/foo.dep')
env.Depends(target = 'f3.out', dependency = 'subdir/bar.dep')
env.Foo(target = 'f1.out', source = 'f1.in')
env.Foo(target = 'f2.out', source = 'f2.in')
env.Bar(target = 'f3.out', source = 'f3.in')
Conscript('subdir/SConscript')
""")

test.write(['subdir', 'SConscript'], """
env.Depends(target = 'f4.out', dependency = 'bar.dep')
env.Foo(target = 'f4.out', source = 'f4.in')
""")

test.write('f1.in', "f1.in\n")

test.write('f2.in', "f2.in\n")

test.write('f3.in', "f3.in\n")

test.write(['subdir', 'f4.in'], "subdir/f4.in\n")

test.write(['subdir', 'foo.dep'], "subdir/foo.dep 1\n")

test.write(['subdir', 'bar.dep'], "subdir/bar.dep 1\n")

#XXXtest.run(arguments = '.')
test.run(arguments = 'f1.out f2.out f3.out subdir/f4.out')

test.fail_test(test.read('f1.out') != "f1.in\nsubdir/foo.dep 1\n")
test.fail_test(test.read('f2.out') != "f2.in\nsubdir/foo.dep 1\n")
test.fail_test(test.read('f3.out') != "f3.in\nsubdir/bar.dep 1\n")
#XXXtest.fail_test(test.read(['subdir', 'f4.out']) !=
#XXX					"subdir/f4.in\nsubdir/bar.dep 1\n")

test.write(['subdir', 'foo.dep'], "subdir/foo.dep 2\n")

test.write(['subdir', 'bar.dep'], "subdir/bar.dep 2\n")

#XXXtest.run(arguments = '.')
test.run(arguments = 'f1.out f2.out f3.out subdir/f4.out')

test.fail_test(test.read('f1.out') != "f1.in\nsubdir/foo.dep 2\n")
test.fail_test(test.read('f2.out') != "f2.in\nsubdir/foo.dep 2\n")
test.fail_test(test.read('f3.out') != "f3.in\nsubdir/bar.dep 2\n")
#XXXtest.fail_test(test.read(['subdir', 'f4.out']) !=
#XXX					"subdir/f4.in\nsubdir/bar.dep 2\n")

test.write(['subdir', 'bar.dep'], "subdir/bar.dep 3\n")

#XXXtest.run(arguments = '.')
test.run(arguments = 'f1.out f2.out f3.out subdir/f4.out')

test.fail_test(test.read('f1.out') != "f1.in\nsubdir/foo.dep 2\n")
test.fail_test(test.read('f2.out') != "f2.in\nsubdir/foo.dep 2\n")
test.fail_test(test.read('f3.out') != "f3.in\nsubdir/bar.dep 3\n")
#XXXtest.fail_test(test.read(['subdir', 'f4.out']) !=
#XXX					"subdir/f4.in\nsubdir/bar.dep 3\n")

test.pass_test()
