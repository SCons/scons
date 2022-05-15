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
Test the ability to configure the $RMICCOM construction variable.
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('src')

out_file1 = os.path.join('out', 'file1', 'class_Stub.class')
out_file2 = os.path.join('out', 'file2', 'class_Stub.class')
out_file3 = os.path.join('out', 'file3', 'class_Stub.class')

test.file_fixture('mycompile.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(
    TOOLS=['default', 'rmic'],
    RMICCOM=r'%(_python_)s mycompile.py rmic $TARGET $SOURCES',
)
env.RMIC(target='out', source='file1.class')
env.RMIC(target='out', source='file2.class')
env.RMIC(target='out', source='file3.class')
""" % locals())

test.write('file1.class', "file1.class\n/*rmic*/\n")
test.write('file2.class', "file2.class\n/*rmic*/\n")
test.write('file3.class', "file3.class\n/*rmic*/\n")

test.run()

test.must_match(out_file1, "file1.class\n")
test.must_match(out_file2, "file2.class\n")
test.must_match(out_file3, "file3.class\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
