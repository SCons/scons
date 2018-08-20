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
Verify correct use of the live 'nasm' assembler.
"""

import os
import sys

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

nasm = test.where_is('nasm')

if not nasm:
    test.skip_test('nasm not found; skipping test\n')

if sys.platform.find('linux') == -1:
    test.skip_test("skipping test on non-Linux platform '%s'\n" % sys.platform)

try:
    import subprocess
    stdout = subprocess.check_output(['nasm','-v'])
except OSError:
    test.skip_test('could not determine nasm version; skipping test\n')
else:
    stdout = stdout.decode()
    version = stdout.split()[2].split('.')
    if int(version[0]) ==0 and int(version[1]) < 98:
        test.skip_test("skipping test of nasm version %s\n" % version)

    machine = os.uname()[4]
    if not machine in ('i386', 'i486', 'i586', 'i686', 'x86_64'):
        fmt = "skipping test of nasm %s on non-x86 machine '%s'\n"
        test.skip_test(fmt % (version, machine))

# Allow flexibility about the type of object/executable format
# needed on different systems.  Format_map is a dict that maps
# sys.platform substrings to the correct argument for the nasm -f
# option.  The default is "elf," which seems to be a reasonable
# lowest common denominator (works on both Linux and FreeBSD,
# anyway...).
nasm_format = 'elf'
format_map = {}
for k, v in format_map.items():
    if sys.platform.find(k) != -1:
        nasm_format = v
        break

test.file_fixture('wrapper.py')

test.write('SConstruct', """
eee = Environment(tools = ['gcc', 'gnulink', 'nasm'],
                  CFLAGS = ['-m32'],
                  LINKFLAGS = '-m32',
                  ASFLAGS = '-f %(nasm_format)s')
fff = eee.Clone(AS = r'%(_python_)s wrapper.py ' + WhereIs('nasm'))
eee.Program(target = 'eee', source = ['eee.asm', 'eee_main.c'])
fff.Program(target = 'fff', source = ['fff.asm', 'fff_main.c'])
""" % locals())

test.write('eee.asm', 
"""
global name
name:
        db 'eee.asm',0
""")

test.write('fff.asm', 
"""        
global name
name:
        db 'fff.asm',0
""")

test.write('eee_main.c', r"""
#include <stdio.h>
extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("eee_main.c %s\n", name);
        exit (0);
}
""")

test.write('fff_main.c', r"""
#include <stdio.h>
#include <stdlib.h>

extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("fff_main.c %s\n", name);
        exit (0);
}
""")

test.run(arguments = 'eee' + _exe, stderr = None)

test.run(program = test.workpath('eee'), stdout =  "eee_main.c eee.asm\n")

test.must_not_exist('wrapper.out')

test.run(arguments = 'fff' + _exe)

test.run(program = test.workpath('fff'), stdout =  "fff_main.c fff.asm\n")

test.must_match('wrapper.out', "wrapper.py\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
