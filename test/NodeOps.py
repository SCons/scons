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

# This test is used to verify that the Buildability of a set of nodes
# is unaffected by various querying operations on those nodes:
#
# 1) Calling exists() on a Node (e.g. from find_file) in a BuildDir
#    will cause that node to be duplicated into the builddir.
#    However, this should *not* occur during a dryrun (-n).  When not
#    performed during a dryrun, this should not affect buildability.
# 2) Calling is_derived() should not affect buildability.
# 3) Calling is_pseudo_derived() may cause the sbuilder to be set, and
#    it may caues the builder to be set as well, but it should not
#    adversely affect buildability.

import sys
import TestSCons
import os
import string

_exe = TestSCons._exe
lib_ = TestSCons.lib_
_lib = TestSCons._lib
_obj = TestSCons._obj
dll_ = TestSCons.dll_
_dll = TestSCons._dll

if sys.platform == 'win32':
    fooflags = '/nologo -DFOO'
    barflags = '/nologo -DBAR'
else:
    fooflags = '-DFOO'
    barflags = '-DBAR'
    
if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if string.find(sys.platform, 'irix') > -1:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

test = TestSCons.TestSCons()

test.subdir('bld', 'src', ['src', 'subsrcdir'])

sconstruct = r"""
foo = Environment(SHCXXFLAGS = '%(fooflags)s', WIN32_INSERT_DEF=1)
bar = Environment(SHCXXFLAGS = '%(barflags)s', WIN32_INSERT_DEF=1)
src = Dir('src')
BuildDir('bld', src, duplicate=1)
Nodes=[]
Nodes.extend(foo.SharedObject(target = 'foo%(_obj)s', source = 'prog.cpp'))
Nodes.extend(bar.SharedObject(target = 'bar%(_obj)s', source = 'prog.cpp'))
SConscript('bld/SConscript', ['Nodes'])
if %(_E)s:
  import os
  derived = map(lambda N: N.is_derived(), Nodes)
  p_derived = map(lambda N: N.is_pseudo_derived(), Nodes)
  real1 = map(lambda N: os.path.exists(str(N)), Nodes)
  exists = map(lambda N: N.exists(), Nodes)
  real2 = map(lambda N: os.path.exists(str(N)), Nodes)
  for N,D,P,R,E,F in map(None, Nodes, derived, p_derived,
                               real1, exists, real2):
    print '%%s: %%s %%s %%s %%s %%s'%%(N,D,P,R,E,F)
foo.SharedLibrary(target = 'foo', source = 'foo%(_obj)s')
bar.SharedLibrary(target = 'bar', source = 'bar%(_obj)s')

fooMain = foo.Copy(LIBS='foo', LIBPATH='.')
foo_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foo_obj)

barMain = bar.Copy(LIBS='bar', LIBPATH='.')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=bar_obj)

gooMain = foo.Copy(LIBS='goo', LIBPATH='bld')
goo_obj = gooMain.Object(target='goomain', source='main.c')
gooMain.Program(target='gooprog', source=goo_obj)
"""
           

test.write('foo.def', r"""
LIBRARY        "foo"
DESCRIPTION    "Foo Shared Library"

EXPORTS
   doIt
""")

test.write('bar.def', r"""
LIBRARY        "bar"
DESCRIPTION    "Bar Shared Library"

EXPORTS
   doIt
""")

test.write('prog.cpp', r"""
#include <stdio.h>

extern "C" void
doIt()
{
#ifdef FOO
	printf("prog.cpp:  FOO\n");
#endif
#ifdef BAR
	printf("prog.cpp:  BAR\n");
#endif
}
""")

sconscript = r"""
import os
Import('*')

import __builtin__
try:
    __builtin__.True
except AttributeError:
    __builtin__.True = 1
    __builtin__.False = 0

def mycopy(env, source, target):
    open(str(target[0]),'w').write(open(str(source[0]),'r').read())

def exists_test(node):
    before = os.path.exists(str(node))  # doesn't exist yet in BuildDir
    via_node = node.exists()            # side effect causes copy from src
    after = os.path.exists(str(node))
    node.is_derived()
    node.is_pseudo_derived()
    import SCons.Script
    if SCons.Script.options.noexec:
        if (before,via_node,after) != (False,False,False):
            import sys
            sys.stderr.write('BuildDir exits() populated during dryrun!\n')
            sys.exit(-2)
    else:
        if (before,via_node,after) != (False,True,True):
            import sys
            sys.stderr.write('BuildDir exists() population did not occur! (%%s:%%s,%%s,%%s)\n'%%(str(node),before,via_node,after))
            sys.exit(-2)
    
goo = Environment(CPPFLAGS = '%(fooflags)s')
goof_in = File('goof.in')
if %(_E)s:
    exists_test(goof_in)
Nodes.append(goof_in)
Nodes.extend(goo.Command(target='goof.c', source='goof.in', action=mycopy))
boo_src = File('subsrcdir/boo.c')
if %(_E)s:
    exists_test(boo_src)
boo_objs = goo.Object(target='subsrcdir/boo%(_obj)s', source = boo_src)
Nodes.extend(boo_objs)
Nodes.extend(goo.Object(target='goo%(_obj)s',source='goof.c'))
goo.Library(target = 'goo', source = ['goo%(_obj)s'] + boo_objs)
"""

