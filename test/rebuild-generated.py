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
Test case for the bug report:
"[ 1088979 ] Unnecessary rebuild with generated header file"
(<http://sourceforge.net/tracker/index.php?func=detail&aid=1088979&group_id=30337&atid=398971>).

Unnecessary rebuild with generated header file
Scons rebuilds some nodes when invoked twice. The
trigger seems to be a generated C++ source file that
includes a header file that also is generated.

A tarball with a minimal test case is attached.
Transcript for reproducing:

cd /tmp
tar xzf scons_rebuild_debug.tar.gz
cd scons_rebuild_debug
scons target.o
scons target.o


Note that the bug is not triggered when scons is run
without arguments.

This may be a duplicate to bug 1019683.
"""

import os
import sys
import sysconfig

import TestSCons

test = TestSCons.TestSCons()

_obj = TestSCons._obj

if sys.platform == 'win32' and not sysconfig.get_platform() in ("mingw",):

    generator_name = 'generator.bat'
    test.write(generator_name, '@echo #include "header.hh"')
    kernel_action = "$SOURCES  > $TARGET"
else:
    generator_name = 'generator.sh'
    test.write(generator_name, 'echo \'#include "header.hh"\'')
    kernel_action = "sh $SOURCES  > $TARGET"

if sysconfig.get_platform() in ("mingw",):
    # mingw Python uses a sep of '/', when Command fires, that will not work.
    # use its altsep instead, that is the standard Windows separator.
    sep = os.altsep
else:
    sep = os.sep


test.write('SConstruct', """\
env = Environment()

kernelDefines = env.Command("header.hh", "header.hh.in", Copy('$TARGET', '$SOURCE'))
kernelImporterSource = env.Command("generated.cc", ["%s"], "%s")
kernelImporter = env.Program(kernelImporterSource + ["main.cc"])
kernelImports = env.Command("KernelImport.hh", kernelImporter, r".%s$SOURCE > $TARGET")
osLinuxModule = env.StaticObject(["target.cc"])
""" % (generator_name, kernel_action, sep))

test.write('main.cc', """\
int
main(int, char *[])
{
    return (0);
}
""")

test.write('target.cc', """\
#if 0

#include "KernelImport.hh"

#endif
""")

test.write("header.hh.in", "#define HEADER_HH 1\n")

test.run(arguments = 'target' + _obj)

expected_stdout = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: `target%(_obj)s' is up to date.
scons: done building targets.
""" % locals()

test.run(arguments = 'target' + _obj, stdout=expected_stdout)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
