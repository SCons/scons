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
Test the PathOption canned option type, with tests for its 
various canned validators.
"""

import os.path
import string

import TestSCons

test = TestSCons.TestSCons()

def check(expect):
    result = string.split(test.stdout(), '\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

#### test PathOption ####

test.subdir('lib', 'qt', ['qt', 'lib'], 'nolib' )
workpath = test.workpath()
libpath = os.path.join(workpath, 'lib')

test.write('SConstruct', """
from SCons.Options import PathOption

qtdir = r'%s'

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PathOption('qtdir', 'where the root of Qt is installed', qtdir),
    PathOption('qt_libraries', 'where the Qt library is installed', r'%s'),
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['qtdir']
print env['qt_libraries']
print env.subst('$qt_libraries')

Default(env.Alias('dummy', None))
""" % (workpath, os.path.join('$qtdir', 'lib') ))

qtpath = workpath
libpath = os.path.join(qtpath, 'lib')
test.run()
check([qtpath, os.path.join('$qtdir', 'lib'), libpath])

qtpath = os.path.join(workpath, 'qt')
libpath = os.path.join(qtpath, 'lib')
test.run(arguments='"qtdir=%s"' % qtpath)
check([qtpath, os.path.join('$qtdir', 'lib'), libpath])

qtpath = workpath
libpath = os.path.join(qtpath, 'nolib')
test.run(arguments='"qt_libraries=%s"' % libpath)
check([qtpath, libpath, libpath])

qtpath = os.path.join(workpath, 'qt')
libpath = os.path.join(workpath, 'nolib')
test.run(arguments='"qtdir=%s" "qt_libraries=%s"' % (qtpath, libpath))
check([qtpath, libpath, libpath])

qtpath = os.path.join(workpath, 'non', 'existing', 'path')
test.run(arguments='"qtdir=%s"' % qtpath,
         stderr = """
scons: *** Path for option qtdir does not exist: %s
File "SConstruct", line 12, in ?
""" % qtpath, status=2)

test.run(arguments='"qt_libraries=%s"' % qtpath,
         stderr = """
scons: *** Path for option qt_libraries does not exist: %s
File "SConstruct", line 12, in ?
""" % qtpath, status=2)



default_file = test.workpath('default_file')
default_subdir = test.workpath('default_subdir')

existing_subdir = test.workpath('existing_subdir')
test.subdir(existing_subdir)

existing_file = test.workpath('existing_file')
test.write(existing_file, "existing_file\n")

non_existing_subdir = test.workpath('non_existing_subdir')
non_existing_file = test.workpath('non_existing_file')



test.write('SConstruct', """\
opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PathOption('X', 'X variable', r'%s', validator=PathOption.PathAccept),
    )

env = Environment(options=opts)

print env['X']

Default(env.Alias('dummy', None))
""" % default_subdir)

test.run()
check([default_subdir])

test.run(arguments='"X=%s"' % existing_file)
check([existing_file])

test.run(arguments='"X=%s"' % non_existing_file)
check([non_existing_file])

test.run(arguments='"X=%s"' % existing_subdir)
check([existing_subdir])

test.run(arguments='"X=%s"' % non_existing_subdir)
check([non_existing_subdir])

test.must_not_exist(non_existing_file)
test.must_not_exist(non_existing_subdir)



test.write('SConstruct', """\
opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PathOption('X', 'X variable', r'%s', validator=PathOption.PathIsFile),
    )

env = Environment(options=opts)

print env['X']

Default(env.Alias('dummy', None))
""" % default_file)

test.run(status=2,
         stderr="""
scons: *** File path for option X does not exist: %s
File "SConstruct", line 6, in ?
""" % default_file)

test.write(default_file, "default_file\n")

test.run()
check([default_file])

test.run(arguments='"X=%s"' % existing_subdir,
         status=2,
         stderr="""
scons: *** File path for option X is a directory: %s
File "SConstruct", line 6, in ?
""" % existing_subdir)

test.run(arguments='"X=%s"' % existing_file)
check([existing_file])

test.run(arguments='"X=%s"' % non_existing_file,
         status=2,
         stderr="""
scons: *** File path for option X does not exist: %s
File "SConstruct", line 6, in ?
""" % non_existing_file)



test.write('SConstruct', """\
opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PathOption('X', 'X variable', r'%s', validator=PathOption.PathIsDir),
    )

env = Environment(options=opts)

print env['X']

Default(env.Alias('dummy', None))
""" % default_subdir)

test.run(status=2,
         stderr="""
scons: *** Directory path for option X does not exist: %s
File "SConstruct", line 6, in ?
""" % default_subdir)

test.subdir(default_subdir)

test.run()
check([default_subdir])

test.run(arguments='"X=%s"' % existing_file,
         status=2,
         stderr="""
scons: *** Directory path for option X is a file: %s
File "SConstruct", line 6, in ?
""" % existing_file)

test.run(arguments='"X=%s"' % existing_subdir)
check([existing_subdir])

test.run(arguments='"X=%s"' % non_existing_subdir,
         status=2,
         stderr="""
scons: *** Directory path for option X does not exist: %s
File "SConstruct", line 6, in ?
""" % non_existing_subdir)



test.write('SConstruct', """\
opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PathOption('X', 'X variable', r'%s', validator=PathOption.PathIsDirCreate),
    )

env = Environment(options=opts)

print env['X']

Default(env.Alias('dummy', None))
""" % default_subdir)

test.run()
check([default_subdir])

test.run(arguments='"X=%s"' % existing_file,
         status=2,
         stderr="""
scons: *** Path for option X is a file, not a directory: %s
File "SConstruct", line 6, in ?
""" % existing_file)

test.run(arguments='"X=%s"' % existing_subdir)
check([existing_subdir])

test.run(arguments='"X=%s"' % non_existing_subdir)
check([non_existing_subdir])

test.must_exist(non_existing_subdir)



test.pass_test()
