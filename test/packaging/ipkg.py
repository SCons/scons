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
Test the ability to call the ipkg tool trough SCons.

TODO: make a test to assert that the clean action removes ALL intermediate files
"""

import os
import TestSCons

python = TestSCons.python
test = TestSCons.TestSCons()
ipkg = test.Environment().WhereIs('ipkg-build')

if not ipkg:
  test.skip_test("ipkg-build not found, skipping test\n")

test.write( 'main.c', r"""
int main(int argc, char *argv[])
{
    return 0;
}
""")

test.write( 'foo.conf', '' )

test.write( 'SConstruct', r"""
env=Environment(tools=['default', 'packaging'])
prog = env.Install( 'bin/', Program( 'main.c') )
conf = env.Install( 'etc/', File( 'foo.conf' ) )
env.Tag( conf, 'CONF', 'MEHR', 'UND MEHR' )
env.Package( PACKAGETYPE = 'ipk',
             source      = env.FindInstalledFiles(),
             NAME        = 'foo',
             VERSION     = '0.0',
             SUMMARY     = 'foo is the ever-present example program -- it does everything',
             DESCRIPTION = '''foo is not a real package. This is simply an example that you
may modify if you wish.
.
When you modify this example, be sure to change the Package, Version,
Maintainer, Depends, and Description fields.''',

             SOURCE_URL       = 'http://gnu.org/foo-0.0.tar.gz',
             X_IPK_SECTION    = 'extras',
             X_IPK_PRIORITY   = 'optional',
             ARCHITECTURE     = 'arm',
             X_IPK_MAINTAINER = 'Familiar User <user@somehost.net>',
             X_IPK_DEPENDS    = 'libc6, grep', )
""")

with os.popen('id -un') as p:
    IPKGUSER = p.read().strip()
with os.popen('id -gn') as p:
    IPKGGROUP = p.read().strip()

expected="""scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
gcc -o main.o -c main.c
gcc -o main main.o
Copy file(s): "main" to "foo-0.0/bin/main"
Copy file(s): "foo.conf" to "foo-0.0/etc/foo.conf"
build_specfiles(["foo-0.0/CONTROL/control", "foo-0.0/CONTROL/conffiles", "foo-0.0/CONTROL/postrm", "foo-0.0/CONTROL/prerm", "foo-0.0/CONTROL/postinst", "foo-0.0/CONTROL/preinst"], ["foo-0.0/bin/main", "foo-0.0/etc/foo.conf"])
ipkg-build -o %s -g %s foo-0.0
Packaged contents of foo-0.0 into %s/foo_0.0_arm.ipk
scons: done building targets.
"""%(IPKGUSER, IPKGGROUP, test.workpath())

test.run(arguments="--debug=stacktrace foo_0.0_arm.ipk", stdout=expected)
test.must_exist( 'foo-0.0/CONTROL/control' )
test.must_exist( 'foo_0.0_arm.ipk' )

test.subdir( 'foo-0.0' )
test.subdir( [ 'foo-0.0', 'CONTROL' ] )

test.write( [ 'foo-0.0', 'CONTROL', 'control' ], r"""
Package: foo
Priority: optional
Section: extras
Source: http://gnu.org/foo-0.0.tar.gz
Version: 0.0
Architecture: arm
Maintainer: Familiar User <user@somehost.net>
Depends: libc6, grep
Description: foo is the ever-present example program -- it does everything
 foo is not a real package. This is simply an example that you
 may modify if you wish.
 .
 When you modify this example, be sure to change the Package, Version,
 Maintainer, Depends, and Description fields.
""")

test.write( 'main.c', r"""
int main(int argc, char *argv[])
{
    return 0;
}
""")

test.write('SConstruct', """
env = Environment( tools = [ 'default', 'ipkg' ] )
prog = env.Install( 'foo-0.0/bin/' , env.Program( 'main.c')  )
env.Ipkg( [ env.Dir( 'foo-0.0' ), prog ] )
""")

test.run(arguments='', stderr = None)
test.must_exist( 'foo_0.0_arm.ipk' )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
