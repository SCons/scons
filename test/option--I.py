#!/usr/bin/env python

__revision__ = "test/option--I.py __REVISION__ __DATE__ __DEVELOPER__"

import TestCmd
import string
import sys

test = TestCmd.TestCmd(program = 'scons.py',
                       workdir = '',
                       interpreter = 'python')

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

test.run(chdir = '.', arguments = '-I sub1 -I sub2')

test.fail_test(test.stdout() != "sub1/foo\nsub2/bar\n")
test.fail_test(test.stderr() != "")

test.run(chdir = '.', arguments = '--include-dir=sub2 --include-dir=sub1')

test.fail_test(test.stdout() != "sub2/foo\nsub2/bar\n")
test.fail_test(test.stderr() != "")

test.pass_test()
 
