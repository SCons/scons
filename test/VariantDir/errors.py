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

"""
Validate successful handling of errors when duplicating things in
VariantDirs.  This is generally when the VariantDir, or something in it,
is read-only.
"""

import os
import stat
import sys
import TestSCons

test = TestSCons.TestSCons()

for dir in ['normal', 'ro-dir', 'ro-SConscript', 'ro-src']:
    test.subdir(dir, [dir, 'src'])

    test.write([dir, 'SConstruct'], """\
import os.path
VariantDir('build', 'src')
SConscript(os.path.join('build', 'SConscript'))
""") 

    test.write([dir, 'src', 'SConscript'], """\
def fake_scan(node, env, target):
    # We fetch the contents here, even though we don't examine
    # them, because get_contents() will cause the engine to
    # try to link the source file into the build directory,
    # potentially triggering a different failure case.
    contents = node.get_contents()
    return []

def cat(env, source, target):
    target = str(target[0])
    with open(target, "w") as f:
        for src in source:
            with open(str(src), "r") as f2:
                f.write(f2.read())

env = Environment(BUILDERS={'Build':Builder(action=cat)},
                  SCANNERS=[Scanner(fake_scan, skeys = ['.in'])])

# Do some Node test operations to ensure no side-effects cause failures
File('file.in').exists()
File('file.in').is_derived()

env.Build('file.out', 'file.in')
""")

    test.write([dir, 'src', 'file.in'], dir + "/src/file.in\n")

# Just verify that the normal case works fine.
test.run(chdir = 'normal', arguments = ".")

test.must_match(['normal', 'build', 'file.out'], "normal/src/file.in\n", mode='r')

# Verify the error when the VariantDir itself is read-only.  Don't bother
# to test this on Windows, because the ACL (I think) still allows the
# owner to create files in the directory even when it's read-only.
if sys.platform != 'win32':
    dir = os.path.join('ro-dir', 'build')
    test.subdir(dir)
    os.chmod(dir, os.stat(dir)[stat.ST_MODE] & ~stat.S_IWUSR)

    test.run(chdir = 'ro-dir',
             arguments = ".",
             status = 2,
             stderr = "scons: *** Cannot duplicate `%s' in `build': Permission denied.  Stop.\n" % os.path.join('src', 'SConscript'))

# Verify the error when the SConscript file within the VariantDir is
# read-only.  Note that we have to make the directory read-only too,
# because otherwise our duplication logic will be able to unlink
# the read-only SConscript and duplicate the new one.
dir = os.path.join('ro-SConscript', 'build')
test.subdir(dir)
SConscript = test.workpath(dir, 'SConscript')
test.write(SConscript, '')
os.chmod(SConscript, os.stat(SConscript)[stat.ST_MODE] & ~stat.S_IWUSR)
with open(SConscript, 'r'):
    os.chmod(dir, os.stat(dir)[stat.ST_MODE] & ~stat.S_IWUSR)

    test.run(chdir = 'ro-SConscript',
             arguments = ".",
             status = 2,
             stderr = "scons: *** Cannot duplicate `%s' in `build': Permission denied.  Stop.\n" % os.path.join('src', 'SConscript'))

    os.chmod('ro-SConscript', os.stat('ro-SConscript')[stat.ST_MODE] | stat.S_IWUSR)

test.run(chdir = 'ro-SConscript',
         arguments = ".",
         status = 2,
         stderr = "scons: *** Cannot duplicate `%s' in `build': Permission denied.  Stop.\n" % os.path.join('src', 'SConscript'))

# Verify the error when the source file within the VariantDir is
# read-only.  Note that we have to make the directory read-only too,
# because otherwise our duplication logic will be able to unlink the
# read-only source file and duplicate the new one.  But because we've
# made the VariantDir read-only, we must also create a writable SConscript
# file there so it can be duplicated from the source directory.
dir = os.path.join('ro-src', 'build')
test.subdir(dir)
test.write([dir, 'SConscript'], '')
file_in = test.workpath(dir, 'file.in')
test.write(file_in, '')
os.chmod(file_in, os.stat(file_in)[stat.ST_MODE] & ~stat.S_IWUSR)
with open(file_in, 'r'):
    os.chmod(dir, os.stat(dir)[stat.ST_MODE] & ~stat.S_IWUSR)

    test.run(chdir = 'ro-src',
             arguments = ".",
             status = 2,
             stderr = """\
scons: *** Cannot duplicate `%s' in `build': Permission denied.  Stop.
""" % (os.path.join('src', 'file.in')))

    test.run(chdir = 'ro-src',
             arguments = "-k .",
             status = 2,
             stderr = """\
scons: *** Cannot duplicate `%s' in `build': Permission denied.  Stop.
""" % (os.path.join('src', 'file.in')))

# ensure that specifying multiple source directories for one
# build directory results in an error message, rather
# than just silently failing.
test.subdir('duplicate', ['duplicate', 'src1'], ['duplicate', 'src2'])

duplicate_SConstruct_path = test.workpath('duplicate', 'SConstruct')

test.write(duplicate_SConstruct_path, """\
VariantDir('build', 'src1')
VariantDir('build', 'src2')
""")

expect_stderr = """
scons: *** 'build' already has a source directory: 'src1'.
""" + test.python_file_line(duplicate_SConstruct_path, 2)

test.run(chdir = 'duplicate',
         arguments = ".",
         status = 2,
         stderr = expect_stderr)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
