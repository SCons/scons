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
Test the ability to create more than rpm file with different package root
from one SCons environment.
"""

import os
import SCons.Tool.rpmutils
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

scons = test.program

rpm = test.Environment().WhereIs('rpm')

if not rpm:
    test.skip_test('rpm not found, skipping test\n')

rpm_build_root = test.workpath('rpm_build_root')

test.subdir('src')
mainpath = os.path.join('src', 'main.c')
test.file_fixture(mainpath, mainpath)

test.write('SConstruct', """
import os

env=Environment(tools=['default', 'packaging'])

env.Prepend(RPM = 'TAR_OPTIONS=--wildcards ')
env.Append(RPMFLAGS = r' --buildroot %(rpm_build_root)s')

prog = env.Install( '/bin/' , Program( 'src/main.c')  )

env.Package( NAME           = 'foo',
             VERSION        = '1.2.3',
             PACKAGEVERSION = 0,
             PACKAGETYPE    = 'rpm',
             LICENSE        = 'gpl',
             SUMMARY        = 'balalalalal',
             X_RPM_GROUP    = 'Application/fu',
             X_RPM_INSTALL  = r'%(_python_)s %(scons)s --debug=tree --install-sandbox="$RPM_BUILD_ROOT" "$RPM_BUILD_ROOT"',
             DESCRIPTION    = 'this should be really really long',
             source         = [ prog ],
             SOURCE_URL     = 'http://foo.org/foo-1.2.3.tar.gz'
        )

env.Package( NAME           = 'foo2',
             VERSION        = '1.2.3',
             PACKAGEVERSION = 0,
             PACKAGETYPE    = 'rpm',
             LICENSE        = 'gpl',
             SUMMARY        = 'balalalalal',
             X_RPM_GROUP    = 'Application/fu',
             X_RPM_INSTALL  = r'%(_python_)s %(scons)s --debug=tree --install-sandbox="$RPM_BUILD_ROOT" "$RPM_BUILD_ROOT"',
             DESCRIPTION    = 'this should be really really long',
             source         = [ prog ],
        )



env.Alias( 'install', prog )
""" % locals())

test.run(arguments='', stderr = None)

src_rpm      = 'foo-1.2.3-0.src.rpm'
machine_rpm  = 'foo-1.2.3-0.%s.rpm' % SCons.Tool.rpmutils.defaultMachine()
src_rpm2     = 'foo2-1.2.3-0.src.rpm'
machine_rpm2 = 'foo2-1.2.3-0.%s.rpm' % SCons.Tool.rpmutils.defaultMachine()

test.must_exist( machine_rpm )
test.must_exist( src_rpm )

test.must_exist( machine_rpm2 )
test.must_exist( src_rpm2 )

test.must_not_exist( 'bin/main' )
out = os.popen( 'rpm -qpl %s' % machine_rpm).read()
test.must_contain_all_lines( out, '/bin/main')
out = os.popen( 'rpm -qpl %s' % src_rpm).read()
test.fail_test( not out == 'foo-1.2.3.spec\nfoo-1.2.3.tar.gz\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
