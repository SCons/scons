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
Testing the 'qt' tool, i.e. support for .ui files and automatic
generation of qt's moc files.
"""

import TestSCons
import os.path

python = TestSCons.python
_exe = TestSCons._exe
_dll = TestSCons._dll
lib_ = TestSCons.lib_

test = TestSCons.TestSCons()

test.subdir( 'qt', ['qt', 'bin'], ['qt', 'include'], ['qt', 'lib'] )

# create a dummy qt installation

test.write(['qt', 'bin', 'mymoc.py'], """
import getopt
import sys
import string
import re
cmd_opts, args = getopt.getopt(sys.argv[1:], 'io:', [])
output = None
impl = 0
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    elif opt == '-i': impl = 1
    else: opt_string = opt_string + ' ' + opt
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
    else:
        if source:
            sys.exit(1)
        source = open(arg, 'rb')
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

test.run(chdir=test.workpath('qt','lib'), arguments = '.')

QT = test.workpath('qt')
QT_LIB = 'myqt'
QT_MOC = '%s %s' % (python, test.workpath('qt','bin','mymoc.py'))
QT_UIC = '%s %s' % (python, test.workpath('qt','bin','myuic.py'))

# 3 test cases with 3 different operation modes

def createSConstruct(test,place):
    test.write(place, """
env = Environment(QTDIR = r'%s',
                  QT_LIB = r'%s',
                  QT_MOC = r'%s',
                  QT_UIC = r'%s',
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
""" % (QT, QT_LIB, QT_MOC, QT_UIC))

test.subdir( 'work1', 'work2', 'work3', 'work4' )

# 1. create a moc file from a header file.

aaa_exe = 'aaa' + _exe
moc = 'moc_aaa.cc'

createSConstruct(test, ['work1', 'SConstruct'])
test.write( ['work1', 'SConscript'], """
Import("env")
env.Program(target = 'aaa', source = 'aaa.cpp')
""")

test.write(['work1', 'aaa.cpp'], r"""
#include "aaa.h"
int main() { aaa(); return 0; }
""")

test.write(['work1', 'aaa.h'], r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT;
""")

test.run(chdir='work1', arguments = aaa_exe)
test.up_to_date(chdir='work1', options = '-n', arguments=aaa_exe)

test.up_to_date(chdir='work1', options = '-n', arguments = aaa_exe)
test.write(['work1', 'aaa.h'], r"""
/* a change */
#include "my_qobject.h"
void aaa(void) Q_OBJECT;
""")
test.not_up_to_date(chdir='work1', options='-n', arguments = moc)
test.run(program = test.workpath('work1', aaa_exe), stdout = 'aaa.h\n')

test.run(chdir='work1',
         arguments = "build_dir=1 " +
                     test.workpath('work1', 'build', aaa_exe) )
test.run(chdir='work1',
         arguments = "build_dir=1 chdir=1 " +
                     test.workpath('work1', 'build', aaa_exe) )

test.fail_test( not os.path.exists(test.workpath('work1', 'build', moc)) )

# 2. create .cpp, .h, moc_....cpp from .ui file

aaa_dll = lib_ + 'aaa' + _dll
moc = 'moc_aaa.cc'
cpp = 'aaa.cc'
h = 'aaa.h'

createSConstruct(test, ['work2', 'SConstruct'])
test.write(['work2', 'SConscript'], """
Import("env")
env.SharedLibrary(target = 'aaa', source = ['aaa.ui', 'useit.cpp'])
""")

test.write(['work2', 'aaa.ui'], r"""
void aaa(void)
""")

test.write(['work2', 'useit.cpp'], r"""
#include "aaa.h"
void useit() {
  aaa();
}
""")

test.run(chdir='work2', arguments = aaa_dll)
test.up_to_date(chdir='work2', options='-n',arguments = aaa_dll)
test.write(['work2', 'aaa.ui'], r"""
/* a change */
void aaa(void)
""")
test.not_up_to_date(chdir='work2', options = '-n', arguments = moc)
test.not_up_to_date(chdir='work2', options = '-n', arguments = cpp)
test.not_up_to_date(chdir='work2', options = '-n', arguments = h)
test.run(chdir='work2', arguments = aaa_dll)
test.write(['work2', 'aaa.ui.h'], r"""
/* test dependency to .ui.h */
""")
test.not_up_to_date(chdir='work2', options = '-n', arguments = cpp)
test.up_to_date(chdir='work2', options = '-n', arguments = h)
test.up_to_date(chdir='work2', options = '-n', arguments = moc)

test.run(chdir='work2',
         arguments = "build_dir=1 " +
                     test.workpath('work2', 'build', aaa_dll) )
test.run(chdir='work2',
         arguments = "build_dir=1 chdir=1 " +
                     test.workpath('work2', 'build', aaa_dll) )

test.fail_test(not os.path.exists(test.workpath('work2','build',moc)) or
               not os.path.exists(test.workpath('work2','build',cpp)) or
               not os.path.exists(test.workpath('work2','build',h)))

# 3. create a moc file from a cpp file

lib_aaa = lib_ + 'aaa.a'
moc = 'moc_aaa.cc'

createSConstruct(test, ['work3', 'SConstruct'])
test.write(['work3', 'SConscript'], """
Import("env")
env.StaticLibrary(target = '%s', source = ['aaa.cpp','useit.cpp'])
""" % lib_aaa)

test.write(['work3', 'aaa.h'], r"""
void aaa(void);
""")

test.write(['work3', 'aaa.cpp'], r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT
#include "%s"
""" % moc)

