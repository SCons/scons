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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Verify that a program which depends on library which in turn depends
on another library can be built correctly using CheckLibWithHeader
"""

from pathlib import Path

from TestSCons import TestSCons, dll_, _dll

test = TestSCons(match=TestSCons.match_re_dotall)

# This is the first library project
libA_dir = Path(test.workdir) / "libA"
libA_dir.mkdir()
libA = str(libA_dir / (dll_ + 'A' + _dll))  # for existence check

test.write(
    str(libA_dir / "libA.h"),
    """\
#ifndef _LIBA_H
#define _LIBA_H

// define BUILDINGSHAREDLIB when building libA as shared lib
#ifdef _MSC_VER
# ifdef BUILDINGSHAREDLIB
#  define LIBA_DECL __declspec(dllexport)
# else
#  define LIBA_DECL __declspec(dllimport)
# endif
#endif // WIN32

#ifndef LIBA_DECL
# define LIBA_DECL
#endif

LIBA_DECL void libA(void);
#endif // _LIBA_H
""",
)
test.write(
    str(libA_dir / "libA.c"),
    """\
#include <stdio.h>
#include "libA.h"

LIBA_DECL void libA(void) {
    printf("libA\\n");
}
""",
)
test.write(
    str(libA_dir / "SConstruct"),
    """\
SharedLibrary(target='A', source=['libA.c'], CPPDEFINES='BUILDINGSHAREDLIB')
""",
)

# This is the second library project, depending on the first
libB_dir = Path(test.workdir) / "libB"
libB_dir.mkdir()
libB = str(libB_dir / (dll_ + 'B' + _dll))  # for existence check
test.write(
    str(libB_dir / "libB.h"),
    """\
#ifndef _LIBB_H
#define _LIBB_H

// define BUILDINGSHAREDLIB when building libB as shared lib
#ifdef _MSC_VER
# ifdef BUILDINGSHAREDLIB
#  define LIBB_DECL __declspec(dllexport)
# else
#  define LIBB_DECL __declspec(dllimport)
# endif
#endif // WIN32

#ifndef LIBB_DECL
# define LIBB_DECL
#endif

LIBB_DECL void libB(void);
#endif // _LIBB_H
""",
)
test.write(
    str(libB_dir / "libB.c"),
    """\
#include <stdio.h>
#include "libA.h"
#include "libB.h"

LIBB_DECL void libB (void) {
    printf("libB\\n");
    libA();
}
""",
)
test.write(
    str(libB_dir / "SConstruct"),
    """\
SharedLibrary(
    target='B',
    source=['libB.c'],
    LIBS=['A'],
    LIBPATH='../libA',
    CPPPATH='../libA',
    CPPDEFINES='BUILDINGSHAREDLIB',
)
""",
)

test.run(arguments='-C libA')
test.must_exist(libA)
test.run(arguments='-C libB')
test.must_exist(libB)

# With the two projects built, we can now run the Configure check
test.write(
    "SConstruct",
    """\
env = Environment(
    CPPPATH=['#'],
    LIBPATH=['libB', 'libA'],
    LIBS=['A', 'B'],
    RPATH=['libA', 'libB'],
)

conf = Configure(env)
if not conf.CheckLibWithHeader(
    ['B'],
    header="libB/libB.h",
    language='C',
    extra_libs=['A'],
    call='libB();',
    autoadd=False,
):
    print("Cannot build against 'B' library, exiting.")
    Exit(1)
env = conf.Finish()

# TODO: we should be able to build and run a test program now,
#   to make sure Configure() didn't lie to us about usability.
#   Disabled for now, because that's trickier in Windows (no rpath)
# env.Program(target="testlibs", source="src/test.c")
""",
)
test.run()
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
