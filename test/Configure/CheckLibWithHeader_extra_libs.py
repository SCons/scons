"""
Verify that a program which depends on library which in turns depend on another library
can be built correctly using CheckLibWithHeader
"""

from pathlib import Path

from TestSCons import TestSCons

test = TestSCons(match=TestSCons.match_re_dotall)


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
SharedLibrary('libA', source=['libA.c'])
""",
)
test.run(chdir=libA_dir)


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
SharedLibrary(
    'libB', 
    source=['libB.c'], 
    LIBS=['A'], 
    LIBPATH='../libA',
    CPPPATH='../libA',
)
""",
)
test.run(chdir=libB_dir)

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
