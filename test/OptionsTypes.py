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

import TestSCons, SCons.Errors
import string, os

test = TestSCons.TestSCons()

def check(expect):
    result = string.split(test.stdout(), '\n')
    assert result[1:len(expect)+1] == expect, (result[1:len(expect)+1], expect)

#### test BoolOption #####

test.write('SConstruct', """
from SCons.Options import BoolOption

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    BoolOption('warnings', 'compilation with -Wall and similiar', 1),
    BoolOption('profile', 'create profiling informations', 0),
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['warnings']
print env['profile']

Default(env.Alias('dummy', None))
""")

test.run()
check(['1', '0'])

test.run(arguments='warnings=0 profile=no profile=true')
check(['0', '1'])

test.run(arguments='warnings=irgendwas',
         stderr = """
scons: *** Error converting option: warnings
Invalid value for boolean option: irgendwas
File "SConstruct", line 10, in ?
""", status=2)


#### test EnumOption ####

test.write('SConstruct', """
from SCons.Options import EnumOption

list_of_libs = Split('x11 gl qt ical')

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    EnumOption('debug', 'debug output and symbols', 'no',
               allowed_values=('yes', 'no', 'full'),
               map={}, ignorecase=0),  # case sensitive
    EnumOption('guilib', 'gui lib to use', 'gtk',
               allowed_values=('motif', 'gtk', 'kde'),
               map={}, ignorecase=1), # case insensitive
    EnumOption('some', 'some option', 'xaver',
               allowed_values=('xaver', 'eins'),
               map={}, ignorecase=2), # make lowercase
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['debug']
print env['guilib']
print env['some']

Default(env.Alias('dummy', None))
""")


test.run(); check(['no', 'gtk', 'xaver'])
test.run(arguments='debug=yes guilib=Motif some=xAVER')
check(['yes', 'Motif', 'xaver'])
test.run(arguments='debug=full guilib=KdE some=EiNs')
check(['full', 'KdE', 'eins'])

test.run(arguments='debug=FULL',
         stderr = """
scons: *** Invalid value for option debug: FULL
File "SConstruct", line 19, in ?
""", status=2)

test.run(arguments='guilib=IrGeNdwas',
         stderr = """
scons: *** Invalid value for option guilib: irgendwas
File "SConstruct", line 19, in ?
""", status=2)

test.run(arguments='some=IrGeNdwas',
         stderr = """
scons: *** Invalid value for option some: irgendwas
File "SConstruct", line 19, in ?
""", status=2)
         


#### test ListOption ####

test.write('SConstruct', """
from SCons.Options import ListOption

list_of_libs = Split('x11 gl qt ical')

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    ListOption('shared',
               'libraries to build as shared libraries',
               'all',
               names = list_of_libs),
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['shared']
if 'ical' in env['shared']: print '1'
else: print '0'
for x in  env['shared']:
    print x,
print
print env.subst('$shared')
Default(env.Alias('dummy', None))
""")

test.run()
check(['all', '1', 'gl ical qt x11', 'gl ical qt x11'])
test.run(arguments='shared=none')
check(['none', '0', '', ''])
test.run(arguments='shared=')
check(['none', '0', '', ''])
test.run(arguments='shared=x11,ical')
check(['ical,x11', '1', 'ical x11', 'ical x11'])
test.run(arguments='shared=x11,,ical,,')
check(['ical,x11', '1', 'ical x11', 'ical x11'])


test.run(arguments='shared=foo',
         stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
File "SConstruct", line 14, in ?
""", status=2)

# be paranoid in testing some more combinations

test.run(arguments='shared=foo,ical',
         stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
File "SConstruct", line 14, in ?
""", status=2)

test.run(arguments='shared=ical,foo',
         stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
File "SConstruct", line 14, in ?
""", status=2)

test.run(arguments='shared=ical,foo,x11',
         stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo
File "SConstruct", line 14, in ?
""", status=2)

