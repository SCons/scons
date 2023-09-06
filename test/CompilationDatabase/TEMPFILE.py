#!/usr/bin/env python
#
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
Test that CompilationDatabase works when TEMPFILE is being used to handle long
commandlines for compilers/linkers/etc
"""

import sys
import os
import os.path
import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('mygcc.py')
test.file_fixture('test_main.c')
test.file_fixture('fixture/SConstruct_tempfile', 'SConstruct')

test.run()

rel_files = [
    'compile_commands_only_arg.json',
]

example_rel_file = """[
    {
        "command": "%s mygcc.py cc -o test_main.o -c test_main.c",
        "directory": "%s",
        "file": "test_main.c",
        "output": "test_main.o"
    }
]
""" % (sys.executable, test.workdir)

if sys.platform == 'win32':
    example_rel_file = example_rel_file.replace('\\', '\\\\')

for f in rel_files:
    # print("Checking:%s" % f)
    test.must_exist(f)
    test.must_match(f, example_rel_file, mode='r')

test.pass_test()
