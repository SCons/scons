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
Verify correct use of the live 'ml' assembler.
"""

import sys

import TestSCons

_python_ = TestSCons._python_
_exe   = TestSCons._exe

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test("Skipping ml test on non-win32 platform '%s'\n" % sys.platform)

ml = test.where_is('ml')

if not ml:
    test.skip_test("ml not found; skipping test\n")

test.file_fixture('wrapper.py')

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

test.must_not_exist('wrapper.out')

test.run(arguments = 'ddd' + _exe)

test.run(program = test.workpath('ddd'), stdout =  "ddd_main.c ddd.asm\n")

test.must_match('wrapper.out', "wrapper.py\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
