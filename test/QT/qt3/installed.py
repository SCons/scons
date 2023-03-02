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
Look if qt3 is installed, and try out all builders.
"""

import os
import sys

import TestSCons

test = TestSCons.TestSCons()

if not os.environ.get('QTDIR', None):
    x ="External environment variable $QTDIR not set; skipping test(s).\n"
    test.skip_test(x)

test.Qt_dummy_installation()

QTDIR=os.environ['QTDIR']


test.write('SConstruct', """\
import os
dummy_env = Environment()
ENV = dummy_env['ENV']
try:
    PATH=ARGUMENTS['PATH']
    if 'PATH' in ENV:
        ENV_PATH = PATH + os.pathsep + ENV['PATH']
    else:
        Exit(0) # this is certainly a weird system :-)
except KeyError:
    ENV_PATH=ENV.get('PATH', '')

env = Environment(tools=['default','qt3'],
                  ENV={'PATH':ENV_PATH,
                       'PATHEXT':os.environ.get('PATHEXT'),
                       'HOME':os.getcwd(),
                       'SystemRoot':ENV.get('SystemRoot')},
                       # moc / uic want to write stuff in ~/.qt
                  CXXFILESUFFIX=".cpp")

conf = env.Configure()
if not conf.CheckLib(env.subst("$QT3_LIB"), autoadd=0):
    conf.env['QT3_LIB'] = 'qt-mt'
    if not conf.CheckLib(env.subst("$QT3_LIB"), autoadd=0):
         Exit(0)
env = conf.Finish()
VariantDir('bld', '.')
env.Program('bld/test_realqt', ['bld/mocFromCpp.cpp',
                                'bld/mocFromH.cpp',
                                'bld/anUiFile.ui',
                                'bld/main.cpp'])
""")

test.write('mocFromCpp.h', """\
void mocFromCpp();
""")

test.write('mocFromCpp.cpp', """\
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
#include "mocFromCpp.moc"
""")

test.write('mocFromH.h', """\
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

test.write('mocFromH.cpp', """\
#include "mocFromH.h"

MyClass2::MyClass2() : QObject() {}
void MyClass2::myslot() {}
void mocFromH() {
  MyClass2 myclass;
}
""")

test.write('anUiFile.ui', """\
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
<includes>
    <include location="local" impldecl="in implementation">anUiFile.ui.h</include>
</includes>
<slots>
    <slot>testSlot()</slot>
</slots>
<layoutdefaults spacing="6" margin="11"/>
</UI>
""")

test.write('anUiFile.ui.h', r"""
#include <stdio.h>
#if QT_VERSION >= 0x030100
void MyWidget::testSlot()
{
    printf("Hello World\n");
}
#endif
""")

test.write('main.cpp', r"""
#include <qapp.h>
#include "mocFromCpp.h"
#include "mocFromH.h"
#include "anUiFile.h"
#include <stdio.h>

int main(int argc, char **argv) {
  QApplication app(argc, argv);
  mocFromCpp();
  mocFromH();
  MyWidget mywidget;
#if QT_VERSION >= 0x030100
  mywidget.testSlot();
#else
  printf("Hello World\n");
#endif
  return 0;
}
""")

test.run(arguments="--warn=no-tool-qt-deprecated bld/test_realqt" + TestSCons._exe)

test.run(
    program=test.workpath("bld", "test_realqt"),
    arguments="--warn=no-tool-qt-deprecated",
    stdout=None,
    status=None,
    stderr=None,
)

if test.stdout() != "Hello World\n" or test.stderr() != '' or test.status:
    sys.stdout.write(test.stdout())
    sys.stderr.write(test.stderr())
    # The test might be run on a system that doesn't have an X server
    # running, or may be run by an ID that can't connect to the server.
    # If so, then print whatever it showed us (which is in and of itself
    # an indication that it built correctly) but don't fail the test.
    expect = 'cannot connect to X server'
    test.fail_test(test.stdout())
    test.fail_test(expect not in test.stderr())
    if test.status != 1 and (test.status >> 8) != 1:
        sys.stdout.write('test_realqt returned status %s\n' % test.status)
        test.fail_test()

QT3DIR = os.environ['QTDIR']
PATH = os.environ['PATH']
os.environ['QTDIR'] = ''
os.environ['PATH'] = '.'

test.run(
    stderr=None,
    arguments="-c bld/test_realqt" + TestSCons._exe,
)

expect1 = "scons: warning: Could not detect qt3, using empty QT3DIR"
expect2 = "scons: warning: Could not detect qt3, using moc executable as a hint"

test.fail_test(expect1 not in test.stderr() and expect2 not in test.stderr())

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
