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

import sys
import TestSCons

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test("Not win32 platform. Skipping test\n")

test.skip_if_not_msvc()

import textwrap
from collections import namedtuple

from SCons.Tool.MSCommon.vc import (
    get_installed_vcs,
    get_msvc_version_numeric,
)

MSVC_VERSION = namedtuple('MSVCVersion', [
    'msvc_version',
    'msvc_verstr',
    'msvc_vernum',
])

def process_version(msvc_version):
    msvc_verstr = get_msvc_version_numeric(msvc_version)
    msvc_vernum = float(msvc_verstr)
    return MSVC_VERSION(msvc_version, msvc_verstr, msvc_vernum)

installed_versions = [process_version(msvc_version) for msvc_version in get_installed_vcs()]

default = installed_versions[0]

if default.msvc_vernum >= 14.1:
    # VS2017 and later for toolset argument

    # msvc_version as toolset version
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(default.msvc_verstr))
    ))
    test.run(arguments='-Q -s', stdout='')

    # msvc_version as toolset version using script argument
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_SCRIPT_ARGS='-vcvars_ver={}', tools=['msvc'])
        """.format(default.msvc_verstr)
    ))
    test.run(arguments='-Q -s', stdout='')

    # error toolset version and script argument
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, MSVC_SCRIPT_ARGS='-vcvars_ver={}', tools=['msvc'])
        """.format(repr(default.msvc_verstr), default.msvc_verstr)
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: multiple toolset version declarations: MSVC_TOOLSET_VERSION={} and MSVC_SCRIPT_ARGS='-vcvars_ver={}':".format(
        repr(default.msvc_verstr), default.msvc_verstr
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

    # msvc_toolset_version does not exist (hopefully)
    missing_toolset_version = default.msvc_verstr + '9.99999'
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(missing_toolset_version))
    ))
    expect = r"^.*MSVCToolsetVersionNotFound: MSVC_TOOLSET_VERSION {} not found for MSVC_VERSION {}.+".format(
        repr(missing_toolset_version), repr(default.msvc_version)
    )
    test.run(arguments='-Q -s', status=2, stderr=expect, match=TestSCons.match_re_dotall)

    # msvc_toolset_version is invalid (format)
    invalid_toolset_version = default.msvc_verstr + '9.99999.99999'
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(invalid_toolset_version))
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) format is not supported:".format(
        repr(invalid_toolset_version)
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

    # msvc_toolset_version is invalid (version greater than msvc version)
    invalid_toolset_vernum = default.msvc_vernum + 0.1
    invalid_toolset_version = str(invalid_toolset_vernum)
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(invalid_toolset_version))
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} > {} MSVC_VERSION:".format(
        repr(invalid_toolset_version), repr(invalid_toolset_version), repr(default.msvc_version)
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

    # msvc_toolset_version is invalid (version less than 14.0)
    invalid_toolset_version = '12.0'
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(invalid_toolset_version))
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} < '14.0' VS2015:".format(
        repr(invalid_toolset_version), repr(invalid_toolset_version)
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

    # 14.0 toolset is invalid (toolset version != 14.0)
    invalid_toolset_version = '14.00.00001'
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(invalid_toolset_version))
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} != '14.0':".format(
        repr(invalid_toolset_version), repr(invalid_toolset_version)
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

unsupported_versions = [v for v in installed_versions if v.msvc_vernum < 14.1]
if unsupported_versions:
    # VS2015 and earlier for toolset argument error

    unsupported = unsupported_versions[0]

    # must be VS2017 or later
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_VERSION={}, MSVC_TOOLSET_VERSION={}, tools=['msvc'])
        """.format(repr(unsupported.msvc_version), repr(unsupported.msvc_verstr))
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: MSVC_TOOLSET_VERSION ({}) constraint violation: MSVC_VERSION {} < '14.1' VS2017:".format(
        repr(unsupported.msvc_version), repr(unsupported.msvc_version)
    )
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

unsupported_versions = [v for v in installed_versions if v.msvc_vernum < 14.0]
if unsupported_versions:
    # VS2013 and earlier for script argument error

    unsupported = unsupported_versions[0]

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
    test.fail_test(test.stderr().split('\n')[0].strip() != expect)

test.pass_test()

