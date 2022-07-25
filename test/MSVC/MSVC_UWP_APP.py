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
Test the MSVC_UWP_APP construction variable.
"""
import textwrap
import re

from SCons.Tool.MSCommon.vc import get_installed_vcs_components
import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()


installed_versions = get_installed_vcs_components()

GE_VS2015_versions = [v for v in installed_versions if v.msvc_vernum >= 14.0]
LT_VS2015_versions = [v for v in installed_versions if v.msvc_vernum < 14.0]

# Look for the Store VC Lib paths in the LIBPATH:
# [VS install path]\VC\LIB\store[\arch] and
# [VS install path]\VC\LIB\store\references
# For example,
# C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\amd64
# C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\LIB\store\references

re_lib_eq2015_1 = re.compile(r'\\vc\\lib\\store\\references', re.IGNORECASE)
re_lib_eq2015_2 = re.compile(r'\\vc\\lib\\store', re.IGNORECASE)

re_lib_ge2017_1 = re.compile(r'\\lib\\x86\\store\\references', re.IGNORECASE)
re_lib_ge2017_2 = re.compile(r'\\lib\\x64\\store', re.IGNORECASE)


def check_libpath(msvc, active, output):

    def _check_libpath(msvc, output):
        outdict = {key.strip(): val.strip() for key, val in [line.split('|') for line in output.splitlines()]}
        platform = outdict.get('PLATFORM', '')
        libpath = outdict.get('LIBPATH', '')
        n_matches = 0
        if msvc.msvc_verstr == '14.0':
            for regex in (re_lib_eq2015_1, re_lib_eq2015_2):
                if regex.search(libpath):
                    n_matches += 1
            return n_matches >= 2, 'store', libpath
        elif platform == 'UWP':
            for regex in (re_lib_ge2017_1, re_lib_ge2017_2):
                if regex.search(libpath):
                    n_matches += 1
            return n_matches > 0, 'uwp', libpath
        return False, 'uwp', libpath

    found, kind, libpath = _check_libpath(msvc, output)

    failmsg = None

    if active and not found:
        failmsg = 'msvc version {} {} paths not found in lib path {}'.format(
            repr(msvc.msvc_version), repr(kind), repr(libpath)
        )
    elif not active and found:
        failmsg = 'msvc version {} {} paths found in lib path {}'.format(
            repr(msvc.msvc_version), repr(kind), repr(libpath)
        )

    return failmsg

if GE_VS2015_versions:
    # VS2015 and later for uwp/store argument

    for supported in GE_VS2015_versions:

        for msvc_uwp_app in (True, '1', False, '0', None):

            active = msvc_uwp_app in (True, '1')

            # uwp using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_UWP_APP={}, tools=['msvc'])
                print('LIBPATH|' + env['ENV'].get('LIBPATH', ''))
                print('PLATFORM|' + env['ENV'].get('VSCMD_ARG_app_plat',''))
                """.format(repr(supported.msvc_version), repr(msvc_uwp_app))
            ))
            test.run(arguments='-Q -s', stdout=None)
            failmsg = check_libpath(supported, active, test.stdout())
            if failmsg:
                test.fail_test(message=failmsg)

            if not active:
                continue

            # error construction variable and script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_UWP_APP={}, MSVC_SCRIPT_ARGS='store', tools=['msvc'])
                """.format(repr(supported.msvc_version), repr(msvc_uwp_app))
            ))
            test.run(arguments='-Q -s', status=2, stderr=None)
            if not test.stderr().strip().startswith("MSVCArgumentError: multiple uwp declarations:"):
                test.fail_test(message='Expected MSVCArgumentError')

        # uwp using script argument
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS='store', tools=['msvc'])
            print('LIBPATH|' + env['ENV'].get('LIBPATH', ''))
            print('PLATFORM|' + env['ENV'].get('VSCMD_ARG_app_plat',''))
            """.format(repr(supported.msvc_version))
        ))
        test.run(arguments='-Q -s', stdout=None)
        failmsg = check_libpath(supported, True, test.stdout())
        if failmsg:
            test.fail_test(message=failmsg)

if LT_VS2015_versions:
    # VS2013 and earlier for uwp/store error

    for unsupported in LT_VS2015_versions:

        for msvc_uwp_app in (True, '1', False, '0', None):

            active = msvc_uwp_app in (True, '1')

            # uwp using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={0}, MSVC_UWP_APP={1}, tools=['msvc'])
                """.format(repr(unsupported.msvc_version), repr(msvc_uwp_app))
            ))
            if not active:
                test.run(arguments='-Q -s', stdout=None)
            else:
                test.run(arguments='-Q -s', status=2, stderr=None)
                expect = 'MSVCArgumentError: MSVC_UWP_APP ({}) constraint violation:'.format(repr(msvc_uwp_app))
                if not test.stderr().strip().startswith(expect):
                    test.fail_test(message='Expected MSVCArgumentError')

test.pass_test()

