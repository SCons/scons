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
Test the ability to use the archiver in combination with builddir.
"""

import os
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

tar = test.detect('TAR', 'tar')

if not tar:
    test.skip_test('tar not found, skipping test\n')

#
# TEST: builddir usage.
#
test.subdir('src')
test.subdir('build')

test.write('src/main.c', '')

test.write('SConstruct', """
VariantDir('build', 'src')
env=Environment(tools=['packaging', 'filesystem', 'zip'])
env.Package( NAME        = 'libfoo',
             PACKAGEROOT = 'build/libfoo',
             VERSION     = '1.2.3',
             PACKAGETYPE = 'src_zip',
             target      = 'build/libfoo-1.2.3.zip',
             source      = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(stderr = None)

test.must_exist( 'build/libfoo-1.2.3.zip' )

# TEST: builddir not placed in archive
# XXX: VariantDir should be stripped.
#
test.subdir('src')
test.subdir('build')
test.subdir('temp')

test.write('src/main.c', '')

test.write('SConstruct', """
VariantDir('build', 'src')
env=Environment(tools=['packaging', 'filesystem', 'tar'])
env.Package( NAME        = 'libfoo',
             VERSION     = '1.2.3',
             PAKCAGETYPE = 'src_targz',
             source      = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(stderr = None)

test.must_exist( 'libfoo-1.2.3.tar.gz' )

os.system('tar -C temp -xzf %s'%test.workpath('libfoo-1.2.3.tar.gz') )

test.must_exist( 'temp/libfoo-1.2.3/src/main.c' )
test.must_exist( 'temp/libfoo-1.2.3/SConstruct' )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
