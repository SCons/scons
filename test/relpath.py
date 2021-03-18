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
Verify ${TARGET.relpath}, ${SOURCE.relpath} match expected path
"""

import TestSCons, os

test = TestSCons.TestSCons()

test.subdir('src', ['src', 'dir'])

test.write('Sconstruct', """\
import os
import shutil

import SCons.Defaults

DefaultEnvironment(tools=[])
Echo = Builder(action = '@echo ${TARGETS.relpath}; echo ${TARGETS.abspath}; echo ${SOURCES.relpath}; echo ${SOURCES.abspath}',
                 target_scanner = SCons.Defaults.DirEntryScanner,
                 target_factory = Entry,
                 source_factory = Entry)

env = Environment(tools=[], BUILDERS = {'Echo': Echo})
env.Echo(['../foo/dir', 'build/file1'], ['src'])
""")

test.run('-Q', status=0, stdout="""\
../foo/dir build/file1
%s %s
src
%s
""" % (os.path.abspath('../foo/dir'), os.path.abspath('build/file1'), os.path.abspath('src')))
