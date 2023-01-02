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
Test the PathVariable canned option type, with tests for its 
various canned validators.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

def check(expect):
    result = test.stdout().split('\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

#### test PathVariable ####

test.subdir('lib', 'qt', ['qt', 'lib'], 'nolib' )
workpath = test.workpath()
libpath = os.path.join(workpath, 'lib')

test.write(SConstruct_path, """\
from SCons.Variables.PathVariable import PathVariable
PV = PathVariable

from SCons.Variables import PathVariable

qtdir = r'%s'

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PathVariable('qtdir', 'where the root of Qt is installed', qtdir),
    PV('qt_libraries', 'where the Qt library is installed', r'%s'),
    )

DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts)
Help(opts.GenerateHelpText(env))

print(env['qtdir'])
print(env['qt_libraries'])
print(env.subst('$qt_libraries'))

Default(env.Alias('dummy', None))
""" % (workpath, os.path.join('$qtdir', 'lib') ))

qtpath = workpath
libpath = os.path.join(qtpath, 'lib')
test.run()
check([qtpath, os.path.join('$qtdir', 'lib'), libpath])

qtpath = os.path.join(workpath, 'qt')
libpath = os.path.join(qtpath, 'lib')
test.run(arguments=['qtdir=%s' % qtpath])
check([qtpath, os.path.join('$qtdir', 'lib'), libpath])

qtpath = workpath
libpath = os.path.join(qtpath, 'nolib')
test.run(arguments=['qt_libraries=%s' % libpath])
check([qtpath, libpath, libpath])

qtpath = os.path.join(workpath, 'qt')
libpath = os.path.join(workpath, 'nolib')
test.run(arguments=['qtdir=%s' % qtpath, 'qt_libraries=%s' % libpath])
check([qtpath, libpath, libpath])

qtpath = os.path.join(workpath, 'non', 'existing', 'path')
SConstruct_file_line = test.python_file_line(test.workpath('SConstruct'), 15)[:-1]

expect_stderr = """
scons: *** Path for option qtdir does not exist: %(qtpath)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['qtdir=%s' % qtpath], stderr=expect_stderr, status=2)

expect_stderr = """
scons: *** Path for option qt_libraries does not exist: %(qtpath)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['qt_libraries=%s' % qtpath], stderr=expect_stderr, status=2)



default_file = test.workpath('default_file')
default_subdir = test.workpath('default_subdir')

existing_subdir = test.workpath('existing_subdir')
test.subdir(existing_subdir)

existing_file = test.workpath('existing_file')
test.write(existing_file, "existing_file\n")

non_existing_subdir = test.workpath('non_existing_subdir')
non_existing_file = test.workpath('non_existing_file')



test.write('SConstruct', """\
opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PathVariable('X', 'X variable', r'%s', validator=PathVariable.PathAccept),
    )

DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts)

print(env['X'])

Default(env.Alias('dummy', None))
""" % default_subdir)

test.run()
check([default_subdir])

test.run(arguments=['X=%s' % existing_file])
check([existing_file])

test.run(arguments=['X=%s' % non_existing_file])
check([non_existing_file])

test.run(arguments=['X=%s' % existing_subdir])
check([existing_subdir])

test.run(arguments=['X=%s' % non_existing_subdir])
check([non_existing_subdir])

test.must_not_exist(non_existing_file)
test.must_not_exist(non_existing_subdir)



test.write(SConstruct_path, """\
opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PathVariable('X', 'X variable', r'%s', validator=PathVariable.PathIsFile),
    )

DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts)

print(env['X'])

Default(env.Alias('dummy', None))
""" % default_file)

SConstruct_file_line = test.python_file_line(test.workpath('SConstruct'), 7)[:-1]

expect_stderr = """
scons: *** File path for option X does not exist: %(default_file)s
%(SConstruct_file_line)s
""" % locals()

test.run(status=2, stderr=expect_stderr)

test.write(default_file, "default_file\n")

test.run()
check([default_file])

expect_stderr = """
scons: *** File path for option X is a directory: %(existing_subdir)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['X=%s' % existing_subdir], status=2, stderr=expect_stderr)

test.run(arguments=['X=%s' % existing_file])
check([existing_file])

expect_stderr = """
scons: *** File path for option X does not exist: %(non_existing_file)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['X=%s' % non_existing_file], status=2, stderr=expect_stderr)



test.write('SConstruct', """\
opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PathVariable('X', 'X variable', r'%s', validator=PathVariable.PathIsDir),
    )

DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts)

print(env['X'])

Default(env.Alias('dummy', None))
""" % default_subdir)

expect_stderr = """
scons: *** Directory path for option X does not exist: %(default_subdir)s
%(SConstruct_file_line)s
""" % locals()

test.run(status=2, stderr=expect_stderr)

test.subdir(default_subdir)

test.run()
check([default_subdir])

expect_stderr = """
scons: *** Directory path for option X is a file: %(existing_file)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['X=%s' % existing_file],
         status=2,
         stderr=expect_stderr)

test.run(arguments=['X=%s' % existing_subdir])
check([existing_subdir])

expect_stderr = """
scons: *** Directory path for option X does not exist: %(non_existing_subdir)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['X=%s' % non_existing_subdir],
         status=2,
         stderr=expect_stderr)



test.write('SConstruct', """\
opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    PathVariable('X', 'X variable', r'%s', validator=PathVariable.PathIsDirCreate),
    )

DefaultEnvironment(tools=[])  # test speedup
env = Environment(variables=opts)

print(env['X'])

Default(env.Alias('dummy', None))
""" % default_subdir)

test.run()
check([default_subdir])

expect_stderr = """
scons: *** Path for option X is a file, not a directory: %(existing_file)s
%(SConstruct_file_line)s
""" % locals()

test.run(arguments=['X=%s' % existing_file], status=2, stderr=expect_stderr)

test.run(arguments=['X=%s' % existing_subdir])
check([existing_subdir])

test.run(arguments=['X=%s' % non_existing_subdir])
check([non_existing_subdir])

test.must_exist(non_existing_subdir)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
