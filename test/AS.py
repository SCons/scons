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

python = TestSCons.python

if sys.platform == 'win32':
    _exe = '.exe'
else:
    _exe = ''

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
    if a[0] != '/':
        if not inf:
            inf = a
        continue
    if a[:3] == '/Fo': out = a[3:]
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
env = Environment(LINK = r'%s mylink.py',
                  AS = r'%s myas.py',
                  CC = r'%s myas.py')
env.Program(target = 'test1', source = 'test1.s')
env.Program(target = 'test2', source = 'test2.S')
env.Program(target = 'test3', source = 'test3.asm')
env.Program(target = 'test4', source = 'test4.ASM')
env.Program(target = 'test5', source = 'test5.spp')
env.Program(target = 'test6', source = 'test6.SPP')
""" % (python, python, python))

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

if as:

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
aaa = Environment()
bbb = aaa.Copy(AS = r'%s wrapper.py ' + WhereIs('as'))
aaa.Program(target = 'aaa', source = ['aaa.s', 'aaa_main.c'])
bbb.Program(target = 'bbb', source = ['bbb.s', 'bbb_main.c'])
""" % python)

    test.write('aaa.s', 
"""        .file   "aaa.s"
.data
.align 4
.globl name
name:
        .ascii	"aaa.s"
	.byte	0
""")

    test.write('bbb.s', 
"""        .file   "bbb.s"
.data
.align 4
.globl name
name:
        .ascii	"bbb.s"
	.byte	0
""")

    test.write('aaa_main.c', r"""
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
extern char name[];

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        printf("bbb_main.c %s\n", name);
        exit (0);
}
""")

    test.run(arguments = 'aaa' + _exe, stderr = None)

    test.run(program = test.workpath('aaa'), stdout =  "aaa_main.c aaa.s\n")

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(arguments = 'bbb' + _exe)

    test.run(program = test.workpath('bbb'), stdout =  "bbb_main.c bbb.s\n")

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

    test.unlink('wrapper.out')



ml = test.where_is('ml')

if ml:

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
ccc['ENV']['PATH'] = os.environ['PATH']
ddd = ccc.Copy(AS = r'%s wrapper.py ' + ccc['AS'])
ccc.Program(target = 'ccc', source = ['ccc.asm', 'ccc_main.c'])
ddd.Program(target = 'ddd', source = ['ddd.asm', 'ddd_main.c'])
""" % python)

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

    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
eee = Environment(tools = ['gcc', 'gnulink', 'nasm'],
                  ASFLAGS = '-f aout')
fff = eee.Copy(AS = r'%s wrapper.py ' + WhereIs('nasm'))
eee.Program(target = 'eee', source = ['eee.asm', 'eee_main.c'])
fff.Program(target = 'fff', source = ['fff.asm', 'fff_main.c'])
""" % python)

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
