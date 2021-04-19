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
Test the --install-sandbox commandline option for Install() and InstallAs().
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('install', 'subdir')
target  = 'destination'
destdir = test.workpath( target )
_SUBDIR_file3_out = os.path.join('$SUBDIR', 'file3.out')
_SUBDIR_file3_in = os.path.join('$SUBDIR', 'file3.in')

target_file2_out = os.path.join(target, 'file2.out')
subdir_file3_in = os.path.join('subdir', 'file3.in')
target_subdir_file3_out = os.path.join(target, 'subdir', 'file3.out')
file1_out = target + os.path.join(target, os.path.splitdrive(destdir)[1], 'file1.out')

test.write('SConstruct', r"""
DefaultEnvironment(tools=[])
env = Environment(tools=[], SUBDIR='subdir')
f1 = env.Install(r'%(destdir)s', 'file1.out')
f2 = env.InstallAs(['file2.out', r'%(_SUBDIR_file3_out)s'],
                   ['file2.in', r'%(_SUBDIR_file3_in)s'])
env.Depends(f2, f1)
""" % locals())

test.write('file1.out', "file1.out\n")
test.write('file2.in', "file2.in\n")
test.write(['subdir', 'file3.in'], "subdir/file3.in\n")

expect = test.wrap_stdout("""\
Install file: "file1.out" as "%(file1_out)s"
Install file: "file2.in" as "%(target_file2_out)s"
Install file: "%(subdir_file3_in)s" as "%(target_subdir_file3_out)s"
""" % locals())

test.run(arguments = '--install-sandbox=%s' % destdir, stdout=expect)

test.must_match(file1_out, "file1.out\n")
test.must_match('destination/file2.out', "file2.in\n")
test.must_match('destination/subdir/file3.out', "subdir/file3.in\n")

#
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