test.run(arguments='shared=foo,x11,,,bar',
         stderr = """
scons: *** Error converting option: shared
Invalid value(s) for option: foo,bar
File "SConstruct", line 14, in ?
""", status=2)


#### test PackageOption ####

test.write('SConstruct', """
from SCons.Options import PackageOption

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    PackageOption('x11',
                  'use X11 installed here (yes = search some places',
                  'yes'),
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['x11']
Default(env.Alias('dummy', None))
""")

test.run()
check(['1'])
test.run(arguments='x11=no'); check(['0'])
test.run(arguments='x11=0'); check(['0'])
test.run(arguments='"x11=%s"' % test.workpath()); check([test.workpath()])

test.run(arguments='x11=/non/existing/path/',
         stderr = """
scons: *** Path does not exist for option x11: /non/existing/path/
File "SConstruct", line 11, in ?
""", status=2)
         


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
scons: *** Path does not exist for option qtdir: %s
File "SConstruct", line 12, in ?
""" % qtpath, status=2)

test.run(arguments='"qt_libraries=%s"' % qtpath,
         stderr = """
scons: *** Path does not exist for option qt_libraries: %s
File "SConstruct", line 12, in ?
""" % qtpath, status=2)


### test help messages ####

workpath = test.workpath()
qtpath  = os.path.join(workpath, 'qt')
libpath = os.path.join(qtpath, 'lib')
libdirvar = os.path.join('$qtdir', 'lib')
         
test.write('SConstruct', """
from SCons.Options import BoolOption, EnumOption, ListOption, \
   PackageOption, PathOption

list_of_libs = Split('x11 gl qt ical')
qtdir = r'%(qtdir)s'

opts = Options(args=ARGUMENTS)
opts.AddOptions(
    BoolOption('warnings', 'compilation with -Wall and similiar', 1),
    BoolOption('profile', 'create profiling informations', 0),
    EnumOption('debug', 'debug output and symbols', 'no',
               allowed_values=('yes', 'no', 'full'),
               map={}, ignorecase=0),  # case sensitive
    EnumOption('guilib', 'gui lib to use', 'gtk',
               allowed_values=('motif', 'gtk', 'kde'),
               map={}, ignorecase=1), # case insensitive
    EnumOption('some', 'some option', 'xaver',
               allowed_values=('xaver', 'eins'),
               map={}, ignorecase=2), # make lowercase
    ListOption('shared',
               'libraries to build as shared libraries',
               'all',
               names = list_of_libs),
    PackageOption('x11',
                  'use X11 installed here (yes = search some places)',
                  'yes'), PathOption('qtdir', 'where the root of Qt is installed', qtdir),
    PathOption('qt_libraries',
               'where the Qt library is installed',
               r'%(libdirvar)s'),
    )

env = Environment(options=opts)
Help(opts.GenerateHelpText(env))

print env['warnings']
print env['profile']

Default(env.Alias('dummy', None))
""" % {'qtdir': qtpath, 'libdirvar': libdirvar, 'libdir': libpath})


test.run(arguments='-h',
         stdout = """scons: Reading SConscript files ...
scons: done reading SConscript files.

warnings: compilation with -Wall and similiar (yes|no)
    default: 1
    actual: 1

profile: create profiling informations (yes|no)
    default: 0
    actual: 0

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
    actual: 1

qtdir: where the root of Qt is installed ( /path/to/qtdir )
    default: %(qtdir)s
    actual: %(qtdir)s

qt_libraries: where the Qt library is installed ( /path/to/qt_libraries )
    default: %(qtdir_lib)s
    actual: %(libdir)s

Use scons -H for help about command-line options.
""" % {'qtdir': qtpath, 'qtdir_lib' : os.path.join('$qtdir', 'lib'),
       'libdirvar': libdirvar, 'libdir': libpath})


test.pass_test()
