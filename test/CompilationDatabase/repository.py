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
from TestCmd import IS_WINDOWS

test = TestSCons.TestSCons()

test.file_fixture('mylink.py', 'build/mylink.py')
test.file_fixture('mygcc.py', 'build/mygcc.py')

test.subdir('src', 'build')

test.file_fixture(['fixture', 'SConstruct_repository'], 'src/SConstruct')
test.file_fixture(['fixture', 'main.c'], 'src/main.c')

test.run(chdir='build', arguments='-Y ../src')

source = test.workpath('src', 'main.c')
directory = test.workpath('build')
main_obj = 'main' + TestSCons._obj
# Build expected JSON safely
cmd = '%s mygcc.py cc -o %s -c %s' % (sys.executable, main_obj, source)
if IS_WINDOWS:
    cmd = cmd.replace('\\', '\\\\')
    dir_s = directory.replace('\\', '\\\\')
    src_s = source.replace('\\', '\\\\')
    out_s = main_obj.replace('\\', '\\\\')
else:
    dir_s = directory
    src_s = source
    out_s = main_obj
expected = """[
    {
        "command": "%s",
        "directory": "%s",
        "file": "%s",
        "output": "%s"
    }
]
""" % (cmd, dir_s, src_s, out_s)

test.must_match(['build', 'compile_commands.json'], expected, mode='r')

test.pass_test()
