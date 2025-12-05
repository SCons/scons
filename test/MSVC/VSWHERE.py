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
Test the ability to configure the $VSWHERE construction variable.
Also test that vswhere.exe is found and sets VSWHERE to the correct values
"""
import os.path
import SCons.Tool.MSCommon
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()
test.skip_if_not_msvc()
test.verbose_set(1)

_default_vc = SCons.Tool.MSCommon.vc.get_installed_vcs_components()[0]
if _default_vc.msvc_vernum < 14.1:
    test.skip_test("no installed msvc requires vswhere.exe; skipping test\n")

test.dir_fixture('VSWHERE-fixture')

test.run(arguments=".")

# Now grab info out of stdout
lines = test.stdout().splitlines()

# Debug code
# print("LINES:\n%s" % lines)

default_locations = []
detected_path = None
env_path = None
for l in lines:
    if 'VSWHERE_PATH' in l:
        path = l.strip().split('=')[-1]
        default_locations.append(path)
    elif 'VSWHERE-detect' in l:
        detected_path = l.strip().split('=')[-1]
    elif 'VSWHERE-env' in l:
        env_path = l.strip().split('=')[-1]
    elif 'VSWHERE-util' in l:
        util_path = l.strip().split('=')[-1]

# Debug code
# print("VPP:%s" % default_locations)
# print("V-D:%s" % detected_path)
# print("V-E:%s" % env_path)
# print("V-U:%s" % util_path)


test.fail_test(
    len(default_locations) == 0, message='No default vswhere.exe locations found'
)
test.fail_test(
    detected_path is None,
    message='No vswhere.exe detected in default paths :%s' % default_locations,
)
test.fail_test(
    detected_path not in default_locations,
    message='detected path [%s] not in default locations [%s]' % (detected_path, default_locations),
)

expected_env_path = os.path.join(test.workdir, 'vswhere.exe')
test.fail_test(
    env_path != expected_env_path,
    message='VSWHERE not\n\t%s\n\t but\n\t%s' % (expected_env_path, env_path),
)

expected_util_path = os.path.join(test.workdir, 'vswhere.exe')
test.fail_test(
    util_path != expected_env_path,
    message='VSWHERE not\n\t%s\n\t but\n\t%s' % (expected_util_path, util_path),
)

test.pass_test()

# here for reference, unused
expected = r"""
PS C:\Users\Bill\AppData\Local\Temp\testcmd.11256.1ae1_as5> py -3.8 C:\Users\Bill\devel\scons\git\scons-2\scripts\scons.py
scons: Reading SConscript files ...
VSWHERE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
VSWHERE_PATH=C:\Program Files\Microsoft Visual Studio\Installer\vswhere.exe
VSWHERE_PATH=C:\ProgramData\chocolatey\bin\vswhere.exe
VSWHERE-detect=C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe
Copy("C:\Users\Bill\AppData\Local\Temp\testcmd.11256.1ae1_as5\vswhere.exe", "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe")
VSWHERE-env=C:\Users\Bill\AppData\Local\Temp\testcmd.11256.1ae1_as5\vswhere.exe
VSWHERE-util=C:\Users\Bill\AppData\Local\Temp\testcmd.11256.1ae1_as5\vswhere.exe
scons: done reading SConscript files.
scons: Building targets ...
scons: `.' is up to date.
scons: done building targets.
"""
