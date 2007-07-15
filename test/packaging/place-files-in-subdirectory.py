#!/usr/bin/env python
#
# __COPYRIGHT__
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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test the requirement to place files in a given subdirectory before archiving.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

tar = test.detect('TAR', 'tar')

if not tar:
    test.skipt_test('tar not found, skipping test\n')

#
# TEST: subdir creation and file copying
#
test.subdir('src')

test.write('src/main.c', '')

test.write('SConstruct', """
env = Environment(tools=['default', 'packaging'])
env.Package( NAME        = 'libfoo',
             PACKAGEROOT = 'libfoo',
             PACKAGETYPE = 'src_zip',
             VERSION     = '1.2.3',
             source      = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(arguments='libfoo-1.2.3.zip', stderr = None)

test.must_exist( 'libfoo' )
test.must_exist( 'libfoo/SConstruct' )
test.must_exist( 'libfoo/src/main.c' )

#
# TEST: subdir guessing and file copying.
#
test.subdir('src')

test.write('src/main.c', '')

test.write('SConstruct', """
env = Environment(tools=['default', 'packaging'])
env.Package( NAME        = 'libfoo',
             VERSION     = '1.2.3',
             PACKAGETYPE = 'src_zip',
             TARGET      = 'src.zip',
             source      = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(stderr = None)

test.must_exist( 'libfoo-1.2.3' )
test.must_exist( 'libfoo-1.2.3/SConstruct' )
test.must_exist( 'libfoo-1.2.3/src/main.c' )

#
# TEST: unpacking without the buildir.
#
test.subdir('src')
test.subdir('temp')

test.write('src/main.c', '')

test.write('SConstruct', """
env = Environment(tools=['default', 'packaging'])
env.Package( NAME        = 'libfoo',
             VERSION     = '1.2.3',
             PACKAGETYPE = 'src_targz',
             source      = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(stderr = None)

str = os.popen( 'tar -tzf %s'%test.workpath('libfoo-1.2.3.tar.gz') ).read()
test.fail_test( str != "libfoo-1.2.3/src/main.c\nlibfoo-1.2.3/SConstruct\n" )

test.pass_test()
