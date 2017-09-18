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
Test that we can build shared libraries and link against shared
libraries that have non-standard library prefixes and suffixes.
"""

import re
import sys
import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
import sys
isCygwin = sys.platform == 'cygwin'
isWindows = sys.platform == 'win32'
isMingw = False
if isWindows:
    import SCons.Tool.MSCommon as msc
    if not msc.msvc_exists():
        # We can't seem to find any MSVC version, so we assume
        # that MinGW is installed instead. Accordingly, we use the
        # standard gcc/g++ conventions for lib prefixes and suffixes
        # in the following...
        isWindows = False
        isMingw = True

env = Environment()

# Make sure that the shared library can be located at runtime.
env.Append(RPATH=['.'])
env.Append(LIBPATH=['.'])

# We first bake the LIBSUFFIXES, so that it will not change as a
# side-effect of changing SHLIBSUFFIX.
env['LIBSUFFIXES'] = list(map( env.subst, env.get('LIBSUFFIXES', [])))

weird_prefixes = ['libXX', 'libYY']

if isWindows:
    weird_suffixes = ['.xxx', '.yyy', '.xxx.dll', '.yyy.dll']
    env.Append(CCFLAGS = '/MD')
elif env['PLATFORM'] == 'darwin':
    weird_suffixes = ['.xxx.dylib', '.yyy.dylib']
else:
    weird_suffixes = ['.xxx.so', '.yyy.so']

shlibprefix = env.subst('$SHLIBPREFIX')
shlibsuffix = env.subst('$SHLIBSUFFIX')

progprefix = env.subst('$PROGPREFIX')
progsuffix = env.subst('$PROGSUFFIX')

goo_obj = env.SharedObject(source='goo.c')
foo_obj = env.SharedObject(source='foo.c')
prog_obj = env.SharedObject(source='prog.c')

#
# The following functions define all the different ways that one can
# use to link against a shared library.
#
def nodeInSrc(source, lib, libname):
    return (source+lib, '')

def pathInSrc(source, lib, libname):
    return (source+list(map(str,lib)), '')

def nodeInLib(source, lib, libname):
    return (source, lib)

def pathInLib(source, lib, libname):
    return (source, list(map(str,lib)))

def nameInLib(source, lib, libname):
    # NOTE: libname must contain both the proper prefix and suffix.
    #
    # When using non-standard prefixes and suffixes, one has to
    # provide the full name of the library since scons can not know
    # which of the non-standard extension to use.
    #
    # Note that this is not necessarily SHLIBPREFIX and
    # SHLIBSUFFIX. These are the ixes of the target library, not the
    # ixes of the library that we are linking against.
    return (source, libname)

libmethods = [nodeInSrc, pathInSrc, nodeInLib, pathInLib]
# We skip the nameInLib test for MinGW and Cygwin...they would fail, due to
# the Tool's internal naming conventions
if not isMingw and not isCygwin:
    libmethods.extend([nameInLib])

def buildAndlinkAgainst(builder, target, source,  method, lib, libname, **kw):
    '''Build a target using a given builder while linking against a given
    library using a specified method for linking against the library.'''

    # On Windows, we have to link against the .lib file.
    if isWindows:
        for l in lib:
            if str(l)[-4:] == '.lib':
                lib = [l]
                break
    # If we use MinGW or Cygwin and create a SharedLibrary, we get two targets: a DLL,
    # and the import lib created by the "--out-implib" parameter. We always
    # want to link against the second one, in order to prevent naming issues
    # for the linker command line...
    if (isMingw or isCygwin) and len(lib) > 1:
        lib = lib[1:]

    # Apply the naming method to be tested and call the specified Builder.
    (source, LIBS) = method(source, lib, libname)
    #build = builder(target=target, source=source, LIBS=LIBS, **kw)
    kw = kw.copy()
    kw['target'] = target
    kw['source'] = source
    kw['LIBS'] = LIBS
    build = builder(**kw)

    # Check that the build target depends on at least one of the
    # library target.
    found_dep = False
    children = build[0].children()
    for l in lib:
        if l in children:
            found_dep = True
            break;
    assert found_dep, \
        "One of %s not found in %s, method=%s, libname=%s, shlibsuffix=%s" % \
        (list(map(str,lib)), list(map(str, build[0].children())), method.__name__, libname, shlibsuffix)
    return build

def prog(i,
         goomethod, goolibprefix, goolibsuffix,
         foomethod, foolibprefix, foolibsuffix):
    '''Build a program

     The program links against a shared library foo which itself links
     against a shared library goo. The libraries foo and goo can use
     arbitrary library prefixes and suffixes.'''

    goo_name =  goolibprefix+'goo'+str(i)+goolibsuffix
    foo_name =  foolibprefix+'foo'+str(i)+foolibsuffix
    prog_name = progprefix+'prog'+str(i)+progsuffix

    print('Prog: %d, %s, %s, %s' % (i, goo_name, foo_name, prog_name))

    # On Windows, we have to link against the .lib file.
    if isWindows:
        goo_libname =  goolibprefix+'goo'+str(i)+'.lib'
        foo_libname =  foolibprefix+'foo'+str(i)+'.lib'
    else:
        goo_libname =  goo_name
        foo_libname =  foo_name

    goo_lib = env.SharedLibrary(
        goo_name, goo_obj, SHLIBSUFFIX=goolibsuffix)
    foo_lib = buildAndlinkAgainst(
        env.SharedLibrary, foo_name, foo_obj,
        goomethod, goo_lib, goo_libname, SHLIBSUFFIX=foolibsuffix)
    prog = buildAndlinkAgainst(env.Program, prog_name, prog_obj,
        foomethod, foo_lib, foo_libname)


#
# Create the list of all possible permutations to test.
#
i = 0
tests = []
prefixes = [shlibprefix] +  weird_prefixes
suffixes = [shlibsuffix] +  weird_suffixes
for foolibprefix in prefixes:
    for foolibsuffix in suffixes:
        for foomethod in libmethods:
            for goolibprefix in prefixes:
                for goolibsuffix in suffixes:
                    for goomethod in libmethods:
                        tests.append(
                            (i,
                             goomethod, goolibprefix, goolibsuffix,
                             foomethod, foolibprefix, foolibsuffix))
                        i = i + 1

#
# Pseudo-randomly choose 200 tests to run out of the possible
# tests. (Testing every possible permutation would take too long.)
#
import random
random.seed(123456)
try:
    random.shuffle(tests)
except AttributeError:
    pass

for i in range(200):
  prog(*tests[i])

""")

test.write('goo.c', r"""
#include <stdio.h>

#ifdef _WIN32
#define EXPORT __declspec( dllexport )
#else
#define EXPORT
#endif

EXPORT void
goo(void)
{
        printf("goo.c\n");
}
""")

test.write('foo.c', r"""
#include <stdio.h>

void goo(void);

#ifdef _WIN32
#define EXPORT __declspec( dllexport )
#else
#define EXPORT
#endif

EXPORT void
foo(void)
{
        goo();
        printf("foo.c\n");
}
""")

test.write('prog.c', r"""
#include <stdio.h>

void foo(void);

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        foo();
        printf("prog.c\n");
        return 0;
}
""")

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

tests = re.findall(r'Prog: (\d+), (\S+), (\S+), (\S+)', test.stdout())
expected = "goo.c\nfoo.c\nprog.c\n"

for t in tests:
    if sys.platform != 'cygwin':
        test.must_exist(t[1])
        test.must_exist(t[2])
    else:
        # Cygwin turns libFoo.xxx into cygFoo.xxx
        for f in t[1:2]:
            test.must_exist(re.sub('^lib', 'cyg', f))

    test.must_exist(t[3])
    test.run(program = test.workpath(t[3]), stdout=expected)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
