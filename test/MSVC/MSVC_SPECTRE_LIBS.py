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
Test the MSVC_SPECTRE_LIBS construction variable.
"""

import TestSCons
import textwrap

from SCons.Tool.MSCommon.vc import get_installed_vcs_components
from SCons.Tool.MSCommon import msvc_toolset_versions_spectre

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

installed_versions = get_installed_vcs_components()

GE_VS2017_versions = [v for v in installed_versions if v.msvc_vernum >= 14.1]
LT_VS2017_versions = [v for v in installed_versions if v.msvc_vernum < 14.1]

if GE_VS2017_versions:
    # VS2017 and later for toolset argument

    for supported in GE_VS2017_versions:

        spectre_toolset_versions = msvc_toolset_versions_spectre(supported.msvc_version)
        spectre_toolset_version = spectre_toolset_versions[0] if spectre_toolset_versions else None

        if spectre_toolset_version:

            # spectre libs using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS=True, tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\lib\\\\spectre\\\\' not in lib_path.lower():
                    raise RuntimeError("'spectre' not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version))
            ))
            test.run(arguments='-Q -s', stdout='')

            # spectre libs using script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_spectre_libs=spectre', tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\lib\\\\spectre\\\\' not in lib_path.lower():
                    raise RuntimeError("'spectre' not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version))
            ))
            test.run(arguments='-Q -s', stdout='')

            # error construction variable and script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS=True, MSVC_SCRIPT_ARGS='-vcvars_spectre_libs=spectre', tools=['msvc'])
                """.format(repr(supported.msvc_version))
            ))
            test.run(arguments='-Q -s', status=2, stderr=None)
            expect = "MSVCArgumentError: multiple spectre declarations: MSVC_SPECTRE_LIBS=True and MSVC_SCRIPT_ARGS='-vcvars_spectre_libs=spectre':"
            test.must_contain_all(test.stderr(), expect)

        else:

            # spectre libs using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS=True, tools=['msvc'])
                """.format(repr(supported.msvc_version))
            ))
            test.run(arguments='-Q -s', status=2, stderr=None)
            if not test.stderr().strip().startswith('MSVCSpectreLibsNotFound: Spectre libraries not found'):
                test.fail_test()

            # spectre libs using script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_spectre_libs=spectre', MSVC_SCRIPTERROR_POLICY='error', tools=['msvc'])
                """.format(repr(supported.msvc_version))
            ))
            test.run(arguments='-Q -s', status=2, stderr=None)
            if not test.stderr().strip().startswith('MSVCScriptExecutionError: vc script errors detected:'):
                test.fail_test()

        # spectre libs using construction variable
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS=False, tools=['msvc'])
            lib_path = env['ENV']['LIB']
            if '\\\\lib\\\\spectre\\\\' in lib_path.lower():
                raise RuntimeError("'spectre' found in lib path " + lib_path)
            """.format(repr(supported.msvc_version))
        ))
        test.run(arguments='-Q -s', stdout='')

if LT_VS2017_versions:
    # VS2015 and earlier for toolset argument error

    for unsupported in LT_VS2017_versions:

        # must be VS2017 or later
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS=True, tools=['msvc'])
            """.format(repr(unsupported.msvc_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        if not test.stderr().strip().startswith('MSVCArgumentError: MSVC_SPECTRE_LIBS (True) constraint violation:'):
            test.fail_test()

        for disabled in (False, None):

            # ignore
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SPECTRE_LIBS={}, tools=['msvc'])
                """.format(repr(unsupported.msvc_version), disabled)
            ))
            test.run(arguments='-Q -s', stdout='')

test.pass_test()

