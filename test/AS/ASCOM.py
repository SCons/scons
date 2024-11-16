#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
#
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

"""
Test the ability to configure the $ASCOM construction variable.
"""

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

if os.path.normcase('.s') == os.path.normcase('.S'):
    alt_s_suffix = '.S'
    alt_asm_suffix = '.ASM'
else:
    alt_s_suffix = '.s'
    alt_asm_suffix = '.asm'

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['as'],
                  ASCOM = r'%(_python_)s mycompile.py as $TARGET $SOURCE',
                  OBJSUFFIX = '.obj',
                  SHOBJPREFIX = '',
                  SHOBJSUFFIX = '.shobj')
env.Object(target = 'test1', source = 'test1.s')
env.Object(target = 'test2', source = 'test2%(alt_s_suffix)s')
env.Object(target = 'test3', source = 'test3.asm')
env.Object(target = 'test4', source = 'test4%(alt_asm_suffix)s')
env.SharedObject(target = 'test5', source = 'test5.s')
env.SharedObject(target = 'test6', source = 'test6%(alt_s_suffix)s')
env.SharedObject(target = 'test7', source = 'test7.asm')
env.SharedObject(target = 'test8', source = 'test8%(alt_asm_suffix)s')
""" % locals())

test.write('test1.s', "test1.s\n/*as*/\n")
test.write('test2'+alt_s_suffix, "test2.S\n/*as*/\n")
test.write('test3.asm', "test3.asm\n/*as*/\n")
test.write('test4'+alt_asm_suffix, "test4.ASM\n/*as*/\n")
test.write('test5.s', "test5.s\n/*as*/\n")
test.write('test6'+alt_s_suffix, "test6.S\n/*as*/\n")
test.write('test7.asm', "test7.asm\n/*as*/\n")
test.write('test8'+alt_asm_suffix, "test8.ASM\n/*as*/\n")

test.run(arguments = '.')

test.must_match('test1.obj', "test1.s\n")
test.must_match('test2.obj', "test2.S\n")
test.must_match('test3.obj', "test3.asm\n")
test.must_match('test4.obj', "test4.ASM\n")
test.must_match('test5.shobj', "test5.s\n")
test.must_match('test6.shobj', "test6.S\n")
test.must_match('test7.shobj', "test7.asm\n")
test.must_match('test8.shobj', "test8.ASM\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
