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
from SCons.Tool.MSCommon.vc import get_msvc_version_numeric

def AreVCStoreLibPathsInLIBPATH(output):
    libpath = None
    msvc_version = None
    UWP_APP = None
    lines = output.splitlines()
    for line in lines:
        if 'env[ENV][LIBPATH]=' in line:
            libpath = line.split('=')[1]
        elif 'env[MSVC_VERSION]=' in line:
            msvc_version = line.split('=')[1]
        elif 'env[ENV][VSCMD_ARG_app_plat]=' in line:
            UWP_APP = line.split('=')[1]

    if not libpath or not msvc_version:
        # Couldn't find the libpath or msvc version in the output
        return (False, False, None)

    libpaths = libpath.lower().split(';')
    msvc_num = float(get_msvc_version_numeric(msvc_version))
    
    (vclibstore_path_present, vclibstorerefs_path_present) = (False, False)
    for path in libpaths:
        # Look for the Store VC Lib paths in the LIBPATH:
        # [VS install path]\VC\LIB\store[\arch] and 
        # [VS install path]\VC\LIB\store\references
        # For example,
        # C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\amd64
        # C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\references
        
        if msvc_num <= 14:
            if r'vc\lib\store\references' in path:
                vclibstorerefs_path_present = True
            elif r'vc\lib\store' in path:
                vclibstore_path_present = True
        elif msvc_num > 14:
            if UWP_APP == "UWP":
                if(r'\lib\x86\store\references' in path
                or r'\lib\x64\store' in path):
                    vclibstorerefs_path_present = True
                    vclibstore_path_present = True

    return (vclibstore_path_present, vclibstorerefs_path_present, msvc_version)

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

installed_msvc_versions = msvc.cached_get_installed_vcs()
# MSVC guaranteed to be at least one version on the system or else
# skip_if_not_msvc() function would have skipped the test

msvc_140 = '14.0' in installed_msvc_versions
msvc_141 = '14.1' in installed_msvc_versions
msvc_142 = '14.2' in installed_msvc_versions

if not any((msvc_140, msvc_141, msvc_142)):
    test.skip_test("Available MSVC doesn't support App store\n")

if msvc_140:
    test.write('SConstruct', """\
if ARGUMENTS.get('MSVC_UWP_APP'):
    help_vars = Variables()
    help_vars.Add(EnumVariable(
                'MSVC_UWP_APP',
                'Build a Universal Windows Platform (UWP) Application',
                '0',
                allowed_values=('0', '1')))
else:
    help_vars = None
env = Environment(tools=['default', 'msvc'], variables=help_vars, MSVC_VERSION='14.0')
# Print the ENV LIBPATH to stdout
print('env[ENV][LIBPATH]=%s' % env.get('ENV').get('LIBPATH'))
print('env[MSVC_VERSION]=%s' % env.get('MSVC_VERSION'))
""")

    # Test setting MSVC_UWP_APP is '1' (True)
    test.run(arguments = "MSVC_UWP_APP=1")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is False) or (vclibstorerefs_path_present is False),
                message='VC Store LIBPATHs NOT present when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)

    # Test setting MSVC_UWP_APP is '0' (False)
    test.run(arguments = "MSVC_UWP_APP=0")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                message='VC Store LIBPATHs present when MSVC_UWP_APP=0 (msvc_version=%s)' % msvc_version)

    # Test not setting MSVC_UWP_APP
    test.run(arguments = "")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                message='VC Store LIBPATHs present when MSVC_UWP_APP not set (msvc_version=%s)' % msvc_version)

if msvc_141 or msvc_142:
    if msvc_142:
        test.write('SConstruct', """\
if ARGUMENTS.get('MSVC_UWP_APP'):
    help_vars = Variables()
    help_vars.Add(EnumVariable(
                'MSVC_UWP_APP',
                'Build a Universal Windows Platform (UWP) Application',
                '0',
                allowed_values=('0', '1')))
else:
    help_vars = None
env = Environment(tools=['default', 'msvc'], variables=help_vars, MSVC_VERSION='14.2')
# Print the ENV LIBPATH to stdout
print('env[ENV][LIBPATH]=%s' % env.get('ENV').get('LIBPATH'))
print('env[MSVC_VERSION]=%s' % env.get('MSVC_VERSION'))
print('env[ENV][VSCMD_ARG_app_plat]=%s' % env.get('ENV').get('VSCMD_ARG_app_plat'))
""")
    elif msvc_141:
        test.write('SConstruct', """\
if ARGUMENTS.get('MSVC_UWP_APP'):
    help_vars = Variables()
    help_vars.Add(EnumVariable(
                'MSVC_UWP_APP',
                'Build a Universal Windows Platform (UWP) Application',
                '0',
                allowed_values=('0', '1')))
else:
    help_vars = None
env = Environment(tools=['default', 'msvc'], variables=help_vars, MSVC_VERSION='14.1')
# Print the ENV LIBPATH to stdout
print('env[ENV][LIBPATH]=%s' % env.get('ENV').get('LIBPATH'))
print('env[MSVC_VERSION]=%s' % env.get('MSVC_VERSION'))
print('env[ENV][VSCMD_ARG_app_plat]=%s' % env.get('ENV').get('VSCMD_ARG_app_plat'))
""")

    # Test setting MSVC_UWP_APP is '1' (True)
    test.run(arguments = "MSVC_UWP_APP=1")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is False) or (vclibstorerefs_path_present is False),
                message='VC Store LIBPATHs NOT present when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)

    # Test setting MSVC_UWP_APP is '0' (False)
    test.run(arguments = "MSVC_UWP_APP=0")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                    message='VC Store LIBPATHs NOT present when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)

    # Test not setting MSVC_UWP_APP
    test.run(arguments = "")
    (vclibstore_path_present, vclibstorerefs_path_present, msvc_version) = AreVCStoreLibPathsInLIBPATH(test.stdout())
    test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True),
                    message='VC Store LIBPATHs NOT present when MSVC_UWP_APP=1 (msvc_version=%s)' % msvc_version)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
