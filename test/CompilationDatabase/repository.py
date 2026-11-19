#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Test CompilationDatabase with sources found through a repository.

The source files are not in the build directory: SCons finds them in a
repository (-Y).  The "file" entry must point at the file SCons actually
compiles, not at the (non-existent) local source path.
"""

import sys

import TestSCons

test = TestSCons.TestSCons()

test.file_fixture('mylink.py', 'build/mylink.py')
test.file_fixture('mygcc.py', 'build/mygcc.py')

test.subdir('src', 'build')

test.file_fixture(['fixture', 'SConstruct_repository'], 'src/SConstruct')
test.file_fixture(['fixture', 'main.c'], 'src/main.c')

test.run(chdir='build', arguments='-Y ../src')

source = test.workpath('src', 'main.c')
expected = """[
    {
        "command": "%s mygcc.py cc -o main.o -c %s",
        "directory": "%s",
        "file": "%s",
        "output": "main.o"
    }
]
""" % (sys.executable, source, test.workpath('build'), source)

if sys.platform == 'win32':
    expected = expected.replace('\\', '\\\\')

test.must_match(['build', 'compile_commands.json'], expected, mode='r')

test.pass_test()
