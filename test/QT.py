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

import os.path
import re
import string

import TestSCons

python = TestSCons.python
_exe = TestSCons._exe
lib_ = TestSCons.lib_
_lib = TestSCons._lib
dll_ = TestSCons.dll_
_dll = TestSCons._dll
_shobj = TestSCons._shobj

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

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
import os.path
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
        sourceFile = arg
if impl:
    output.write( '#include "' + impl + '"\\n' )
    if string.find(source.read(), '// ui.h') != -1:
        output.write(
           '#include "' +
           os.path.basename(os.path.splitext(sourceFile)[0]) + '.ui.h"\\n')
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
         stderr=TestSCons.noisy_ar)

QT = test.workpath('qt')
QT_LIB = 'myqt'
QT_MOC = '%s %s' % (python, test.workpath('qt','bin','mymoc.py'))
QT_UIC = '%s %s' % (python, test.workpath('qt','bin','myuic.py'))

##############################################################################
# Test cases with different operation modes

def createSConstruct(test,place):
    test.write(place, """
if ARGUMENTS.get('noqtdir', 0): QTDIR=None
else: QTDIR=r'%s'
env = Environment(QTDIR = QTDIR,
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

test.subdir( 'work1', 'work2', 'work3', 'work4',
             'work5', 'work6', 'work7', 'work8',
             'work9', ['work9', 'local_include'],
             'work10', ['work10', 'sub'], ['work10', 'sub', 'local_include'],
             'work11', ['work11', 'include'], ['work11', 'ui'],
             'work12')

##############################################################################
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

##############################################################################
# 2. create .cpp, .h, moc_....cpp from .ui file

aaa_dll = dll_ + 'aaa' + _dll
moc = 'moc_aaa.cc'
cpp = 'uic_aaa.cc'
obj = os.path.splitext(cpp)[0] + _shobj
h = 'aaa.h'

createSConstruct(test, ['work2', 'SConstruct'])
test.write(['work2', 'SConscript'], """
Import("env")
env.SharedLibrary(target = 'aaa', source = ['aaa.ui', 'useit.cpp'])
""")

test.write(['work2', 'aaa.ui'], r"""
#if defined (_WIN32) || defined(__CYGWIN__)
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void aaa(void)
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
#if defined (_WIN32) || defined(__CYGWIN__)
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT
#endif
DLLEXPORT void aaa(void)
""")
test.not_up_to_date(chdir='work2', options = '-n', arguments = moc)
test.not_up_to_date(chdir='work2', options = '-n', arguments = cpp)
test.not_up_to_date(chdir='work2', options = '-n', arguments = h)
test.run(chdir='work2', arguments = aaa_dll)
test.write(['work2', 'aaa.ui.h'], r"""
/* test dependency to .ui.h */
""")
test.write(['work2', 'aaa.ui'], r"""
void aaa(void)
// ui.h
""")
test.run(chdir='work2', arguments = aaa_dll)
test.write(['work2', 'aaa.ui.h'], r"""
/* changed */
""")
test.not_up_to_date(chdir='work2', options = '-n', arguments = obj)
test.up_to_date(chdir='work2', options = '-n', arguments = cpp)
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

##############################################################################
# 3. create a moc file from a cpp file

lib_aaa = lib_ + 'aaa' + _lib
moc = 'aaa.moc'

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

test.run(chdir='work3', arguments = lib_aaa, stderr=TestSCons.noisy_ar)
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
                     test.workpath('work3', 'build', lib_aaa),
         stderr=TestSCons.noisy_ar )
test.run(chdir='work3',
         arguments = "build_dir=1 chdir=1 " +
                     test.workpath('work3', 'build', lib_aaa) )

test.fail_test(not os.path.exists(test.workpath('work3', 'build', moc)))

##############################################################################
# 4. Test with a copied environment.

createSConstruct(test, ['work4', 'SConstruct'])
test.write(['work4', 'SConscript'], """\
Import("env")
env.Append(CPPDEFINES = ['FOOBAZ'])
                                                                                
copy = env.Copy()
copy.Append(CPPDEFINES = ['MYLIB_IMPL'])
                                                                                
copy.SharedLibrary(
   target = 'MyLib',
   source = ['MyFile.cpp','MyForm.ui']
)
""")

test.write(['work4', 'MyFile.h'], r"""
void aaa(void);
""")

test.write(['work4', 'MyFile.cpp'], r"""
#include "MyFile.h"
void useit() {
  aaa();
}
""")

test.write(['work4', 'MyForm.ui'], r"""
void aaa(void)
""")

test.run(chdir='work4')
moc_MyForm = filter(lambda x: string.find(x, 'moc_MyForm') != -1,
                    string.split(test.stdout(), '\n'))
MYLIB_IMPL = filter(lambda x: string.find(x, 'MYLIB_IMPL') != -1, moc_MyForm)
if not MYLIB_IMPL:
    print "Did not find MYLIB_IMPL on moc_MyForm compilation line:"
    print test.stdout()
    test.fail_test()

##############################################################################
# 5. Test creation from a copied environment that already has QT variables.
#    This makes sure the tool initialization is re-entrant.

createSConstruct(test, ['work5', 'SConstruct'])
test.write( ['work5', 'SConscript'], """
Import("env")
env = env.Copy(tools=['qt'])
env.Program('main', 'main.cpp', CPPDEFINES=['FOO'], LIBS=[])
""")

test.write(['work5', 'main.cpp'], r"""
#include "foo5.h"
int main() { foo5(); return 0; }
""")

test.write(['qt', 'include', 'foo5.h'], """\
#include <stdio.h>
void
foo5(void)
{
#ifdef  FOO
    printf("qt/include/foo5.h\\n");
#endif
}
""")

test.run(chdir='work5')

main_exe = 'main' + _exe
test.run(program = test.workpath('work5', main_exe),
         stdout = 'qt/include/foo5.h\n')

##############################################################################
# 6. Test creation from a copied empty environment.

test.write(['work6', 'SConstruct'], """\
orig = Environment()
env = orig.Copy(QTDIR = r'%s',
                QT_LIB = r'%s',
                QT_MOC = r'%s',
                QT_UIC = r'%s',
                tools=['qt'])
env.Program('main', 'main.cpp', CPPDEFINES=['FOO'], LIBS=[])
""" % (QT, QT_LIB, QT_MOC, QT_UIC))

test.write(['work6', 'main.cpp'], r"""
#include "foo6.h"
int main() { foo6(); return 0; }
""")

test.write(['qt', 'include', 'foo6.h'], """\
#include <stdio.h>
void
foo6(void)
{
#ifdef  FOO
    printf("qt/include/foo6.h\\n");
#endif
}
""")

# we can receive warnings about a non detected qt (empty QTDIR)
# these are not critical, but maybe annoying
test.run(chdir='work6', stderr=None)

main_exe = 'main' + _exe
test.run(program = test.workpath('work6', main_exe),
         stderr = None,
         stdout = 'qt/include/foo6.h\n')

##############################################################################
# 7. look if qt is installed, and try out all builders

if os.environ.get('QTDIR', None):

    QTDIR=os.environ['QTDIR']
    

    test.write( ['work7', 'SConstruct'],"""
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

    test.write( ['work7', 'mocFromCpp.h'],"""
void mocFromCpp();
""")

    test.write( ['work7', 'mocFromCpp.cpp'],"""
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

    test.write( ['work7', 'mocFromH.h'],"""
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
    
    test.write( ['work7', 'mocFromH.cpp'],"""
#include "mocFromH.h"
    
MyClass2::MyClass2() : QObject() {}
void MyClass2::myslot() {}
void mocFromH() {
  MyClass2 myclass;
}
""")
    
    test.write( ['work7', 'anUiFile.ui'],"""
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

    test.write( ['work7', 'main.cpp'], """
#include "mocFromCpp.h"
#include "mocFromH.h"
#include "anUiFile.h"
int main() {
  mocFromCpp();
  mocFromH();
  MyWidget mywidget();
}
""")

    test.run(chdir='work7', arguments="test_realqt" + _exe)

    QTDIR=os.environ['QTDIR']
    del os.environ['QTDIR']

    test.run(chdir='work7', stderr=None, arguments="-c test_realqt" + _exe)
    test.fail_test(not test.match_re(test.stderr(), r"""
scons: warning: Could not detect qt, using empty QTDIR
File "SConstruct", line \d+, in .+
"""))

    test.run(chdir='work7', stderr=None,
             arguments="PATH=%s/bin test_realqt%s"%(QTDIR,_exe))
    
    test.fail_test(not test.match_re(test.stderr(), r"""
scons: warning: Could not detect qt, using moc executable as a hint \(QTDIR=%s\)
File "SConstruct", line \d+, in .+
""" % (re.escape(QTDIR))))

    
else:
    print "Could not find QT, skipping test(s)."

##############################################################################
# 8. test the $QT_AUTOBUILD_MOC_SOURCES variable
#
# This has been removed, but I'm leaving the test here, commented out,
# in case we ever resurrect this functionality again in the future.
#
#aaa_dll = dll_ + 'aaa' + _dll
#moc = 'moc_aaa.cc'
#
#createSConstruct(test, ['work8', 'SConstruct'])
#
#test.write(['work8', 'SConscript'], """
#Import("env")
#env = env.Copy(QT_AUTOBUILD_MOC_SOURCES = 0)
#env.SharedLibrary(target = 'aaa', source = ['aaa.ui', 'useit.cpp', 'aaa_function.cpp'])
#""")
#
#test.write(['work8', 'aaa.ui'], r"""
##if defined (_WIN32) || defined(__CYGWIN__)
##define DLLEXPORT __declspec(dllexport)
##else
##define DLLEXPORT
##endif
#DLLEXPORT void aaa(void)
#""")
#
#test.write(['work8', 'useit.cpp'], r"""
##include "aaa.h"
#void useit() {
#  aaa();
#}
#""")
#
#test.write(['work8', 'aaa_function.cpp'], r"""
##include "my_qobject.h"
##if defined (_WIN32) || defined(__CYGWIN__)
##define DLLEXPORT __declspec(dllexport)
##else
##define DLLEXPORT
##endif
#DLLEXPORT void aaa(void)
# { my_qt_symbol( "aaa_function.cpp\n" ); }
#""")
#
#test.run(chdir='work8', arguments = aaa_dll)
#
#test.must_not_exist(test.workpath('work8', moc))
#
#test.write(['work8', 'SConscript'], """
#Import("env")
#env = env.Copy(QT_AUTOBUILD_MOC_SOURCES = 1)
#env.SharedLibrary(target = 'aaa', source = ['aaa.ui', 'useit.cpp'])
#""")
#
#test.run(chdir='work8', arguments = aaa_dll)
#
#test.must_exist(test.workpath('work8', moc))

##############################################################################
# 9. test that an overwritten CPPPATH is working with generated files

# this is basically test 1, but with an additional include
aaa_exe = 'aaa' + _exe

createSConstruct(test, ['work9', 'SConstruct'])
test.write( ['work9', 'SConscript'], """
Import("env")
env.Program(target = 'aaa', source = 'aaa.cpp', CPPPATH=['$CPPPATH', './local_include'])
""")

test.write(['work9', 'aaa.cpp'], r"""
#include "aaa.h"
int main() { aaa(); return 0; }
""")

test.write(['work9', 'aaa.h'], r"""
#include "my_qobject.h"
#include "local_include.h"
void aaa(void) Q_OBJECT;
""")

test.write(['work9', 'local_include', 'local_include.h'], r"""
/* empty; just needs to be found */
""")

test.run(chdir='work9', arguments = aaa_exe)

##############################################################################
# 10. test that an appended relative CPPPATH is working with generated files

# this is basically test 9, but the include path is env.Append-ed and
# everything goes into sub directory "sub"
aaa_exe = os.path.join('sub', 'aaa' + _exe)

createSConstruct(test, ['work10', 'SConstruct'])
test.write( ['work10', 'SConscript'], r"""
SConscript('sub/SConscript')
""")

test.write( ['work10', 'sub', 'SConscript'], r"""
Import("env")
env.Append(CPPPATH=['./local_include'])
env.Program(target = 'aaa', source = 'aaa.cpp')
""")

test.write(['work10', 'sub', 'aaa.cpp'], r"""
#include "aaa.h"
int main() { aaa(); return 0; }
""")

test.write(['work10', 'sub', 'aaa.h'], r"""
#include "my_qobject.h"
#include "local_include.h"
void aaa(void) Q_OBJECT;
""")

test.write(['work10', 'sub', 'local_include', 'local_include.h'], r"""
/* empty; just needs to be found */
""")

test.run(chdir='work10', arguments = aaa_exe)

###############################################################################
# 11. test the manual QT builder calls

aaa_exe = 'aaa' + _exe

createSConstruct(test, ['work11', 'SConstruct'])
test.write( ['work11', 'SConscript'], r"""
Import("env")
sources = ['aaa.cpp', 'bbb.cpp', 'ddd.cpp', 'eee.cpp', 'main.cpp']

# normal invocation
sources.append(env.Moc('include/aaa.h'))
env.Moc('bbb.cpp')
sources.extend(env.Uic('ui/ccc.ui')[1:])

# manual target specification
sources.append(env.Moc('moc-ddd.cpp', 'include/ddd.h',
               QT_MOCHPREFIX='')) # Watch out !
env.Moc('moc_eee.cpp', 'eee.cpp')
sources.extend(env.Uic(['include/uic_fff.hpp', 'fff.cpp', 'fff.moc.cpp'],
                       'ui/fff.ui')[1:])

print map(str,sources)
env.Program(target='aaa',
            source=sources,
            CPPPATH=['$CPPPATH', './include'],
            QT_AUTOSCAN=0)
""")

test.write(['work11', 'aaa.cpp'], r"""
#include "aaa.h"
""")
                     
test.write(['work11', 'include', 'aaa.h'], r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT;
""")

test.write(['work11', 'bbb.h'], r"""
void bbb(void);
""")

test.write(['work11', 'bbb.cpp'], r"""
#include "my_qobject.h"
void bbb(void) Q_OBJECT
#include "bbb.moc"
""")

test.write(['work11', 'ui', 'ccc.ui'], r"""
void ccc(void)
""")

test.write(['work11', 'ddd.cpp'], r"""
#include "ddd.h"
""")
                     
test.write(['work11', 'include', 'ddd.h'], r"""
#include "my_qobject.h"
void ddd(void) Q_OBJECT;
""")

test.write(['work11', 'eee.h'], r"""
void eee(void);
""")

test.write(['work11', 'eee.cpp'], r"""
#include "my_qobject.h"
void eee(void) Q_OBJECT
#include "moc_eee.cpp"
""")

test.write(['work11', 'ui', 'fff.ui'], r"""
void fff(void)
""")

test.write(['work11', 'main.cpp'], r"""
#include "aaa.h"
#include "bbb.h"
#include "ui/ccc.h"
#include "ddd.h"
#include "eee.h"
#include "uic_fff.hpp"

int main() {
  aaa(); bbb(); ccc(); ddd(); eee(); fff(); return 0;
}
""")

test.run(chdir='work11', arguments = aaa_exe)

# normal invocation
test.must_exist(test.workpath('work11', 'include', 'moc_aaa.cc'))
test.must_exist(test.workpath('work11', 'bbb.moc'))
test.must_exist(test.workpath('work11', 'ui', 'ccc.h'))
test.must_exist(test.workpath('work11', 'ui', 'uic_ccc.cc'))
test.must_exist(test.workpath('work11', 'ui', 'moc_ccc.cc'))

# manual target spec.
test.must_exist(test.workpath('work11', 'moc-ddd.cpp'))
test.must_exist(test.workpath('work11', 'moc_eee.cpp'))
test.must_exist(test.workpath('work11', 'include', 'uic_fff.hpp'))
test.must_exist(test.workpath('work11', 'fff.cpp'))
test.must_exist(test.workpath('work11', 'fff.moc.cpp'))


##############################################################################
# 12. test the tool warings
createSConstruct(test, ['work12', 'SConstruct'])

test.write(['work12', 'aaa.cpp'], r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT
""")

test.write(['work12', 'SConscript'], r"""
Import("env")
import os
env.StaticLibrary('aaa.cpp')
""")

test.run(chdir='work12', stderr=None)
test.fail_test(not test.match_re(test.stderr(), r"""
scons: warning: Generated moc file 'aaa.moc' is not included by 'aaa.cpp'
File .+
"""))

os.environ['QTDIR'] = QT
test.run(chdir='work12', arguments='-n noqtdir=1')

# We'd like to eliminate $QTDIR from the environment as follows:
#       del os.environ['QTDIR']
# But unfortunately, in at least some versions of Python, the Environment
# class doesn't implement a __delitem__() method to make the library
# call to actually remove the deleted variable from the *external*
# environment, so it only gets removed from the Python dictionary.
# Consequently, we need to just wipe out its value as follows>
os.environ['QTDIR'] = ''
test.run(chdir='work12', stderr=None, arguments='-n noqtdir=1')
test.fail_test(not test.match_re(test.stderr(), r"""
scons: warning: Could not detect qt, using empty QTDIR
File "SConstruct", line \d+, in .+
"""))

test.pass_test()
