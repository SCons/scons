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
Verify the ability to make a SConsignFile() in a non-existent
subdirectory.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

sub_dir = os.path.join('sub', 'dir')
bar_foo_txt = os.path.join('bar', 'foo.txt')

test.write('SConstruct', """
import SCons.dblite
DefaultEnvironment(tools=[])
env = Environment(tools=[])
env.SConsignFile("sub/dir/sconsign", SCons.dblite)
env.Install('bar', 'foo.txt')
""")

test.write('foo.txt', "Foo\n")
expect = test.wrap_stdout(
    read_str='Mkdir("%s")\n' % sub_dir,
    build_str='Install file: "foo.txt" as "%s"\n' % bar_foo_txt,
)

test.run(options='-n', stdout=expect)

test.must_not_exist(['bar', 'foo.txt'])

test.must_not_exist('sub')
test.must_not_exist(['sub', 'dir'])
database_name = test.get_sconsignname()
test.must_not_exist(['sub', 'dir', database_name + '.dblite'])

test.run(stdout=expect)

test.must_match(['bar', 'foo.txt'], "Foo\n")

test.must_exist(['sub', 'dir', 'sconsign.dblite'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
