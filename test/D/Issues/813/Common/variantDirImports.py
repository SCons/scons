#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""
Regression test for github issue #813: "DMD and variant_dir don't play nice".

D compilers resolve ``import module;`` strictly through -I paths, unlike C's
quoted includes which also search the including file's own directory. The D
scanner already searches the source file's directory, so dependencies are
tracked, but the D tools' default DPATH of ``['#/']`` only put the top-level
SConstruct directory on the compile line. With sources in a subdirectory
the compiler could not find local modules. The problem was somewhat masked
because quick tests often put some test files in the top directory and
don't try sources in a subdirectory - this happens to work because the
place to include from *was* the topdir.

https://github.com/SCons/scons/issues/813
"""

import sys
from os.path import abspath, dirname

import TestSCons

sys.path.insert(1, abspath(dirname(__file__) + '/../../../Support'))
from executablesSearch import isExecutableOfToolAvailable


def testForTool(tool):
    test = TestSCons.TestSCons()

    if not isExecutableOfToolAvailable(test, tool):
        test.skip_test(
            "Required executable for tool '{0}' not found, skipping test.\n".format(tool)
        )

    # duplicate=False is the interesting case: sources stay in src/, build
    # products go to build/, and the compiler runs from the top-level dir.
    test.write('SConstruct', """\
env = Environment(tools=['default', '%(tool)s'])
env.VariantDir('build', 'src', duplicate=False)
env.Program('build/prog', ['build/main.d'])
""" % locals())

    test.subdir('src')
    test.write(['src', 'main.d'], """\
import mymod;
void main() {}
""")
    test.write(['src', 'mymod.d'], """\
module mymod;
""")

    # Before the fix this fails with "unable to read module `mymod'" because
    # the compiler only gets -I. (the top-level dir), not -Isrc.
    test.run()

    # The scanner should still track the imported module as a dependency.
    test.up_to_date()
    test.write(['src', 'mymod.d'], """\
module mymod;
// touched
""")
    test.not_up_to_date()

    test.pass_test()
