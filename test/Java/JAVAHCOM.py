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
Test the ability to configure the $JAVAHCOM construction variable.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.file_fixture('mycompile.py')

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(
    TOOLS=['default', 'javah'],
    JAVAHCOM=r'%(_python_)s mycompile.py javah $TARGET $SOURCES',
)
env.JavaH(target='out', source='file1.class')
env.JavaH(target='out', source='file2.class')
env.JavaH(target='out', source='file3.class')
""" % locals())

test.write('file1.class', "file1.class\n/*javah*/\n")
test.write('file2.class', "file2.class\n/*javah*/\n")
test.write('file3.class', "file3.class\n/*javah*/\n")

test.run()

test.must_match(['out', 'file1.h'], "file1.class\n")
test.must_match(['out', 'file2.h'], "file2.class\n")
test.must_match(['out', 'file3.h'], "file3.class\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
