
#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write(contents)
file.close()
""")

test.write('SConstruct', """
env = Environment()
env.Command(target = 'f1.out', source = 'f1.in',
		action = "python build.py %(target)s %(source)s")
env.Command(target = 'f2.out', source = 'f2.in',
		action = "python build.py temp2 %(source)s\\npython build.py %(target)s temp2")
env.Command(target = 'f3.out', source = 'f3.in',
		action = ["python build.py temp3 %(source)s",
			  "python build.py %(target)s temp3"])
# Eventually, add ability to do execute Python code.
""")

test.write('f1.in', "f1.in\n")

test.write('f2.in', "f2.in\n")

test.write('f3.in', "f3.in\n")

#XXXtest.run(arguments = '.')
test.run(arguments = 'f1.out f2.out f3.out')

test.fail_test(test.read('f1.out') != "f1.in\n")
test.fail_test(test.read('f2.out') != "f2.in\n")
test.fail_test(test.read('f3.out') != "f3.in\n")

test.pass_test()
