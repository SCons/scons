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
import sys

import TestCmd
import TestSCons

dll_ = TestSCons.dll_
_dll = TestSCons._dll

test = TestSCons.TestSCons()

# Some systems apparently need -ldl on the link line, others don't.
no_dl_lib = "env.Program(target = 'dlopenprog', source = 'dlopenprog.c')"
use_dl_lib = "env.Program(target = 'dlopenprog', source = 'dlopenprog.c', LIBS=['dl'])"

dlopen_line = {
    'darwin' : no_dl_lib,
    'freebsd4' : no_dl_lib,
    'linux2' : use_dl_lib,
    'linux3' : use_dl_lib,
}
platforms_with_dlopen = list(dlopen_line.keys())

test.write('SConstruct', """
env = Environment()
# dlopenprog tries to dynamically load foo1 at runtime using dlopen().
env.LoadableModule(target = 'foo1', source = 'f1.c')
""" + dlopen_line.get(sys.platform, ''))


test.write('f1.c', r"""
#include <stdio.h>

void
f1(void)
{
        printf("f1.c\n");
        fflush(stdout);
}
""")

dlopenprog = r"""
#include <errno.h>
#include <stdio.h>
#include <dlfcn.h>

extern int errno;

int
main(int argc, char *argv[])
{
        argv[argc++] = "--";
        void *foo1_shobj = dlopen("__foo1_name__", RTLD_NOW);
        if(!foo1_shobj){
          printf("Error loading foo1 '__foo1_name__' library at runtime, exiting.\n");
          printf("%d\n", errno);
          perror("");
          return -1;
        }
        void (*f1)() = dlsym(foo1_shobj, "f1\0");
        (*f1)();
        printf("dlopenprog.c\n");
        dlclose(foo1_shobj);
        return 0;
}
"""

# Darwin dlopen()s a bundle named "foo1",
# other systems dlopen() a traditional libfoo1.so file.
foo1_name = {'darwin' : 'foo1'}.get(sys.platform[:6], dll_+'foo1'+_dll)

test.write('dlopenprog.c',
           dlopenprog.replace('__foo1_name__', foo1_name))

test.run(arguments = '.',
         stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

# TODO: Add new Intel-based Macs?  Why are we only picking on Macs?
#if sys.platform.find('darwin') != -1:
#    test.run(program='/usr/bin/file',
#             arguments = "foo1",
#             match = TestCmd.match_re,
#             stdout="foo1: Mach-O bundle (ppc|i386)\n")
# My laptop prints "foo1: Mach-O 64-bit bundle x86_64"

if sys.platform in platforms_with_dlopen:
    os.environ['LD_LIBRARY_PATH'] = test.workpath()
    test.run(program = test.workpath('dlopenprog'),
             stdout = "f1.c\ndlopenprog.c\n")
                 


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
