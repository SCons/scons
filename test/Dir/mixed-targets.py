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
Make sure that target lists of intermixed Node.FS.Dir and Node.FS.File
Nodes work with a DirEntryScanner.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('src', ['src', 'dir'])

test.write('SConstruct', """\
import os
import shutil

import SCons.Defaults

def copier(target, source, env):
    os.rmdir('build')
    shutil.copytree(str(source[0]), 'build')
    return 0

DefaultEnvironment(tools=[])
Copier = Builder(action = copier,
                 target_scanner = SCons.Defaults.DirEntryScanner,
                 target_factory = Entry,
                 source_factory = Entry)

env = Environment(tools=[], BUILDERS = {'Copier': Copier})
env.Copier(['build/dir', 'build/file1'], ['src'])
""")

test.write(['src', 'file1'],            "src/file1\n")

test.write(['src', 'dir', 'file2'],     "src/dir/file2\n")
test.write(['src', 'dir', 'file3'],     "src/dir/file3\n")

test.run(arguments = '.')

test.must_match(['build', 'file1'],         "src/file1\n")

test.must_match(['build', 'dir', 'file2'],  "src/dir/file2\n")
test.must_match(['build', 'dir', 'file3'],  "src/dir/file3\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
