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

_python_ = TestSCons._python_
_exe = TestSCons._exe

test = TestSCons.TestSCons()

test.Qt_dummy_installation()
test.subdir('work1', 'work2')

test.run(
    chdir=test.workpath('qt', 'lib'),
    arguments='.',
    stderr=TestSCons.noisy_ar,
    match=TestSCons.match_re_dotall,
)

QT = test.workpath('qt')
QT_LIB = 'myqt'
QT_MOC = '%s %s' % (_python_, test.workpath('qt', 'bin', 'mymoc.py'))
QT_UIC = '%s %s' % (_python_, test.workpath('qt', 'bin', 'myuic.py'))

def createSConstruct(test, place, overrides):
    test.write(place, """\
env = Environment(
    tools=['default','qt'],
    QTDIR = r'%s',
    QT_LIB = r'%s',
    QT_MOC = r'%s',
    QT_UIC = r'%s',
    %s  # last because 'overrides' may add comma
)
if ARGUMENTS.get('variant_dir', 0):
    if ARGUMENTS.get('chdir', 0):
        SConscriptChdir(1)
    else:
        SConscriptChdir(0)
    VariantDir('build', '.', duplicate=1)
    sconscript = Dir('build').File('SConscript')
else:
    sconscript = File('SConscript')
Export("env")
SConscript(sconscript)
""" % (QT, QT_LIB, QT_MOC, QT_UIC, overrides))


createSConstruct(test, ['work1', 'SConstruct'],
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
test.write(['work1', 'SConscript'],"""
Import("env")
env.Program('mytest', ['mocFromH.cpp',
                       'mocFromCpp.cpp',
                       'an_ui_file.myui',
                       'another_ui_file.myui',
                       'main.cpp'])
""")

test.write(['work1', 'mocFromH.hpp'], """
#include "my_qobject.h"
void mocFromH() Q_OBJECT
""")

test.write(['work1', 'mocFromH.cpp'], """
#include "mocFromH.hpp"
""")

test.write(['work1', 'mocFromCpp.cpp'], """
#include "my_qobject.h"
void mocFromCpp() Q_OBJECT
#include "mocmocFromCpp.inl"
""")

test.write(['work1', 'an_ui_file.myui'], """
void an_ui_file()
""")

test.write(['work1', 'another_ui_file.myui'], """
void another_ui_file()
""")

test.write(['work1', 'another_ui_file.desc.hpp'], """
/* just a dependency checker */
""")

test.write(['work1', 'main.cpp'], """
#include "mocFromH.hpp"
#include "uic-an_ui_file.hpp"
#include "uic-another_ui_file.hpp"
void mocFromCpp();

int main(void) {
  mocFromH();
  mocFromCpp();
  an_ui_file();
  another_ui_file();
}
""")

test.run(chdir = 'work1', arguments = "mytest" + _exe)

test.must_exist(['work1', 'mmmmocFromH.cxx'],
                ['work1', 'mocmocFromCpp.inl'],
                ['work1', 'an_ui_file.cxx'],
                ['work1', 'uic-an_ui_file.hpp'],
                ['work1', 'mmman_ui_file.cxx'],
                ['work1', 'another_ui_file.cxx'],
                ['work1', 'uic-another_ui_file.hpp'],
                ['work1', 'mmmanother_ui_file.cxx'])

def _flagTest(test,fileToContentsStart):
    for f,c in fileToContentsStart.items():
        if test.read(test.workpath('work1', f), mode='r').find(c) != 0:
            return 1
    return 0

test.fail_test(_flagTest(test, {'mmmmocFromH.cxx':'/* mymoc.py -z */',
                                'mocmocFromCpp.inl':'/* mymoc.py -w */',
                                'an_ui_file.cxx':'/* myuic.py -x */',
                                'uic-an_ui_file.hpp':'/* myuic.py -y */',
                                'mmman_ui_file.cxx':'/* mymoc.py -z */'}))

test.write(['work2', 'SConstruct'], """
import os.path
env1 = Environment(tools=['qt'],
                   QTDIR = r'%(QTDIR)s',
                   QT_BINPATH='$QTDIR/bin64',
                   QT_LIBPATH='$QTDIR/lib64',
                   QT_CPPPATH='$QTDIR/h64')

cpppath = env1.subst('$CPPPATH')
if os.path.normpath(cpppath) != os.path.join(r'%(QTDIR)s', 'h64'):
    print(cpppath)
    Exit(1)
libpath = env1.subst('$LIBPATH')
if os.path.normpath(libpath) != os.path.join(r'%(QTDIR)s', 'lib64'):
    print(libpath)
    Exit(2)
qt_moc = env1.subst('$QT_MOC')
if os.path.normpath(qt_moc) != os.path.join(r'%(QTDIR)s', 'bin64', 'moc'):
    print(qt_moc)
    Exit(3)

env2 = Environment(tools=['default', 'qt'],
                   QTDIR = None,
                   QT_LIB = None,
                   QT_CPPPATH = None,
                   QT_LIBPATH = None)

env2.Program('main.cpp')
""" % {'QTDIR':QT})

test.write(['work2', 'main.cpp'], """
int main(void) { return 0; }
""")

# Ignore stderr, because if Qt is not installed,
# there may be a warning about an empty QTDIR on stderr.
test.run(chdir='work2', stderr=None)

test.must_exist(['work2', 'main' + _exe])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
