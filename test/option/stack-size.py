#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

isStackSizeAvailable = False
try:
    import threading
    isStackSizeAvailable = hasattr(threading,'stack_size')
except ImportError:
    pass

test.subdir('work1', 'work2')

test.write('build.py', r"""
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as infp:
    f.write(infp.read())
""")


test.write(['work1', 'SConstruct'], """
B = Builder(action = r'%(_python_)s ../build.py $TARGETS $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(tools=[], BUILDERS = { 'B' : B })
f1 = env.B(target = 'f1.out', source = 'f1.in')
f2 = env.B(target = 'f2.out', source = 'f2.in')
Requires(f2, f1)
""" % locals())

test.write(['work1', 'f1.in'], "f1.in\n")
test.write(['work1', 'f2.in'], "f2.in\n")


test.write(['work2', 'SConstruct'], """
SetOption('stack_size', 128)
B = Builder(action = r'%(_python_)s ../build.py $TARGETS $SOURCES')
DefaultEnvironment(tools=[])  # test speedup
env = Environment(BUILDERS = { 'B' : B })
f1 = env.B(target = 'f1.out', source = 'f1.in')
f2 = env.B(target = 'f2.out', source = 'f2.in')
Requires(f2, f1)
""" % locals())

test.write(['work2', 'f1.in'], "f1.in\n")
test.write(['work2', 'f2.in'], "f2.in\n")



expected_stdout = test.wrap_stdout("""\
%(_python_)s ../build.py f1.out f1.in
%(_python_)s ../build.py f2.out f2.in
""" % locals())

re_expected_stdout = expected_stdout.replace('\\', '\\\\')

expect_unsupported = """
scons: warning: Setting stack size is unsupported by this version of Python:
    (('module' object|'threading' module) has no attribute 'stack_size'|stack_size)
File .*
"""


#
# Test without any options
#
test.run(chdir='work1', 
         arguments = '.',
         stdout=expected_stdout,
         stderr='')
test.must_exist(['work1', 'f1.out'])
test.must_exist(['work1', 'f2.out'])

test.run(chdir='work1', 
         arguments = '-c .')
test.must_not_exist(['work1', 'f1.out'])
test.must_not_exist(['work1', 'f2.out'])

#
# Test with -j2
#
test.run(chdir='work1', 
         arguments = '-j2 .',
         stdout=expected_stdout,
         stderr='')
test.must_exist(['work1', 'f1.out'])
test.must_exist(['work1', 'f2.out'])

test.run(chdir='work1', 
         arguments = '-j2 -c .')
test.must_not_exist(['work1', 'f1.out'])
test.must_not_exist(['work1', 'f2.out'])


#
# Test with --stack-size
#
test.run(chdir='work1', 
         arguments = '--stack-size=128 .',
         stdout=expected_stdout,
         stderr='')
test.must_exist(['work1', 'f1.out'])
test.must_exist(['work1', 'f2.out'])

test.run(chdir='work1', 
         arguments = '--stack-size=128 -c .')
test.must_not_exist(['work1', 'f1.out'])
test.must_not_exist(['work1', 'f2.out'])

#
# Test with SetOption('stack_size', 128)
#
test.run(chdir='work2', 
         arguments = '.',
         stdout=expected_stdout,
         stderr='')
test.must_exist(['work2', 'f1.out'])
test.must_exist(['work2', 'f2.out'])

test.run(chdir='work2', 
         arguments = '--stack-size=128 -c .')
test.must_not_exist(['work2', 'f1.out'])
test.must_not_exist(['work2', 'f2.out'])

if isStackSizeAvailable:
    #
    # Test with -j2 --stack-size=128
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 -c .')
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 --stack-size=16
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 .',
             match=TestSCons.match_re,
             stdout=re_expected_stdout,
             stderr="""
scons: warning: Setting stack size failed:
    size not valid: 16384 bytes
File .*
""")
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 -c .',
             match=TestSCons.match_re,
             stderr="""
scons: warning: Setting stack size failed:
    size not valid: 16384 bytes
File .*
""")
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 SetOption('stack_size', 128)
    #
    test.run(chdir='work2', 
             arguments = '-j2 .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work2', 'f1.out'])
    test.must_exist(['work2', 'f2.out'])

    test.run(chdir='work2', 
             arguments = '-j2  -c .')
    test.must_not_exist(['work2', 'f1.out'])
    test.must_not_exist(['work2', 'f2.out'])

    #
    # Test with -j2 --stack-size=128 --warn=no-stack-size
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128  --warn=no-stack-size -c .')
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 --stack-size=16 --warn=no-stack-size
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 --warn=no-stack-size -c .')
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2  --warn=no-stack-size SetOption('stack_size', 128) 
    #
    test.run(chdir='work2', 
             arguments = '-j2  --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work2', 'f1.out'])
    test.must_exist(['work2', 'f2.out'])

    test.run(chdir='work2', 
             arguments = '-j2   --warn=no-stack-size -c .')
    test.must_not_exist(['work2', 'f1.out'])
    test.must_not_exist(['work2', 'f2.out'])

else:

    #
    # Test with -j2 --stack-size=128
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 .',
             match=TestSCons.match_re,
             stdout=re_expected_stdout,
             stderr=expect_unsupported)
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 -c .',
             match=TestSCons.match_re,
             stderr=expect_unsupported)
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 --stack-size=16
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 .',
             match=TestSCons.match_re,
             stdout=re_expected_stdout,
             stderr=expect_unsupported)
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 -c .',
             match=TestSCons.match_re,
             stderr=expect_unsupported)
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 SetOption('stack_size', 128)
    #
    test.run(chdir='work2', 
             arguments = '-j2 .',
             match=TestSCons.match_re,
             stdout=re_expected_stdout,
             stderr=expect_unsupported)
    test.must_exist(['work2', 'f1.out'])
    test.must_exist(['work2', 'f2.out'])

    test.run(chdir='work2', 
             arguments = '-j2  -c .',
             match=TestSCons.match_re,
             stderr=expect_unsupported)
    test.must_not_exist(['work2', 'f1.out'])
    test.must_not_exist(['work2', 'f2.out'])

    #
    # Test with -j2 --stack-size=128 --warn=no-stack-size
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128 --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=128  --warn=no-stack-size -c .')
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2 --stack-size=16 --warn=no-stack-size
    #
    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work1', 'f1.out'])
    test.must_exist(['work1', 'f2.out'])

    test.run(chdir='work1', 
             arguments = '-j2 --stack-size=16 --warn=no-stack-size -c .')
    test.must_not_exist(['work1', 'f1.out'])
    test.must_not_exist(['work1', 'f2.out'])

    #
    # Test with -j2  --warn=no-stack-size SetOption('stack_size', 128) 
    #
    test.run(chdir='work2', 
             arguments = '-j2  --warn=no-stack-size .',
             stdout=expected_stdout,
             stderr='')
    test.must_exist(['work2', 'f1.out'])
    test.must_exist(['work2', 'f2.out'])

    test.run(chdir='work2', 
             arguments = '-j2   --warn=no-stack-size -c .')
    test.must_not_exist(['work2', 'f1.out'])
    test.must_not_exist(['work2', 'f2.out'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
