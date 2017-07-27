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
Test the ability to configure the $MSVC_UWP_APP construction variable with
the desired effect.
"""

import TestSCons
import SCons.Tool.MSCommon.vc as msvc

def AreVCStoreLibPathsInLIBPATH(output):
    libpath = None
    msvc_version = None
    lines = output.splitlines()
    for line in lines:
        if 'env[ENV][LIBPATH]=' in line:
            libpath = line.split('=')[1]
        elif 'env[MSVC_VERSION]=' in line:
            msvc_version = line.split('=')[1]

    if not libpath or not msvc_version:
        # Couldn't find the libpath or msvc version in the output
        return (False, False, None)

    libpaths = libpath.lower().split(';')
    (vclibstore_path_present, vclibstorerefs_path_present) = (False, False)
    for path in libpaths:
        # Look for the Store VC Lib paths in the LIBPATH:
        # [VS install path]\VC\LIB\store[\arch] and 
        # [VS install path]\VC\LIB\store\references
        # For example,
        # C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\amd64
        # C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\references
        if r'vc\lib\store\references' in path:
            vclibstorerefs_path_present = True
        elif r'vc\lib\store' in path:
            vclibstore_path_present = True

    return (vclibstore_path_present, vclibstorerefs_path_present, msvc_version)

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

test.write('SConstruct', """
if ARGUMENTS.get('MSVC_UWP_APP'):
    help_vars = Variables()
    help_vars.Add(EnumVariable(
                  'MSVC_UWP_APP',
                  'Build for a Universal Windows Platform (UWP) Application',
                  '0',
                  allowed_values=('0', '1')))
else:
    help_vars = None
env = Environment(tools=['default', 'msvc'], variables=help_vars)
# Print the ENV LIBPATH to stdout
print('env[ENV][LIBPATH]=%s' % env.get('ENV').get('LIBPATH'))
print('env[MSVC_VERSION]=%s' % env.get('MSVC_VERSION'))
""")

installed_msvc_versions = msvc.cached_get_installed_vcs()
# MSVC guaranteed to be at least one version on the system or else skip_if_not_msvc() function
# would have skipped the test
greatest_msvc_version_on_system = installed_msvc_versions[0]
maj, min = msvc.msvc_version_to_maj_min(greatest_msvc_version_on_system)

# We always use the greatest MSVC version installed on the system

# Test setting MSVC_UWP_APP is '1' (True)
test.run(arguments = "MSVC_UWP_APP=1")
(vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test(msvc_version != greatest_msvc_version_on_system)
# VS2015+
if maj >= 14:
    test.fail_test((vclibstore_path_present is False) or (vclibstorerefs_path_present is False),
                   message='VC Store LIBPATHs NOT present when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)
else:
    test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                   message='VC Store LIBPATHs present for unsupported version when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)

# Test setting MSVC_UWP_APP is '0' (False)
test.run(arguments = "MSVC_UWP_APP=0")
(vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test(msvc_version != greatest_msvc_version_on_system)
test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                   message='VC Store LIBPATHs present when MSVC_UWP_APP=0 (msvc_version=%s)' % msvc_version)

# Test not setting MSVC_UWP_APP
test.run(arguments = "")
(vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test(msvc_version != greatest_msvc_version_on_system)
test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                   message='VC Store LIBPATHs present when MSVC_UWP_APP not set (msvc_version=%s)' % msvc_version)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
