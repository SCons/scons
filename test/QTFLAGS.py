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
Testing the configuration mechanisms of the 'qt' tool.
"""

import TestSCons
import os.path

python = TestSCons.python
_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.subdir( 'qt', ['qt', 'bin'], ['qt', 'include'], ['qt', 'lib'] )

# create a dummy qt installation

test.write(['qt', 'bin', 'mymoc.py'], """
import getopt
import sys
import string
import re
cmd_opts, args = getopt.getopt(sys.argv[1:], 'wzio:', [])
output = None
impl = 0
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    elif opt == '-i': impl = 1
    else: opt_string = opt_string + ' ' + opt
output.write( "/* mymoc.py%s */\\n" % opt_string)
for a in args:
    contents = open(a, 'rb').read()
    subst = r'{ my_qt_symbol( "' + a + '\\\\n" ); }'
    if impl:
        contents = re.sub( r'#include.*', '', contents )
    output.write(string.replace(contents, 'Q_OBJECT', subst))
output.close()
sys.exit(0)
""" )

test.write(['qt', 'bin', 'myuic.py'], """
import sys
import string
output_arg = 0
impl_arg = 0
impl = None
source = None
opt_string = ''
for arg in sys.argv[1:]:
    if output_arg:
        output = open(arg, 'wb')
        output_arg = 0
    elif impl_arg:
        impl = arg
        impl_arg = 0
    elif arg == "-o":
        output_arg = 1
    elif arg == "-impl":
        impl_arg = 1
    elif arg[0:1] == "-":
        opt_string = opt_string + ' ' + arg
    else:
        if source:
            sys.exit(1)
        source = open(arg, 'rb')
output.write("/* myuic.py%s */\\n" % opt_string)
if impl:
    output.write( '#include "' + impl + '"\\n' )
else:
    output.write( '#include "my_qobject.h"\\n' + source.read() + " Q_OBJECT \\n" )
output.close()
sys.exit(0)
""" )

test.write(['qt', 'include', 'my_qobject.h'], r"""
#define Q_OBJECT ;
void my_qt_symbol(const char *arg);
""")

test.write(['qt', 'lib', 'my_qobject.cpp'], r"""
#include "../include/my_qobject.h"
#include <stdio.h>
void my_qt_symbol(const char *arg) {
  printf( arg );
}
""")

test.write(['qt', 'lib', 'SConstruct'], r"""
env = Environment()
env.StaticLibrary( 'myqt', 'my_qobject.cpp' )
""")

test.run(chdir=test.workpath('qt','lib'), arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

QT = test.workpath('qt')
QT_LIB = 'myqt'
QT_MOC = '%s %s' % (python, test.workpath('qt','bin','mymoc.py'))
QT_UIC = '%s %s' % (python, test.workpath('qt','bin','myuic.py'))

# 3 test cases with 3 different operation modes

def createSConstruct(test,place,overrides):
    test.write(place, """
env = Environment(QTDIR = r'%s',
                  QT_LIB = r'%s',
                  QT_MOC = r'%s',
                  QT_UIC = r'%s',
                  %s
                  tools=['default','qt'])
if ARGUMENTS.get('build_dir', 0):
    if ARGUMENTS.get('chdir', 0):
        SConscriptChdir(1)
    else:
        SConscriptChdir(0)
    BuildDir('build', '.', duplicate=1)
    sconscript = Dir('build').File('SConscript')
else:
    sconscript = File('SConscript')
Export("env")
SConscript( sconscript )
""" % (QT, QT_LIB, QT_MOC, QT_UIC, overrides))


createSConstruct(test, ['SConstruct'],
                 """QT_UICIMPLFLAGS='-x',
                    QT_UICDECLFLAGS='-y',
                    QT_MOCFROMHFLAGS='-z',
                    QT_MOCFROMCXXFLAGS='-i -w',
                    QT_UICDECLPREFIX='uic-',
                    QT_UICDECLSUFFIX='.hpp',
                    QT_UICIMPLPREFIX='',
                    QT_UICIMPLSUFFIX='.cxx',
                    QT_MOCHPREFIX='mmm',
                    QT_MOCHSUFFIX='.cxx',
                    QT_MOCCXXPREFIX='moc',
                    QT_MOCCXXSUFFIX='.inl',
                    QT_UISUFFIX='.myui',""")
test.write('SConscript',"""
Import("env")
env.Program('mytest', ['mocFromH.cpp',
                       'mocFromCpp.cpp',
                       'an_ui_file.myui',
                       'another_ui_file.myui',
                       'main.cpp'])
""")

test.write('mocFromH.hpp', """
#include "my_qobject.h"
void mocFromH() Q_OBJECT
""")

test.write('mocFromH.cpp', """
#include "mocFromH.hpp"
""")

test.write('mocFromCpp.cpp', """
#include "my_qobject.h"
void mocFromCpp() Q_OBJECT
#include "mocmocFromCpp.inl"
""")

test.write('an_ui_file.myui', """
void an_ui_file()
""")

test.write('another_ui_file.myui', """
void another_ui_file()
""")

test.write('another_ui_file.desc.hpp', """
/* just a dependency checker */
""")

test.write('main.cpp', """
#include "mocFromH.hpp"
#include "uic-an_ui_file.hpp"
#include "uic-another_ui_file.hpp"
void mocFromCpp();

int main() {
  mocFromH();
  mocFromCpp();
  an_ui_file();
  another_ui_file();
}
""")

test.run( arguments = "mytest" + _exe )
                       
test.must_exist('mmmmocFromH.cxx',
                'mocmocFromCpp.inl',
                'an_ui_file.cxx',
                'uic-an_ui_file.hpp',
                'mmman_ui_file.cxx',
                'another_ui_file.cxx',
                'uic-another_ui_file.hpp',
                'mmmanother_ui_file.cxx')

def _flagTest(test,fileToContentsStart):
    import string
    for f,c in fileToContentsStart.items():
        if string.find(test.read(f), c) != 0:
            return 1
    return 0

test.fail_test(_flagTest(test, {'mmmmocFromH.cxx':'/* mymoc.py -z */',
                                'mocmocFromCpp.inl':'/* mymoc.py -w */',
                                'an_ui_file.cxx':'/* myuic.py -x */',
                                'uic-an_ui_file.hpp':'/* myuic.py -y */',
                                'mmman_ui_file.cxx':'/* mymoc.py -z */'}))

test.pass_test()
