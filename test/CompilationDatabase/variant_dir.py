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
"""
Test CompilationDatabase and several variations of ways to call it
and values of COMPILATIONDB_USE_ABSPATH
"""

import sys
import os
import os.path
import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('mylink.py')
test.file_fixture('mygcc.py')

test.verbose_set(1)
test.file_fixture('fixture/SConstruct_variant', 'SConstruct')
test.file_fixture('test_main.c', 'src/test_main.c')
test.run()

rel_files = [
    'compile_commands_only_arg.json',
    'compile_commands_target.json',
    'compile_commands.json',
    'compile_commands_over_rel.json',
    'compile_commands_over_abs_0.json'
]

abs_files = [
    'compile_commands_clone_abs.json',
    'compile_commands_over_abs.json',
    'compile_commands_target_over_abs.json',
    'compile_commands_over_abs_1.json',
]

example_rel_file = """[
    {
        "command": "%(exe)s mygcc.py cc -o %(output_file)s -c %(variant_src_file)s",
        "directory": "%(workdir)s",
        "file": "%(src_file)s",
        "output": "%(output_file)s"
    },
    {
        "command": "%(exe)s mygcc.py cc -o %(output2_file)s -c %(src_file)s",
        "directory": "%(workdir)s",
        "file": "%(src_file)s",
        "output": "%(output2_file)s"
    }
]""" % {'exe': sys.executable,
        'workdir': test.workdir,
        'src_file': os.path.join('src', 'test_main.c'),
        'output_file': os.path.join('build', 'test_main.o'),
        'output2_file': os.path.join('build2', 'test_main.o'),
        'variant_src_file': os.path.join('build', 'test_main.c')
        }

if sys.platform == 'win32':
    example_rel_file = example_rel_file.replace('\\', '\\\\')

for f in rel_files:
    # print("Checking:%s" % f)
    test.must_exist(f)
    test.must_match(f, example_rel_file, mode='r')

example_abs_file = """[
    {
        "command": "%(exe)s mygcc.py cc -o %(output_file)s -c %(variant_src_file)s",
        "directory": "%(workdir)s",
        "file": "%(abs_src_file)s",
        "output": "%(abs_output_file)s"
    },
    {
        "command": "%(exe)s mygcc.py cc -o %(output2_file)s -c %(src_file)s",
        "directory": "%(workdir)s",
        "file": "%(abs_src_file)s",
        "output": "%(abs_output2_file)s"
    }
]""" % {'exe': sys.executable,
        'workdir': test.workdir,
        'src_file': os.path.join('src', 'test_main.c'),
        'abs_src_file': os.path.join(test.workdir, 'src', 'test_main.c'),
        'abs_output_file': os.path.join(test.workdir, 'build', 'test_main.o'),
        'abs_output2_file': os.path.join(test.workdir, 'build2', 'test_main.o'),
        'output_file': os.path.join('build', 'test_main.o'),
        'output2_file': os.path.join('build2', 'test_main.o'),
        'variant_src_file': os.path.join('build', 'test_main.c')}

if sys.platform == 'win32':
    example_abs_file = example_abs_file.replace('\\', '\\\\')

for f in abs_files:
    test.must_exist(f)
    test.must_match(f, example_abs_file, mode='r')

test.pass_test()