test.write(['work3', 'useit.cpp'], r"""
#include "aaa.h"
void useit() {
  aaa();
}
""")

test.run(chdir='work3', arguments = lib_aaa)
test.up_to_date(chdir='work3', options = '-n', arguments = lib_aaa)
test.write(['work3', 'aaa.cpp'], r"""
#include "my_qobject.h"
/* a change */
void aaa(void) Q_OBJECT
#include "%s"
""" % moc)
test.not_up_to_date(chdir='work3', options = '-n', arguments = moc)

test.run(chdir='work3',
         arguments = "build_dir=1 " +
                     test.workpath('work3', 'build', lib_aaa) )
test.run(chdir='work3',
         arguments = "build_dir=1 chdir=1 " +
                     test.workpath('work3', 'build', lib_aaa) )

test.fail_test(not os.path.exists(test.workpath('work3', 'build', moc)))


# look if qt is installed, and try out all builders

if os.environ.get('QTDIR', None):

    QTDIR=os.environ['QTDIR']
    

    test.write( ['work4', 'SConstruct'],"""
import os
dummy_env = Environment()
ENV = dummy_env['ENV']
try:
    PATH=ARGUMENTS['PATH']
    if ENV.has_key('PATH'):
        ENV_PATH = PATH + ':' + ENV['PATH']
    else:
        Exit(0) # this is certainly a weird system :-)
except KeyError:
    if ENV.has_key('PATH'):
        ENV_PATH=dummy_env['ENV']['PATH']
    else:
        ENV_PATH=''
    pass

env = Environment(tools=['default','qt'],
                  ENV={'PATH':ENV_PATH,
                       'HOME':os.getcwd()},
                       # moc / uic want to write stuff in ~/.qt
                  CXXFILESUFFIX=".cpp")

conf = env.Configure()
if not conf.CheckLib(env.subst("$QT_LIB")):
    conf.env['QT_LIB'] = 'qt-mt'
    if not conf.CheckLib(env.subst("$QT_LIB")):
         Exit(0)
env = conf.Finish()

env.Program('test_realqt', ['mocFromCpp.cpp',
                            'mocFromH.cpp',
                            'anUiFile.ui',
                            'main.cpp'])
""")

    test.write( ['work4', 'mocFromCpp.h'],"""
void mocFromCpp();
""")

    test.write( ['work4', 'mocFromCpp.cpp'],"""
#include <qobject.h>
#include "mocFromCpp.h"
class MyClass1 : public QObject {
  Q_OBJECT
  public:
  MyClass1() : QObject() {};
  public slots:
  void myslot() {};
};
void mocFromCpp() {
  MyClass1 myclass;
}
#include "moc_mocFromCpp.cpp"
""")

    test.write( ['work4', 'mocFromH.h'],"""
#include <qobject.h>
class MyClass2 : public QObject {
  Q_OBJECT;
  public:
  MyClass2();
  public slots:
  void myslot();
};
void mocFromH();
""")
    
    test.write( ['work4', 'mocFromH.cpp'],"""
#include "mocFromH.h"
    
MyClass2::MyClass2() : QObject() {}
void MyClass2::myslot() {}
void mocFromH() {
  MyClass2 myclass;
}
""")
    
    test.write( ['work4', 'anUiFile.ui'],"""
<!DOCTYPE UI><UI>
<class>MyWidget</class>
<widget>
    <class>QWidget</class>
    <property name="name">
        <cstring>MyWidget</cstring>
    </property>
    <property name="caption">
        <string>MyWidget</string>
    </property>
</widget>
<layoutdefaults spacing="6" margin="11"/>
</UI>
""")

    test.write( ['work4', 'main.cpp'], """
#include "mocFromCpp.h"
#include "mocFromH.h"
#include "anUiFile.h"
int main() {
  mocFromCpp();
  mocFromH();
  MyWidget mywidget();
}
""")

    test.run(chdir='work4', arguments="test_realqt" + _exe)

    QTDIR=os.environ['QTDIR']
    del os.environ['QTDIR']

    test.run(chdir='work4', arguments="-c test_realqt" + _exe)
    test.run(chdir='work4', arguments="PATH=%s/bin test_realqt%s"%(QTDIR,_exe))
    
else:
    print "Could not find QT, skipping test(s)."


test.pass_test()