test.write(['src', 'goof.in'], r"""
#include <stdio.h>

extern char *boo_sub();

void
doIt()
{
#ifdef FOO
	printf("prog.cpp:  %s\n", boo_sub());
#endif
}
""")

test.write(['src', 'subsrcdir', 'boo.c'], r"""
char *
boo_sub()
{
    return "GOO";
}
""")

test.write('main.c', r"""

void doIt();

int
main(int argc, char* argv[])
{
    doIt();
    return 0;
}
""")

builddir_srcnodes = [ os.path.join('bld', 'goof.in'),
                      os.path.join('bld', 'subsrcdir', 'boo.c'),
                    ]

sub_build_nodes = [ os.path.join('bld', 'subsrcdir','boo' + _obj),
                    os.path.join('bld', 'goo' + _obj),
                    os.path.join('bld', 'goof.c'),
                    os.path.join('bld', lib_ + 'goo' + _lib),
]

build_nodes = ['fooprog' + _exe,
               dll_ + 'foo' + _dll,
	       'foo' + _obj,
               'barprog' + _exe,
	       dll_ + 'bar' + _dll,
	       'bar' + _obj,

               'gooprog' + _exe,

               ] + builddir_srcnodes + sub_build_nodes

def cleanup_test():
    "cleanup after running a test"
    for F in builddir_srcnodes:
        test.unlink(F)  # will be repopulated during clean operation
    test.run(arguments = '-c')
    for F in builddir_srcnodes:
        test.unlink(F)
    for name in build_nodes:
        test.must_not_exist(test.workpath(name))


### First pass, make sure everything goes quietly

for name in build_nodes:
    test.must_not_exist(test.workpath(name))

_E=0
test.write('SConstruct', sconstruct % locals() )
test.write(['src', 'SConscript'], sconscript % locals() )

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = test.workpath('fooprog'), stdout = "prog.cpp:  FOO\n")
test.run(program = test.workpath('barprog'), stdout = "prog.cpp:  BAR\n")
test.run(program = test.workpath('gooprog'), stdout = "prog.cpp:  GOO\n")

for name in build_nodes:
    test.must_exist(test.workpath(name))

cleanup_test()

### Next pass: add internal Node ops that may have side effects to
### ensure that those side-effects don't interfere with building

for name in build_nodes:
    test.must_not_exist(test.workpath(name))

_E=1
test.write('SConstruct', sconstruct % locals() )
test.write(['src', 'SConscript'], sconscript % locals() )

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = test.workpath('fooprog'), stdout = "prog.cpp:  FOO\n")
test.run(program = test.workpath('barprog'), stdout = "prog.cpp:  BAR\n")
test.run(program = test.workpath('gooprog'), stdout = "prog.cpp:  GOO\n")

for name in build_nodes:
    test.must_exist(test.workpath(name))

cleanup_test()

### Next pass: try a dry-run first and verify that it doesn't change
### the buildability.

for name in build_nodes:
    test.must_not_exist(test.workpath(name))

_E=1
test.write('SConstruct', sconstruct % locals() )
test.write(['src', 'SConscript'], sconscript % locals() )

test.run(arguments = '-n .',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

for name in build_nodes:
    test.must_not_exist(test.workpath(name))

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

test.run(program = test.workpath('fooprog'), stdout = "prog.cpp:  FOO\n")
test.run(program = test.workpath('barprog'), stdout = "prog.cpp:  BAR\n")
test.run(program = test.workpath('gooprog'), stdout = "prog.cpp:  GOO\n")

for name in build_nodes:
    test.must_exist(test.workpath(name))

cleanup_test()

### Next pass: do an up-build from a BuildDir src


for name in build_nodes:
    test.must_not_exist(test.workpath(name))

_E=0
test.write('SConstruct', sconstruct % locals() )
test.write(['src', 'SConscript'], sconscript % locals() )

test.run(chdir='src', arguments = '-u',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

for name in build_nodes:
    if name in sub_build_nodes or name in builddir_srcnodes:
        test.must_exist(test.workpath(name))
    else:
        test.must_not_exist(test.workpath(name))

cleanup_test()

### Next pass: do an up-build from a BuildDir src with Node Ops
### side-effects

for name in build_nodes:
    test.must_not_exist(test.workpath(name))

_E=1
test.write('SConstruct', sconstruct % locals() )
test.write(['src', 'SConscript'], sconscript % locals() )

test.run(chdir='src', arguments = '-u',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

for name in build_nodes:
    if name in sub_build_nodes or name in builddir_srcnodes:
        test.must_exist(test.workpath(name))
    else:
        test.must_not_exist(test.workpath(name))

cleanup_test()

test.pass_test()
