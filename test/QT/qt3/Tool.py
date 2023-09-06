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
Verify that applying env.Tool('qt3') after running Configure checks
works properly.  This was broken in 0.96.95.

The configuration here is a moderately stripped-down version of the
real-world configuration for lprof (lprof.sourceforge.net).  It's probably
not completely minimal, but we're leaving it as-is since it represents a
good real-world sanity check on the interaction of some key subsystems.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

if not os.environ.get('QTDIR', None):
    x ="External environment variable $QTDIR not set; skipping test(s).\n"
    test.skip_test(x)

test.write('SConstruct', """
import os

def DoWithVariables(variables, prefix, what):
  saved_variables = { }
  for name in variables.keys():
    saved_variables[ name ] = env[ name ][:]
    env[ name ].append(variables[ name ])

  result = what()
  
  for name in saved_variables.keys():
    env[ name ] = saved_variables[ name ]
    env[ prefix+name ] = variables[ name ]

  return result

def CheckForQtAt(context, qtdir):
  context.Message('Checking for Qt at %s... ' % qtdir)
  libp = os.path.join(qtdir, 'lib')
  cppp = os.path.join(qtdir, 'include')
  result = AttemptLinkWithVariables(context,
      { "LIBS": "qt-mt", "LIBPATH": libp , "CPPPATH": cppp },
      '''
#include <qapplication.h>
int main(int argc, char **argv) { 
  QApplication qapp(argc, argv);
  return 0;
}
''',".cpp","QT_")
  context.Result(result)
  return result

def CheckForQt(context):
  # list is currently POSIX centric - what happens with Windows?
  potential_qt_dirs = [
    "/usr/share/qt3", # Debian unstable
    "/usr/share/qt",
    "/usr",
    "/usr/local",
    "/usr/lib/qt3", # Suse
    "/usr/lib/qt",
    "/usr/qt/3", # Gentoo
    "/usr/pkg/qt3" # pkgsrc (NetBSD)
    ]

  if 'QTDIR' in os.environ:
    potential_qt_dirs.insert(0, os.environ['QTDIR'])
  
  if env[ 'qt_directory' ] != "/":
     uic_path = os.path.join(env['qt_directory'], 'bin', 'uic')
     if os.path.isfile(uic_path):
        potential_qt_dirs.insert(0, env[ 'qt_directory' ])
     else:
        print("QT not found. Invalid qt_directory value - failed to find uic.")
        return 0

  for i in potential_qt_dirs:
    context.env.Replace(QT3DIR = i)
    if CheckForQtAt(context, i):
       # additional checks to validate QT installation
       if not os.path.isfile(os.path.join(i, 'bin', 'uic')):
          print("QT - failed to find uic.")
          return 0
       if not os.path.isfile(os.path.join(i, 'bin', 'moc')):
          print("QT - failed to find moc.")
          return 0
       if not os.path.exists(os.path.join(i, 'lib')):
          print("QT - failed to find QT lib path.")
          return 0
       if not os.path.exists(os.path.join(i, 'include')):
          print("QT - failed to find QT include path.")
          return 0
       return 1
    else:
      if i==env['qt_directory']:
        print("QT directory not valid.  Failed QT test build.")
        return 0
  return 0

def AttemptLinkWithVariables(context, variables, code, extension, prefix):
  return DoWithVariables(variables, prefix,
                         lambda: context.TryLink(code, extension))

env = Environment(CPPPATH=['.'], LIBPATH=['.'], LIBS=[])

opts = Variables('lprof.conf') 
opts.Add(PathVariable("qt_directory", "Path to Qt directory", "/"))
opts.Update(env)

env['QT3_LIB'] = 'qt-mt'
config = env.Configure(custom_tests = {
    'CheckForQt' : CheckForQt,
})

if not config.CheckForQt():
    print("Failed to find valid QT environment.")
    Exit(1)

env.Tool('qt3', ['$TOOL_PATH'])
""")

test.run(arguments='.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
