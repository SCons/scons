#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
Test the ability to handle internationalized package and file meta-data.

These are x-rpm-Group, description, summary and the lang_xx file tag.
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

#
# test INTERNATIONAL PACKAGE META-DATA
#
test.file_fixture('src/main.c', 'main.c')

test.write('SConstruct', """
# -*- coding: utf-8 -*-
import os

env  = Environment(tools=['default', 'packaging'])

env.Prepend(RPM = 'TAR_OPTIONS=--wildcards ')
env.Append(RPMFLAGS = r' --buildroot %(rpm_build_root)s')

prog = env.Install( '/bin', Program( 'main.c' ) )

env.Package( NAME           = 'foo',
             VERSION        = '1.2.3',
             PACKAGETYPE    = 'rpm',
             LICENSE        = 'gpl',
             SUMMARY        = 'hello',
             SUMMARY_de     = 'hallo',
             SUMMARY_fr     = 'bonjour',
             PACKAGEVERSION = 0,
             X_RPM_GROUP    = 'Application/office',
             X_RPM_GROUP_de = 'Applikation/büro',
             X_RPM_GROUP_fr = 'Application/bureau',
             X_RPM_INSTALL  = r'%(_python_)s %(scons)s --install-sandbox="$RPM_BUILD_ROOT" "$RPM_BUILD_ROOT"',
             DESCRIPTION    = 'this should be really long',
             DESCRIPTION_de = 'das sollte wirklich lang sein',
             DESCRIPTION_fr = 'ceci devrait être vraiment long',
             source         = [ prog ],
             SOURCE_URL     = 'http://foo.org/foo-1.2.3.tar.gz'
            )

env.Alias ( 'install', prog )
""" % locals())

test.run(arguments='', stderr = None)

src_rpm = 'foo-1.2.3-0.src.rpm'
machine_rpm = 'foo-1.2.3-0.%s.rpm' % SCons.Tool.rpmutils.defaultMachine()

test.must_exist( src_rpm )
test.must_exist( machine_rpm )

test.must_not_exist( 'bin/main' )

cmd = 'rpm -qp --queryformat \'%%{GROUP}-%%{SUMMARY}-%%{DESCRIPTION}\' %s'

os.environ['LANGUAGE'] = 'de'
out = os.popen( cmd % test.workpath(machine_rpm) ).read()
test.fail_test( out != 'Applikation/büro-hallo-das sollte wirklich lang sein' )

os.environ['LANGUAGE'] = 'fr'
out = os.popen( cmd % test.workpath(machine_rpm) ).read()
test.fail_test( out != 'Application/bureau-bonjour-ceci devrait être vraiment long' )

os.environ['LANGUAGE'] = 'en'
out = os.popen( cmd % test.workpath(machine_rpm) ).read()
test.fail_test( out != 'Application/office-hello-this should be really long' )

os.environ['LC_ALL'] = 'ae'
out = os.popen( cmd % test.workpath(machine_rpm) ).read()
test.fail_test( out != 'Application/office-hello-this should be really long' )

#
# test INTERNATIONAL PACKAGE TAGS
#
mainpath = os.path.join('src', 'main.c')
test.file_fixture(mainpath)

test.write( ['man.de'], '' )
test.write( ['man.en'], '' )
test.write( ['man.fr'], '' )

test.write('SConstruct', """
# -*- coding: utf-8 -*-
import os

env  = Environment(tools=['default', 'packaging'])
prog = env.Install( '/bin', Program( 'main.c' ) )

man_pages = Flatten( [
  env.Install( '/usr/share/man/de', 'man.de' ),
  env.Install( '/usr/share/man/en', 'man.en' ),
  env.Install( '/usr/share/man/fr', 'man.fr' )
] )

env.Tag( man_pages, 'LANG_DE', 'DOC')

env.Package( NAME           = 'foo',
             VERSION        = '1.2.3',
             PACKAGETYPE    = 'rpm',
             LICENSE        = 'gpl',
             SUMMARY        = 'hello',
             SUMMARY_de     = 'hallo',
             SUMMARY_fr     = 'bonjour',
             PACKAGEVERSION = 0,
             X_RPM_GROUP    = 'Application/office',
             X_RPM_GROUP_de = 'Applikation/büro',
             X_RPM_GROUP_fr = 'Application/bureau',
             X_RPM_INSTALL  = r'%(_python_)s %(scons)s --install-sandbox="$RPM_BUILD_ROOT" "$RPM_BUILD_ROOT"',
             DESCRIPTION    = 'this should be really long',
             DESCRIPTION_de = 'das sollte wirklich lang sein',
             DESCRIPTION_fr = 'ceci devrait être vraiment long',
             source         = [ prog, man_pages ],
             SOURCE_URL     = 'http://foo.org/foo-1.2.3.tar.gz',
            )

env.Alias ( 'install', [ prog, man_pages ] )
""" % locals())


test.run(arguments='--install-sandbox=blubb install', stderr = None)

test.must_exist( src_rpm )
test.must_exist( machine_rpm )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
