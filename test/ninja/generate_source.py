#!/usr/bin/env python
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
#

import os

import TestSCons
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

try:
    import ninja
except ImportError:
    test.skip_test("Could not find module in python")

_python_ = TestSCons._python_
_exe = TestSCons._exe

ninja_bin = os.path.abspath(os.path.join(
    ninja.__file__,
    os.pardir,
    'data',
    'bin',
    'ninja' + _exe))

test.dir_fixture('ninja-fixture')

shell = '' if IS_WINDOWS else './'

test.write('SConstruct', """
SetOption('experimental','ninja')
DefaultEnvironment(tools=[])

env = Environment()
env.Tool('ninja')
prog = env.Program(target = 'generate_source', source = 'generate_source.c')
env.Command('generated_source.c', prog, '%(shell)sgenerate_source%(_exe)s')
env.Program(target = 'generated_source', source = 'generated_source.c')
""" % locals())

test.write('generate_source.c', """
#include <stdio.h>

int main(int argc, char *argv[]) {
    FILE *fp;

    fp = fopen("generated_source.c", "w");
    fprintf(fp, "#include <stdio.h>\\n");
    fprintf(fp, "#include <stdlib.h>\\n");
    fprintf(fp, "\\n");
    fprintf(fp, "int\\n");
    fprintf(fp, "main(int argc, char *argv[])\\n");
    fprintf(fp, "{\\n");
    fprintf(fp, "        printf(\\"generated_source.c\\");\\n");
    fprintf(fp, "        exit (0);\\n");
    fprintf(fp, "}\\n");
    fclose(fp);
}
""")

# generate simple build
test.run(stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_contain_all(test.stdout(), 'Executing:')
test.must_contain_all(test.stdout(), 'ninja%(_exe)s -f' % locals())
test.run(program=test.workpath('generated_source' + _exe), stdout="generated_source.c")

# clean build and ninja files
test.run(arguments='-c', stdout=None)
test.must_contain_all_lines(test.stdout(), [
    'Removed generate_source.o',
    'Removed generate_source' + _exe,
    'Removed generated_source.c',
    'Removed generated_source.o',
    'Removed generated_source' + _exe,
    'Removed build.ninja'])

# only generate the ninja file
test.run(arguments='--disable-execute-ninja', stdout=None)
test.must_contain_all_lines(test.stdout(), ['Generating: build.ninja'])
test.must_not_exist(test.workpath('generated_source' + _exe))

# run ninja independently
program = test.workpath('run_ninja_env.bat') if IS_WINDOWS else ninja_bin
test.run(program=program, stdout=None)
test.run(program=test.workpath('generated_source' + _exe), stdout="generated_source.c")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
