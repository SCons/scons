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
Test the ability to create a rpm package from a explicit target name.
"""

import os
import TestSCons
import sys

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

test.write('SConstruct', """\
import os

env=Environment(tools=['default', 'packaging'])

env.Prepend(RPM = 'TAR_OPTIONS=--wildcards ')
env.Append(RPMFLAGS = r' --buildroot %(rpm_build_root)s')

prog = env.Install( '/bin/' , Program( 'src/main.c')  )

env.Alias( 'install', prog )

env.Package( NAME           = 'foo',
             VERSION        = '1.2.3',
             PACKAGEVERSION = 0,
             PACKAGETYPE    = 'rpm',
             LICENSE        = 'gpl',
             SUMMARY        = 'balalalalal',
             X_RPM_GROUP    = 'Application/fu',
             X_RPM_INSTALL  = r'%(_python_)s %(scons)s --tree=all --install-sandbox="$RPM_BUILD_ROOT" "$RPM_BUILD_ROOT"',
             DESCRIPTION    = 'this should be really really long',
             source         = [ prog ],
             target         = "my_rpm_package.rpm",
             SOURCE_URL     = 'https://foo.org/foo-1.2.3.tar.gz'
        )
""" % locals())


if sys.version_info.minor >= 8:
    line_number = 12
else:
    line_number = 23

expect = """
scons: *** Setting target is not supported for rpm.
""" + test.python_file_line(test.workpath('SConstruct'), line_number)

test.run(arguments='', status=2, stderr=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
