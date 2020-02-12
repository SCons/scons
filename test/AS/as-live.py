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
Verify correct use of the live 'as' assembler.
"""

import sys

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



if not test.detect('AS', 'as'):
    test.skip_test("as not found; skipping test\n")

x86 = (sys.platform == 'win32' or sys.platform.find('linux') != -1)

if not x86:
    test.skip_test("skipping as test on non-x86 platform '%s'\n" % sys.platform)

namelbl = "name"
testccc = """ccc = aaa.Clone(CPPPATH=['.'])
ccc.Program(target = 'ccc', source = ['ccc.S', 'ccc_main.c'])
"""
if sys.platform == "win32":
    namelbl = "_name"
    testccc = ""
    
test.write("wrapper.py", """\
import subprocess
import sys
with open('%s', 'wb') as f:
    f.write(("wrapper.py: %%s\\n" %% sys.argv[-1]).encode())
cmd = " ".join(sys.argv[1:])
subprocess.run(cmd, shell=True)
""" % test.workpath('wrapper.out').replace('\\', '\\\\'))

test.write('SConstruct', """\
aaa = Environment()
aaa.Program(target = 'aaa', source = ['aaa.s', 'aaa_main.c'])
bbb = aaa.Clone(AS = r'%(_python_)s wrapper.py ' + WhereIs('as'))
bbb.Program(target = 'bbb', source = ['bbb.s', 'bbb_main.c'])
%(testccc)s
""" % locals())

test.write('aaa.s', 
"""        .file   "aaa.s"
.data
.align 4
.globl %(namelbl)s
%(namelbl)s:
        .ascii	"aaa.s"
        .byte	0
""" % locals())

test.write('bbb.s', """\
.file   "bbb.s"
.data
.align 4
.globl %(namelbl)s
%(namelbl)s:
        .ascii	"bbb.s"
        .byte	0
""" % locals())

test.write('ccc.h', """\
#define STRING  "ccc.S"
""")

test.write('ccc.S', """\
#include <ccc.h>
.file   STRING
.data
.align 4
.globl name
name:
        .ascii	STRING
        .byte	0
""")

test.write('aaa_main.c', r"""
#include <stdlib.h>
#include <stdio.h>

extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("aaa_main.c %s\n", name);
        exit (0);
}
""")

test.write('bbb_main.c', r"""
#include <stdlib.h>
#include <stdio.h>

extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("bbb_main.c %s\n", name);
        exit (0);
}
""")

test.write('ccc_main.c', r"""
#include <stdlib.h>
#include <stdio.h>

extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("ccc_main.c %s\n", name);
        exit (0);
}
""")

test.write('ddd_main.c', r"""
extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("ddd_main.c %s\n", name);
        exit (0);
}
""")

test.run()

test.run(program = test.workpath('aaa'), stdout =  "aaa_main.c aaa.s\n")
test.run(program = test.workpath('bbb'), stdout =  "bbb_main.c bbb.s\n")

if sys.platform != "win32":
    test.run(program = test.workpath('ccc'), stdout =  "ccc_main.c ccc.S\n")
    
    test.must_match('wrapper.out', "wrapper.py: bbb.s\n")
    
    test.write("ccc.h", """\
    #define STRING  "ccc.S 2"
    """)
    
    test.run()
    test.run(program = test.workpath('ccc'), stdout =  "ccc_main.c ccc.S 2\n")

test.unlink('wrapper.out')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
