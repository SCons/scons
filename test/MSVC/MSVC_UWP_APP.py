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

def AreVCStoreLibPathsInLIBPATH(output):
    lines = output.splitlines()
    for line in lines:
        if 'env[ENV][LIBPATH]=' in line:
            idx_eq = line.find('=')
            libpath = line[idx_eq + 1:]

    if not libpath:
        # Couldn't find the libpath in the output
        return (False, False)

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

    return (vclibstore_path_present, vclibstorerefs_path_present)

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
""")

# Test setting MSVC_UWP_APP is '1' (True)
test.run(arguments = "MSVC_UWP_APP=1")
(vclibstore_path_present, vclibstorerefs_path_present) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test((vclibstore_path_present is False) or (vclibstorerefs_path_present is False))

# Test setting MSVC_UWP_APP is '0' (False)
test.run(arguments = "MSVC_UWP_APP=0")
(vclibstore_path_present, vclibstorerefs_path_present) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True))

# Test not setting MSVC_UWP_APP
test.run(arguments = "")
(vclibstore_path_present, vclibstorerefs_path_present) = AreVCStoreLibPathsInLIBPATH(test.stdout())
test.fail_test((vclibstore_path_present is True) or (vclibstorerefs_path_present is True))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
