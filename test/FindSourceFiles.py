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
Test Environment's FindSourceFiles method.
"""

import sys
import TestSCons

test = TestSCons.TestSCons()

package_format = "src_tarbz2"
if not test.where_is('tar') or sys.platform == 'win32':
    if not test.where_is('zip'):
        test.skip_test("neither 'tar' nor 'zip' found; skipping test\n")
    package_format = "src_zip"

# Quite complex, but real-life test.
# 0. Setup VariantDir, "var", without duplication. The "src" is source dir.
# 1. Generate souce file var/foo.c from src/foo.c.in. Define program foo.
# 2. Gather all sources necessary to create '.' node and create source
#    tarball. We expect 'src/foo.c.in' file within tarball, and no content
#    under 'var' directory.
test.subdir('src')

test.write('SConstruct', """
VariantDir(src_dir = 'src', variant_dir = 'var', duplicate = 0)
env = Environment(tools = ['default','textfile','packaging'])
SConscript(['var/SConscript'], exports = 'env')
sources = env.FindSourceFiles('.')
pkg = env.Package( NAME = 'foo', VERSION = '1.0', PACKAGETYPE = '%s',
                   source = sources )
Ignore( '.', pkg )
""" % package_format)

test.write('src/SConscript', """
Import('env')
foo_c = env.Substfile('foo.c.in', SUBST_DICT = {'__A__' : '0' })
foo = env.Program(foo_c)
""")

test.write('src/foo.c.in', """ int main(void) { return __A__;}
""")

test.run(arguments = 'package')

test.must_exist('foo-1.0/src/SConscript')
test.must_exist('foo-1.0/src/foo.c.in')
test.must_not_exist('foo-1.0/var/SConscript')
test.must_not_exist('foo-1.0/var/foo.c.in')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
