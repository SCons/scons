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

if sys.platform =='darwin':
    # change to make it work with stock OS X python framework
    # we can't link to static libpython because there isn't one on OS X
    # so we link to a framework version. However, testing must also
    # use the same version, or else you get interpreter errors.
    python = "/System/Library/Frameworks/Python.framework/Versions/Current/bin/python"
else:
    python = TestSCons.python
    
_exe   = TestSCons._exe
_obj   = TestSCons._obj

# swig-python expects specific filenames.
# the platform specific suffix won't necessarily work.
if sys.platform == 'win32':
    _dll = '.dll'
else:
    _dll   = '.so' 

test = TestSCons.TestSCons()



test.write('myswig.py', r"""
import getopt
import sys
opts, args = getopt.getopt(sys.argv[1:], 'c:o:')
for opt, arg in opts:
    if opt == '-c': pass
    elif opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:4] != 'swig':
	outfile.write(l)
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools=['default', 'swig'], SWIG = r'%s myswig.py')
env.Program(target = 'test1', source = 'test1.i')
env.CFile(target = 'test2', source = 'test2.i')
env.Copy(SWIGFLAGS = '-c++').Program(target = 'test3', source = 'test3.i')
""" % (python))

test.write('test1.i', r"""
int
main(int argc, char *argv[]) {
	argv[argc++] = "--";
	printf("test1.i\n");
	exit (0);
}
swig
""")

test.write('test2.i', r"""test2.i
swig
""")

test.write('test3.i', r"""
#include <stdio.h>
#include <stdlib.h>
int
main(int argc, char *argv[]) {
	argv[argc++] = "--";
	printf("test3.i\n");
	exit (0);
}
swig
""")

test.run(arguments = '.', stderr = None)

test.run(program = test.workpath('test1' + _exe), stdout = "test1.i\n")
test.fail_test(not os.path.exists(test.workpath('test1_wrap.c')))
test.fail_test(not os.path.exists(test.workpath('test1_wrap' + _obj)))

test.fail_test(test.read('test2_wrap.c') != "test2.i\n")

test.run(program = test.workpath('test3' + _exe), stdout = "test3.i\n")
test.fail_test(not os.path.exists(test.workpath('test3_wrap.cc')))
test.fail_test(not os.path.exists(test.workpath('test3_wrap' + _obj)))



swig = test.where_is('swig')

if swig:

    version = sys.version[:3] # see also sys.prefix documentation

    # handle testing on other platforms:
    frameworks = ''
    ldmodule_prefix = ''
    platform_sys_prefix = sys.prefix
    if sys.platform == 'darwin':
        # OS X has a built-in Python but no static libpython
        # so you should link to it using apple's 'framework' scheme.
        # (see top of file for further explanation)
        frameworks = '-framework Python'
        ldmodule_prefix = '_'
        platform_sys_prefix = '/System/Library/Frameworks/Python.framework/Versions/%s/' % version
    
    test.write("wrapper.py",
"""import os
import string
import sys
open('%s', 'wb').write("wrapper.py\\n")
os.system(string.join(sys.argv[1:], " "))
""" % string.replace(test.workpath('wrapper.out'), '\\', '\\\\'))

    test.write('SConstruct', """
foo = Environment(SWIGFLAGS='-python',
                  CPPPATH='%(platform_sys_prefix)s/include/python%(version)s/',
                  SHCCFLAGS='',
                  LDMODULEPREFIX='%(ldmodule_prefix)s',
                  LDMODULESUFFIX='%(_dll)s',
                  FRAMEWORKSFLAGS='%(frameworks)s',
                  )

swig = foo.Dictionary('SWIG')
bar = foo.Copy(SWIG = r'%(python)s wrapper.py ' + swig)
foo.LoadableModule(target = 'foo', source = ['foo.c', 'foo.i'])
bar.LoadableModule(target = 'bar', source = ['bar.c', 'bar.i'])
""" % locals())

    test.write("foo.c", """\
char *
foo_string()
{
    return "This is foo.c!";
}
""")

    test.write("foo.i", """\
%module foo
%{
/* Put header files here (optional) */
%}

extern char *foo_string();
""")

    test.write("bar.c", """\
char *
bar_string()
{
    return "This is bar.c!";
}
""")

    test.write("bar.i", """\
%module bar
%{
/* Put header files here (optional) */
%}

extern char *bar_string();
""")

    test.run(arguments = ldmodule_prefix+'foo' + _dll)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.run(program = python, stdin = """\
import foo
print foo.foo_string()
""", stdout="""\
This is foo.c!
""")

    test.up_to_date(arguments = ldmodule_prefix+'foo' + _dll)

    test.run(arguments = ldmodule_prefix+'bar' + _dll)

    test.fail_test(test.read('wrapper.out') != "wrapper.py\n")

    test.run(program = python, stdin = """\
import foo
import bar
print foo.foo_string()
print bar.bar_string()
""", stdout="""\
This is foo.c!
This is bar.c!
""")

    test.up_to_date(arguments = '.')



test.pass_test()
