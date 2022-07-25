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
Test the MSVC_TOOLSET_VERSION construction variable.
"""
import textwrap

from SCons.Tool.MSCommon.vc import get_installed_vcs_components
from SCons.Tool.MSCommon import msvc_toolset_versions

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

installed_versions = get_installed_vcs_components()

default_version = installed_versions[0]

GE_VS2017_versions = [v for v in installed_versions if v.msvc_vernum >= 14.1]
LT_VS2017_versions = [v for v in installed_versions if v.msvc_vernum < 14.1]
LT_VS2015_versions = [v for v in LT_VS2017_versions if v.msvc_vernum < 14.0]

if GE_VS2017_versions:
    # VS2017 and later for toolset argument

    for supported in GE_VS2017_versions:

        toolset_full_versions = msvc_toolset_versions(supported.msvc_version, full=True, sxs=False)
        toolset_full_version = toolset_full_versions[0] if toolset_full_versions else None

        toolset_sxs_versions = msvc_toolset_versions(supported.msvc_version, full=False, sxs=True)
        toolset_sxs_version = toolset_sxs_versions[0] if toolset_sxs_versions else None

        if toolset_full_version:

            # toolset version using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={0}, MSVC_TOOLSET_VERSION={1}, tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\{2}\\\\' not in lib_path:
                    raise RuntimeError("{1} not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version), repr(toolset_full_version), toolset_full_version)
            ))
            test.run(arguments='-Q -s', stdout='')

            # toolset version using script argument
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={0}, MSVC_SCRIPT_ARGS='-vcvars_ver={1}', tools=['msvc'])
                lib_path = env['ENV']['LIB']
                if '\\\\{1}\\\\' not in lib_path:
                    raise RuntimeError("'{1}' not found in lib path " + lib_path)
                """.format(repr(supported.msvc_version), toolset_full_version)
            ))
            test.run(arguments='-Q -s', stdout='')

        if toolset_sxs_version:

            # sxs toolset version using construction variable
            test.write('SConstruct', textwrap.dedent(
                """
                DefaultEnvironment(tools=[])
                env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
                """.format(repr(supported.msvc_version), repr(toolset_sxs_version))
            ))
            test.run(arguments='-Q -s', stdout='')

        # msvc_version as toolset version
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(supported.msvc_verstr))
        ))
        test.run(arguments='-Q -s', stdout='')

        # msvc_version as toolset version using script argument
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_ver={}', tools=['msvc'])
            """.format(repr(supported.msvc_version), supported.msvc_verstr)
        ))
        test.run(arguments='-Q -s', stdout='')

        # error toolset version and script argument
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_ver={}', tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(supported.msvc_verstr), supported.msvc_verstr)
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: multiple toolset version declarations: MSVC_TOOLSET_VERSION={} and MSVC_SCRIPT_ARGS='-vcvars_ver={}':".format(
            repr(supported.msvc_verstr), supported.msvc_verstr
        )
        test.must_contain_all(test.stderr(), expect)

        # msvc_toolset_version does not exist (hopefully)
        missing_toolset_version = supported.msvc_verstr + '9.99999'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(missing_toolset_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCToolsetVersionNotFound: MSVC_TOOLSET_VERSION {} not found for MSVC_VERSION {}:".format(
            repr(missing_toolset_version), repr(supported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # msvc_toolset_version is invalid (format)
        invalid_toolset_version = supported.msvc_verstr + '9.99999.99999'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(invalid_toolset_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) format is not supported:".format(
            repr(invalid_toolset_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # msvc_toolset_version is invalid (version greater than msvc version)
        invalid_toolset_vernum = round(supported.msvc_vernum + 0.1, 1)
        invalid_toolset_version = str(invalid_toolset_vernum)
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(invalid_toolset_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} > {} MSVC_VERSION:".format(
            repr(invalid_toolset_version), repr(invalid_toolset_version), repr(supported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # msvc_toolset_version is invalid (version less than 14.0)
        invalid_toolset_version = '12.0'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(invalid_toolset_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} < '14.0' VS2015:".format(
            repr(invalid_toolset_version), repr(invalid_toolset_version)
        )
        test.must_contain_all(test.stderr(), expect)

        # 14.0 toolset is invalid (toolset version != 14.0)
        invalid_toolset_version = '14.00.00001'
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(supported.msvc_version), repr(invalid_toolset_version))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} != '14.0':".format(
            repr(invalid_toolset_version), repr(invalid_toolset_version)
        )
        test.must_contain_all(test.stderr(), expect)

if LT_VS2017_versions:
    # VS2015 and earlier for toolset argument error

    for unsupported in LT_VS2017_versions:

        # must be VS2017 or later
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
            """.format(repr(unsupported.msvc_version), repr(unsupported.msvc_verstr))
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: MSVC_VERSION {} < '14.1' VS2017:".format(
            repr(unsupported.msvc_verstr), repr(unsupported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

if LT_VS2015_versions:
    # VS2013 and earlier for script argument error

    for unsupported in LT_VS2015_versions:

        # must be VS2015 or later for MSVC_SCRIPT_ARGS
        test.write('SConstruct', textwrap.dedent(
            """
            DefaultEnvironment(tools=[])
            env = Environment(MSVC_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_ver={}', tools=['msvc'])
            """.format(repr(unsupported.msvc_version), unsupported.msvc_verstr)
        ))
        test.run(arguments='-Q -s', status=2, stderr=None)
        expect = "MSVCArgumentError: MSVC_SCRIPT_ARGS ('-vcvars_ver={}') constraint violation: MSVC_VERSION {} < '14.0' VS2015:".format(
            unsupported.msvc_verstr, repr(unsupported.msvc_version)
        )
        test.must_contain_all(test.stderr(), expect)

test.pass_test()

