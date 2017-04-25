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
Test the Variables help messages.
"""

import os

import TestSCons

str_True = str(True)
str_False = str(False)

test = TestSCons.TestSCons()

workpath = test.workpath()
qtpath  = os.path.join(workpath, 'qt')
libpath = os.path.join(qtpath, 'lib')
libdirvar = os.path.join('$qtdir', 'lib')

test.subdir(qtpath)
test.subdir(libpath)
         
test.write('SConstruct', """
from SCons.Variables import BoolVariable, EnumVariable, ListVariable, \
   PackageVariable, PathVariable

list_of_libs = Split('x11 gl qt ical')
qtdir = r'%(qtpath)s'

opts = Variables(args=ARGUMENTS)
opts.AddVariables(
    BoolVariable('warnings', 'compilation with -Wall and similiar', 1),
    BoolVariable('profile', 'create profiling informations', 0),
    EnumVariable('debug', 'debug output and symbols', 'no',
               allowed_values=('yes', 'no', 'full'),
               map={}, ignorecase=0),  # case sensitive
    EnumVariable('guilib', 'gui lib to use', 'gtk',
               allowed_values=('motif', 'gtk', 'kde'),
               map={}, ignorecase=1), # case insensitive
    EnumVariable('some', 'some option', 'xaver',
               allowed_values=('xaver', 'eins'),
               map={}, ignorecase=2), # make lowercase
    ListVariable('shared',
               'libraries to build as shared libraries',
               'all',
               names = list_of_libs),
    PackageVariable('x11',
                  'use X11 installed here (yes = search some places)',
                  'yes'),
    PathVariable('qtdir', 'where the root of Qt is installed', qtdir),
    PathVariable('qt_libraries',
               'where the Qt library is installed',
               r'%(libdirvar)s'),
    )

env = Environment(variables=opts)
Help(opts.GenerateHelpText(env))

print(env['warnings'])
print(env['profile'])

Default(env.Alias('dummy', None))
""" % locals())


test.run(arguments='-h',
         stdout = """\
scons: Reading SConscript files ...
%(str_True)s
%(str_False)s
scons: done reading SConscript files.

warnings: compilation with -Wall and similiar (yes|no)
    default: 1
    actual: %(str_True)s

profile: create profiling informations (yes|no)
    default: 0
    actual: %(str_False)s

debug: debug output and symbols (yes|no|full)
    default: no
    actual: no

guilib: gui lib to use (motif|gtk|kde)
    default: gtk
    actual: gtk

some: some option (xaver|eins)
    default: xaver
    actual: xaver

shared: libraries to build as shared libraries
    (all|none|comma-separated list of names)
    allowed names: x11 gl qt ical
    default: all
    actual: x11 gl qt ical

x11: use X11 installed here (yes = search some places)
    ( yes | no | /path/to/x11 )
    default: yes
    actual: %(str_True)s

qtdir: where the root of Qt is installed ( /path/to/qtdir )
    default: %(qtpath)s
    actual: %(qtpath)s

qt_libraries: where the Qt library is installed ( /path/to/qt_libraries )
    default: %(libdirvar)s
    actual: %(libpath)s

Use scons -H for help about command-line options.
""" % locals())



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
