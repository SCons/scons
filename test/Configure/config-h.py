#!/usr/bin/env python
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Verify creation of a config.h file from a Configure context.
"""


import re

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_exact)

lib = test.Configure_lib
LIB = "LIB" + lib.upper()

test.write('SConstruct', """\
env = Environment()
import os
env.AppendENVPath('PATH', os.environ['PATH'])
conf = Configure(env, config_h = 'config.h')
r1 = conf.CheckFunc('printf')
r2 = conf.CheckFunc('noFunctionCall')
r3 = conf.CheckFunc('memmove')
r4 = conf.CheckType('int')
r5 = conf.CheckType('noType')

m1 = conf.CheckMember('struct timespec.tv_sec', '#include <time.h>')
m2 = conf.CheckMember('struct timespec.tv_nanosec', '#include <time.h>')

r6 = conf.CheckCHeader('stdio.h', '<>')
r7 = conf.CheckCHeader('hopefullynoc-header.h')
r8 = conf.CheckCXXHeader('vector', '<>')
r9 = conf.CheckCXXHeader('hopefullynocxx-header.h')
env = conf.Finish()
conf = Configure(env, config_h = 'config.h')
r10 = conf.CheckLib('%(lib)s', 'sin')
r11 = conf.CheckLib('hopefullynolib', 'sin')
r12 = conf.CheckLibWithHeader('%(lib)s', 'math.h', 'c')
r13 = conf.CheckLibWithHeader('%(lib)s', 'hopefullynoheader2.h', 'c')
r14 = conf.CheckLibWithHeader('hopefullynolib2', 'math.h', 'c')
env = conf.Finish()
""" % locals())

expected_read_str = """\
Checking for C function printf()... yes
Checking for C function noFunctionCall()... no
Checking for C function memmove()... yes
Checking for C type int... yes
Checking for C type noType... no
Checking for C member struct timespec.tv_sec... yes
Checking for C member struct timespec.tv_nanosec... no
Checking for C header file stdio.h... yes
Checking for C header file hopefullynoc-header.h... no
Checking for C++ header file vector... yes
Checking for C++ header file hopefullynocxx-header.h... no
Checking for sin() in C library %(lib)s... yes
Checking for sin() in C library hopefullynolib... no
Checking for C library %(lib)s... yes
Checking for C library %(lib)s... no
Checking for C library hopefullynolib2... no
""" % locals()

expected_build_str = """\
scons: Configure: creating config.h
"""
    
expected_stdout = test.wrap_stdout(build_str=expected_build_str,
                                       read_str=expected_read_str)

expected_config_h = ("""\
#ifndef CONFIG_H_SEEN
#define CONFIG_H_SEEN


/* Define to 1 if the system has the function `printf'. */
#define HAVE_PRINTF 1

/* Define to 1 if the system has the function `noFunctionCall'. */
/* #undef HAVE_NOFUNCTIONCALL */

/* Define to 1 if the system has the function `memmove'. */
#define HAVE_MEMMOVE 1

/* Define to 1 if the system has the type `int'. */
#define HAVE_INT 1

/* Define to 1 if the system has the type `noType'. */
/* #undef HAVE_NOTYPE */

/* Define to 1 if the system has the member `struct timespec.tv_sec`. */
#define HAVE_STRUCT_TIMESPEC_TV_SEC 1

/* Define to 1 if the system has the member `struct timespec.tv_nanosec`. */
/* #undef HAVE_STRUCT_TIMESPEC_TV_NANOSEC */

/* Define to 1 if you have the <stdio.h> header file. */
#define HAVE_STDIO_H 1

/* Define to 1 if you have the <hopefullynoc-header.h> header file. */
/* #undef HAVE_HOPEFULLYNOC_HEADER_H */

/* Define to 1 if you have the <vector> header file. */
#define HAVE_VECTOR 1

/* Define to 1 if you have the <hopefullynocxx-header.h> header file. */
/* #undef HAVE_HOPEFULLYNOCXX_HEADER_H */

/* Define to 1 if you have the `%(lib)s' library. */
#define HAVE_%(LIB)s 1

/* Define to 1 if you have the `hopefullynolib' library. */
/* #undef HAVE_LIBHOPEFULLYNOLIB */

/* Define to 1 if you have the `%(lib)s' library. */
#define HAVE_%(LIB)s 1

/* Define to 1 if you have the `%(lib)s' library. */
/* #undef HAVE_%(LIB)s */

/* Define to 1 if you have the `hopefullynolib2' library. */
/* #undef HAVE_LIBHOPEFULLYNOLIB2 */

#endif /* CONFIG_H_SEEN */
""" % locals())

test.run(stdout=expected_stdout)

config_h = test.read(test.workpath('config.h'), mode='r')
if expected_config_h != config_h:
    print("Unexpected config.h")
    print("Expected: ")
    print("---------------------------------------------------------")
    print(repr(expected_config_h))
    print("---------------------------------------------------------")
    print("Found: ")
    print("---------------------------------------------------------")
    print(repr(config_h))
    print("---------------------------------------------------------")
    print("Stdio: ")
    print("---------------------------------------------------------")
    print(test.stdout())
    print("---------------------------------------------------------")
    test.fail_test()

expected_read_str = re.sub(r'\b((yes)|(no))\b',
                           r'(cached) \1',
                           expected_read_str)
expected_build_str = "scons: `.' is up to date.\n"
expected_stdout = test.wrap_stdout(build_str=expected_build_str,
                                   read_str=expected_read_str)
#expected_stdout = expected_stdout.replace("\n", os.linesep)

test.run(stdout=expected_stdout)    

config_h = test.read(test.workpath('config.h'),mode='r')
if expected_config_h != config_h:
    print("Unexpected config.h")
    print("Expected: ")
    print("---------------------------------------------------------")
    print(repr(expected_config_h))
    print("---------------------------------------------------------")
    print("Found: ")
    print("---------------------------------------------------------")
    print(repr(config_h))
    print("---------------------------------------------------------")
    print("Stdio: ")
    print("---------------------------------------------------------")
    print(test.stdout())
    print("---------------------------------------------------------")
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
