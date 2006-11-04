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

import os
import string
import sys
import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()



if sys.platform == 'win32':

    test.write('mylink.py', r"""
import string
import sys
args = sys.argv[1:]
while args:
    a = args[0]
    if a[0] != '/':
        break
    args = args[1:]
    if string.lower(a[:5]) == '/out:': out = a[5:]
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:5] != '#link':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myas.py', r"""
import sys
args = sys.argv[1:]
inf = None
while args:
    a = args[0]
    args = args[1:]
    if not a[0] in "/-":
        if not inf:
            inf = a
        continue
    if a[:3] == '/Fo': out = a[3:]
    if a == '-o':
        out = args[0]
        args = args[1:]
infile = open(inf, 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:3] != '#as':
        outfile.write(l)
sys.exit(0)
""")

else:

    test.write('mylink.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'o:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:5] != '#link':
        outfile.write(l)
sys.exit(0)
""")

    test.write('myas.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'co:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:3] != '#as':
        outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(LINK = r'%(_python_)s mylink.py',
                  AS = r'%(_python_)s myas.py',
                  CC = r'%(_python_)s myas.py')
env.Program(target = 'test1', source = 'test1.s')
env.Program(target = 'test2', source = 'test2.S')
env.Program(target = 'test3', source = 'test3.asm')
env.Program(target = 'test4', source = 'test4.ASM')
env.Program(target = 'test5', source = 'test5.spp')
env.Program(target = 'test6', source = 'test6.SPP')
""" % locals())

test.write('test1.s', r"""This is a .s file.
#as
#link
""")

test.write('test2.S', r"""This is a .S file.
#as
#link
""")

test.write('test3.asm', r"""This is a .asm file.
#as
#link
""")

test.write('test4.ASM', r"""This is a .ASM file.
#as
#link
""")

test.write('test5.spp', r"""This is a .spp file.
#as
#link
""")

test.write('test6.SPP', r"""This is a .SPP file.
#as
#link
""")

test.run(arguments = '.', stderr = None)

test.fail_test(test.read('test1' + _exe) != "This is a .s file.\n")

test.fail_test(test.read('test2' + _exe) != "This is a .S file.\n")

test.fail_test(test.read('test3' + _exe) != "This is a .asm file.\n")

test.fail_test(test.read('test4' + _exe) != "This is a .ASM file.\n")

test.fail_test(test.read('test5' + _exe) != "This is a .spp file.\n")

test.fail_test(test.read('test6' + _exe) != "This is a .SPP file.\n")


as = test.detect('AS', 'as')
x86 = (sys.platform == 'win32' or string.find(sys.platform, 'linux') != -1)

if as and x86:

    test.write("wrapper.py", """\
import os
import string
import sys
open('%s', 'wb').write("wrapper.py: %%s\\n" %% sys.argv[-1])
cmd = string.join(sys.argv[1:])
os.system(cmd)
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """\
aaa = Environment()
bbb = aaa.Clone(AS = r'%(_python_)s wrapper.py ' + WhereIs('as'))
ccc = aaa.Clone(CPPPATH=['.'])
aaa.Program(target = 'aaa', source = ['aaa.s', 'aaa_main.c'])
bbb.Program(target = 'bbb', source = ['bbb.s', 'bbb_main.c'])
ccc.Program(target = 'ccc', source = ['ccc.S', 'ccc_main.c'])
""" % locals())

    test.write('aaa.s', 
"""        .file   "aaa.s"
.data
.align 4
.globl name
name:
        .ascii	"aaa.s"
        .byte	0
""")

    test.write('bbb.s', """\
.file   "bbb.s"
.data
.align 4
.globl name
name:
        .ascii	"bbb.s"
        .byte	0
""")

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
    test.run(program = test.workpath('ccc'), stdout =  "ccc_main.c ccc.S\n")

    test.fail_test(test.read('wrapper.out') != "wrapper.py: bbb.s\n")

    test.write("ccc.h", """\
#define STRING  "ccc.S 2"
""")

    test.run()
    test.run(program = test.workpath('ccc'), stdout =  "ccc_main.c ccc.S 2\n")

    test.unlink('wrapper.out')



ml = test.where_is('ml')

if ml and sys.platform == 'win32':

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
import os
ccc = Environment(tools = ['msvc', 'mslink', 'masm'],
                  ASFLAGS = '/nologo /coff')
ccc['ENV']['PATH'] = ccc['ENV']['PATH'] + os.pathsep + os.environ['PATH']
ddd = ccc.Clone(AS = r'%(_python_)s wrapper.py ' + ccc['AS'])
ccc.Program(target = 'ccc', source = ['ccc.asm', 'ccc_main.c'])
ddd.Program(target = 'ddd', source = ['ddd.asm', 'ddd_main.c'])
""" % locals())

    test.write('ccc.asm', 
"""
DSEG	segment
        PUBLIC _name
_name	byte "ccc.asm",0
DSEG	ends
        end
""")

    test.write('ddd.asm', 
"""        
DSEG	segment
        PUBLIC _name
_name	byte "ddd.asm",0
DSEG	ends
        end
""")

    test.write('ccc_main.c', r"""
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

    test.run(arguments = 'ccc' + _exe, stderr = None)

    test.run(program = test.workpath('ccc'), stdout =  "ccc_main.c ccc.asm\n")

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(arguments = 'ddd' + _exe)

    test.run(program = test.workpath('ddd'), stdout =  "ddd_main.c ddd.asm\n")

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")




nasm = test.where_is('nasm')

if nasm:

    # Allow flexibility about the type of object/executable format
    # needed on different systems.  Format_map is a dict that maps
    # sys.platform substrings to the correct argument for the nasm -f
    # option.  The default is "elf," which seems to be a reasonable
    # lowest common denominator (works on both Linux and FreeBSD,
    # anyway...).
    nasm_format = 'elf'
    format_map = {}
    for k, v in format_map.items():
        if string.find(sys.platform, k) != -1:
            nasm_format = v
            break

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
eee = Environment(tools = ['gcc', 'gnulink', 'nasm'],
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

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(arguments = 'fff' + _exe)

    test.run(program = test.workpath('fff'), stdout =  "fff_main.c fff.asm\n")

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")



test.pass_test()
