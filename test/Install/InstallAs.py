#!/usr/bin/env python
#
# MIT Licenxe
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
Test the InstallAs() Environment method.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('install', 'subdir')

install = test.workpath('install')
install_f1_out = os.path.join('install', 'f1.out')
install_file1_out = test.workpath('install', 'file1.out')
install_file2_out = test.workpath('install', 'file2.out')
install_file3_out = test.workpath('install', 'file3.out')

_INSTALLDIR_file2_out = os.path.join('$INSTALLDIR', 'file2.out')
_SUBDIR_file3_in = os.path.join('$SUBDIR', 'file3.in')

#
test.write('SConstruct', r"""
DefaultEnvironment(tools=[])
env = Environment(tools=[], INSTALLDIR=r'%(install)s', SUBDIR='subdir')
InstallAs(r'%(install_file1_out)s', 'file1.in')
env.InstallAs([r'%(_INSTALLDIR_file2_out)s', r'%(install_file3_out)s'],
              ['file2.in', r'%(_SUBDIR_file3_in)s'])
# test passing a keyword arg (not used, but should be accepted)
env.InstallAs('install/f1.out', './file1.in', FOO="bar")
""" % locals())

test.write('file1.in', "file1.in\n")
test.write('file2.in', "file2.in\n")
test.write(['subdir', 'file3.in'], "subdir/file3.in\n")

install_file1_out = os.path.join('install', 'file1.out')
install_file2_out = os.path.join('install', 'file2.out')
install_file3_out = os.path.join('install', 'file3.out')
install_file1a_out = os.path.join('install', 'f1.out')

subdir_file3_in = os.path.join('subdir', 'file3.in')

expect = test.wrap_stdout("""\
Install file: "file1.in" as "%(install_f1_out)s"
Install file: "file1.in" as "%(install_file1_out)s"
Install file: "file2.in" as "%(install_file2_out)s"
Install file: "%(subdir_file3_in)s" as "%(install_file3_out)s"
""" % locals())

test.run(arguments = '.', stdout=expect)

test.must_match(install_file1_out, "file1.in\n", mode='r')
test.must_match(install_file2_out, "file2.in\n", mode='r')
test.must_match(install_file3_out, "subdir/file3.in\n", mode='r')
test.must_match(install_file1a_out, "file1.in\n", mode='r')

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
