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

from TestSCons import TestSCons

test = TestSCons(match=TestSCons.match_re_dotall)

# This is the first library project
libA_dir = Path(test.workdir) / "libA"
libA_dir.mkdir()
test.write(
    str(libA_dir / "libA.h"),
    """\
void libA();
""",
)
test.write(
    str(libA_dir / "libA.c"),
    """\
#include <stdio.h>
#include "libA.h"

void libA() {
    printf("libA\\n");
}
""",
)
test.write(
    str(libA_dir / "SConstruct"),
    """\
DefaultEnvironment(tools=[])
SharedLibrary('A', source=['libA.c'])
""",
)
test.run(arguments='-C libA')

# This is the second library project, depending on the first
libB_dir = Path(test.workdir) / "libB"
libB_dir.mkdir()
test.write(
    str(libB_dir / "libB.h"),
    """\
void libB();
""",
)
test.write(
    str(libB_dir / "libB.c"),
    """\
#include <stdio.h>
#include "libA.h"
#include "libB.h"

void libB () {
    libA();
}
""",
)
test.write(
    str(libB_dir / "SConstruct"),
    """\
DefaultEnvironment(tools=[])
SharedLibrary(
    'B',
    source=['libB.c'],
    LIBS=['A'],
    LIBPATH='../libA',
    CPPPATH='../libA',
)
""",
)
test.run(arguments='-C libB')

# With the two projects built, we can now run the Configure check
test.write(
    "SConstruct",
    """\
import os

env = Environment(ENV=os.environ, CPPPATH=['libB', 'libA'], LIBPATH=['libB', 'libA'])
conf = Configure(env)

ret = conf.CheckLibWithHeader(
    ['B'],
    header="libB.h",
    language='C',
    extra_libs=['A'],
    call='libB();',
    autoadd=False,
)
assert ret
""",
)
test.run()
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
