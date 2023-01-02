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
This test is used to verify that the Buildability of a set of nodes
is unaffected by various querying operations on those nodes:

1) Calling exists() on a Node (e.g. from find_file) in a VariantDir
   will cause that node to be duplicated into the builddir.
   However, this should *not* occur during a dryrun (-n).  When not
   performed during a dryrun, this should not affect buildability.
2) Calling is_derived() should not affect buildability.
"""

import sys
import os

import TestSCons
from TestSCons import _exe, lib_, _lib, _obj, dll_, _dll

if os.name == 'posix':
    os.environ['LD_LIBRARY_PATH'] = '.'
if sys.platform.find('irix') > -1:
    os.environ['LD_LIBRARYN32_PATH'] = '.'

test = TestSCons.TestSCons()

test.subdir('bld', 'src', ['src', 'subsrcdir'])

sconstruct = r"""
DefaultEnvironment(tools=[])  # test speedup
foo = Environment(SHOBJPREFIX='', WINDOWS_INSERT_DEF=1)
foo.Append(SHCXXFLAGS = '-DFOO')
bar = Environment(SHOBJPREFIX='', WINDOWS_INSERT_DEF=1)
bar.Append(SHCXXFLAGS = '-DBAR')
src = Dir('src')
VariantDir('bld', src, duplicate=1)
Nodes=[]
Nodes.extend(foo.SharedObject(target = 'foo%(_obj)s', source = 'prog.cpp'))
Nodes.extend(bar.SharedObject(target = 'bar%(_obj)s', source = 'prog.cpp'))
SConscript('bld/SConscript', ['Nodes'])
if %(_E)s:
  import os
  derived = [N.is_derived() for N in Nodes]
  real1 = [os.path.exists(str(N)) for N in Nodes]
  exists = [N.exists() for N in Nodes]
  real2 = [os.path.exists(str(N)) for N in Nodes]
  for N,D,R,E,F in zip(Nodes, derived, real1, exists, real2):
    print('%%s: %%s %%s %%s %%s'%%(N,D,R,E,F))
foo.SharedLibrary(target = 'foo', source = 'foo%(_obj)s')
bar.SharedLibrary(target = 'bar', source = 'bar%(_obj)s')

fooMain = foo.Clone(LIBS='foo', LIBPATH='.')
foo_obj = fooMain.Object(target='foomain', source='main.c')
fooMain.Program(target='fooprog', source=foo_obj)

barMain = bar.Clone(LIBS='bar', LIBPATH='.')
bar_obj = barMain.Object(target='barmain', source='main.c')
barMain.Program(target='barprog', source=bar_obj)

gooMain = foo.Clone(LIBS='goo', LIBPATH='bld')
goo_obj = gooMain.Object(target='goomain', source='main.c')
gooMain.Program(target='gooprog', source=goo_obj)
"""

test.write('foo.def', r"""
LIBRARY        "foo"

EXPORTS
   doIt
""")

test.write('bar.def', r"""
LIBRARY        "bar"

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

def mycopy(env, source, target):
    with open(str(target[0]), 'wt') as fo, open(str(source[0]), 'rt') as fi:
        fo.write(fi.read())

def exists_test(node):
    before = os.path.exists(str(node))  # doesn't exist yet in VariantDir
    via_node = node.exists()            # side effect causes copy from src
    after = os.path.exists(str(node))
    node.is_derived()
    import SCons.Script
    if GetOption('no_exec'):
        if (before,via_node,after) != (False,False,False):
            import sys
            sys.stderr.write('VariantDir exists() populated during dryrun!\n')
            sys.exit(-2)
    else:
        if (before,via_node,after) != (False,True,True):
            import sys
            sys.stderr.write('VariantDir exists() population did not occur! (%%s:%%s,%%s,%%s)\n'%%(str(node),before,via_node,after))
            sys.exit(-2)

goo = Environment()
goo.Append(CFLAGS = '-DFOO')
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
    """cleanup after running a test"""
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

### Next pass: do an up-build from a VariantDir src


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

### Next pass: do an up-build from a VariantDir src with Node Ops
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

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
