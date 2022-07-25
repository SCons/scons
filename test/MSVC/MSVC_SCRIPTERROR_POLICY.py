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
Test the MSVC_SCRIPTERROR_POLICY construction variable and functions.
"""

import TestSCons
import textwrap

from SCons.Tool.MSCommon.vc import get_installed_vcs_components

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

installed_versions = get_installed_vcs_components()

default_version = installed_versions[0]

# Test construction variable with valid symbols
test.write('SConstruct', textwrap.dedent(
    """
    env_list = []
    DefaultEnvironment(tools=[])
    for symbol in ['Error', 'Exception', 'Warn', 'Warning', 'Ignore', 'Suppress']:
        for policy in [symbol, symbol.upper(), symbol.lower()]:
            env = Environment(MSVC_SCRIPTERROR_POLICY=policy, tools=['msvc'])
            env_list.append(env)
    """
))
test.run(arguments='-Q -s', stdout='')

if default_version.msvc_vernum >= 14.1:
    # Need VS2017 or later for MSVC_SCRIPT_ARGS

    # Test environment construction with construction variable (invalid)
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], MSVC_SCRIPTERROR_POLICY='Undefined', tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCArgumentError: Value specified for MSVC_SCRIPTERROR_POLICY is not supported: 'Undefined'."
    test.must_contain_all(test.stderr(), expect)

    # Test environment construction with construction variable (override global)
    test.write('SConstruct', textwrap.dedent(
        """
        from SCons.Tool.MSCommon import msvc_set_scripterror_policy
        DefaultEnvironment(tools=[])
        msvc_set_scripterror_policy('Exception')
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], MSVC_SCRIPTERROR_POLICY='Ignore', tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', stdout='')

    # Test environment construction with global policy
    test.write('SConstruct', textwrap.dedent(
        """
        from SCons.Tool.MSCommon import msvc_set_scripterror_policy
        DefaultEnvironment(tools=[])
        msvc_set_scripterror_policy('Exception')
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCScriptExecutionError: vc script errors detected:"
    test.must_contain_all(test.stderr(), expect)

    # Test environment construction with global policy and construction variable ignored
    test.write('SConstruct', textwrap.dedent(
        """
        from SCons.Tool.MSCommon import msvc_set_scripterror_policy
        DefaultEnvironment(tools=[])
        msvc_set_scripterror_policy('Exception')
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], MSVC_SCRIPTERROR_POLICY=None, tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCScriptExecutionError: vc script errors detected:"
    test.must_contain_all(test.stderr(), expect)

    # Test environment construction with construction variable
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], MSVC_SCRIPTERROR_POLICY='Error', tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=2, stderr=None)
    expect = "MSVCScriptExecutionError: vc script errors detected:"
    test.must_contain_all(test.stderr(), expect)

    # Test environment construction with global policy
    test.write('SConstruct', textwrap.dedent(
        """
        from SCons.Tool.MSCommon import msvc_set_scripterror_policy
        DefaultEnvironment(tools=[])
        msvc_set_scripterror_policy('Warning')
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=0, stderr=None)
    expect = "scons: warning: vc script errors detected:"
    test.must_contain_all(test.stderr(), expect)

    # Test environment construction with construction variable
    test.write('SConstruct', textwrap.dedent(
        """
        DefaultEnvironment(tools=[])
        env = Environment(MSVC_SCRIPT_ARGS=['-thisdoesnotexist=somevalue'], MSVC_SCRIPTERROR_POLICY='Warning', tools=['msvc'])
        """
    ))
    test.run(arguments='-Q -s', status=0, stderr=None)
    expect = "scons: warning: vc script errors detected:"
    test.must_contain_all(test.stderr(), expect)

test.pass_test()

