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
Test the MSVC_SDK_VERSION construction variable.
"""
import textwrap

from SCons.Tool.MSCommon.vc import get_installed_vcs_components
from SCons.Tool.MSCommon import msvc_sdk_versions
from SCons.Tool.MSCommon import msvc_toolset_versions
import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()


installed_versions = get_installed_vcs_components()

default_version = installed_versions[0]

GE_VS2015_versions = [v for v in installed_versions if v.msvc_vernum >= 14.0]
LT_VS2015_versions = [v for v in installed_versions if v.msvc_vernum < 14.0]

default_sdk_versions_uwp = msvc_sdk_versions(version=None, msvc_uwp_app=True)
default_sdk_versions_def = msvc_sdk_versions(version=None, msvc_uwp_app=False)

have_140 = any([v.msvc_verstr == '14.0' for v in GE_VS2015_versions])

def version_major(version):
    components = version.split('.')
    if len(components) >= 2:
        return components[0] + '.' + components[1][0]
    if len(components) == 1:
        return components[0] + '.0'
    return version

def version_major_list(version_list):
    versions = []
    seen_major = set()
    for version in version_list:
        major = version_major(version)
        if major in seen_major:
            continue
        versions.append(version)
        seen_major.add(major)
    return versions

if GE_VS2015_versions:

    for supported in GE_VS2015_versions:

        sdk_versions_uwp = msvc_sdk_versions(version=supported.msvc_version, msvc_uwp_app=True)
        sdk_versions_def = msvc_sdk_versions(version=supported.msvc_version, msvc_uwp_app=False)

        # find sdk version for each major SDK
        sdk_versions = version_major_list(sdk_versions_def)

        for sdk_version in sdk_versions:

            # sdk version construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={0}, MSVC_SDK_VERSION={1}, tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\{2}\\\\' not in lib_path:
                    raise RuntimeError("{1} not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version), repr(sdk_version), sdk_version)
            ))
            test.run(arguments='-Q -s', stdout='')

            # sdk version script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={0}, MSVC_SCRIPT_ARGS={1}, tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\{2}\\\\' not in lib_path:
                    raise RuntimeError("{1} not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version), repr(sdk_version), sdk_version)
            ))
            test.run(arguments='-Q -s', stdout='')

            # sdk version construction variable and script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION={}, MSVC_SCRIPT_ARGS={}, tools=['msvc'])
                """.format(repr(supported.msvc_version), repr(sdk_version), repr(sdk_version))
            ))
            test.run(arguments='-Q -s', status=2, stderr=None)
            expect = "MSVCArgumentError: multiple sdk version declarations: MSVC_SDK_VERSION={} and MSVC_SCRIPT_ARGS={}:".format(
                repr(sdk_version), repr(sdk_version)
            )
            test.must_contain_all(test.stderr(), expect)

        # sdk version is not supported
        invalid_sdk_version = '9.1'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(invalid_sdk_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_SDK_VERSION ({}) is not supported:".format(
            repr(invalid_sdk_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # sdk version not found
        missing_sdk_version = '10.0.12345.6'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(missing_sdk_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCSDKVersionNotFound: MSVC_SDK_VERSION {} not found for platform type 'Desktop':".format(
            repr(missing_sdk_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # platform contraints: 8.1 and UWP
        if '8.1' in sdk_versions:

            if supported.msvc_vernum > 14.0:

                toolset_full_versions = msvc_toolset_versions(supported.msvc_version, full=True, sxs=False)
                toolset_versions = version_major_list(toolset_full_versions)

                # toolset msvc_version != current msvc_version and toolset msvc_version != 14.0
                toolset_candidates = [v for v in toolset_versions if version_major(v) not in (supported.msvc_verstr, '14.0')]
                toolset_version = toolset_candidates[0] if toolset_candidates else None

                # sdk version 8.1, UWP, and msvc_verson > VS2015
                test.write('SConstruct', textwrap.dedent(
                    """
                    DefaultEnvironment(tools=[])
                    env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION='8.1', MSVC_UWP_APP=True, tools=['msvc'])
                    """.format(repr(supported.msvc_version))
                ))
                test.run(arguments='-Q -s', status=2, stderr=None)
                expect = "MSVCArgumentError: MSVC_SDK_VERSION ('8.1') and platform type ('UWP') constraint violation: MSVC_VERSION {} > '14.0' VS2015:".format(
                    repr(supported.msvc_version)
                )
                test.must_contain_all(test.stderr(), expect)

                if toolset_version:

                    # sdk version 8.1, UWP, and msvc_toolset_verson > VS2015
                    test.write('SConstruct', textwrap.dedent(
                        """
                        DefaultEnvironment(tools=[])
                        env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, MSVC_SDK_VERSION='8.1', MSVC_UWP_APP=True, tools=['msvc'])
                        """.format(repr(supported.msvc_version), repr(toolset_version))
                    ))
                    test.run(arguments='-Q -s', status=2, stderr=None)
                    expect = "MSVCArgumentError: MSVC_SDK_VERSION ('8.1') and platform type ('UWP') constraint violation: toolset version {} > '14.0' VS2015:".format(
                        repr(toolset_version)
                    )
                    test.must_contain_all(test.stderr(), expect)

                if have_140:

                    # sdk version 8.1, UWP, and msvc_toolset_version > VS2015
                    test.write('SConstruct', textwrap.dedent(
                        """
                        DefaultEnvironment(tools=[])
                        env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION='8.1', MSVC_TOOLSET_VERSION='14.0', MSVC_UWP_APP=True, tools=['msvc'])
                        """.format(repr(supported.msvc_version))
                    ))
                    test.run(arguments='-Q -s', stdout='')

            elif supported.msvc_vernum == 14.0:

                # sdk version 8.1, UWP, and msvc_verson == VS2015
                test.write('SConstruct', textwrap.dedent(
                    """
                    DefaultEnvironment(tools=[])
                    env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION='8.1', MSVC_UWP_APP=True, tools=['msvc'])
                    """.format(repr(supported.msvc_version))
                ))
                test.run(arguments='-Q -s', stdout='')

if LT_VS2015_versions:

    for unsupported in LT_VS2015_versions:
        # must be VS2015 or later

        sdk_version = default_sdk_versions_def[0] if default_sdk_versions_def else '8.1'

        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SDK_VERSION={}, tools=['msvc'])
            """.format(repr(unsupported.msvc_version), repr(sdk_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_SDK_VERSION ({}) constraint violation: MSVC_VERSION {} < '14.0' VS2015:".format(
            repr(sdk_version), repr(unsupported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS={}, tools=['msvc'])
            """.format(repr(unsupported.msvc_version), repr(sdk_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_SCRIPT_ARGS ({}) constraint violation: MSVC_VERSION {} < '14.0' VS2015:".format(
            repr(sdk_version), repr(unsupported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

test.pass_test()

