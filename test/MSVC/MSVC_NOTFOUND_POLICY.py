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
Test the MSVC_NOTFOUND_POLICY construction variable and functions.
"""

import TestSCons

test = TestSCons.TestSCons()
test.skip_if_not_msvc()

import textwrap

# Test construction variable with valid symbols
test.write('SConstruct', textwrap.dedent(
    """
    env_list = []
    DefaultEnvironment(tools=[])
    for symbol in ['Error', 'Exception', 'Warn', 'Warning', 'Ignore', 'Suppress']:
        for policy in [symbol, symbol.upper(), symbol.lower()]:
            env = Environment(MSVC_NOTFOUND_POLICY=policy, tools=['msvc'])
            env_list.append(env)
    """
))
test.run(arguments='-Q -s', stdout='')

# Test construction variable with invalid symbol
test.write('SConstruct', textwrap.dedent(
    """
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='Undefined', tools=['msvc'])
    """
))
test.run(arguments='-Q -s', status=2, stderr=None)
expect = "MSVCArgumentError: Value specified for MSVC_NOTFOUND_POLICY is not supported: 'Undefined'."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with global policy
test.write('SConstruct', textwrap.dedent(
    """
    from SCons.Tool.MSCommon import msvc_set_notfound_policy
    msvc_set_notfound_policy('Exception')
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', tools=['msvc'])
    """
))
test.run(arguments='-Q -s', status=2, stderr=None)
expect = "MSVCVersionNotFound: MSVC version '12.9' was not found."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with global policy and construction variable ignored
test.write('SConstruct', textwrap.dedent(
    """
    from SCons.Tool.MSCommon import msvc_set_notfound_policy
    msvc_set_notfound_policy('Exception')
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY=None, tools=['msvc'])
    """
))
test.run(arguments='-Q -s', status=2, stderr=None)
expect = "MSVCVersionNotFound: MSVC version '12.9' was not found."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with construction variable
test.write('SConstruct', textwrap.dedent(
    """
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='Error', tools=['msvc'])
    """
))
test.run(arguments='-Q -s', status=2, stderr=None)
expect = "MSVCVersionNotFound: MSVC version '12.9' was not found."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with global policy
test.write('SConstruct', textwrap.dedent(
    """
    from SCons.Tool.MSCommon import msvc_set_notfound_policy
    msvc_set_notfound_policy('Warning')
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', tools=['msvc'])
    """
))
test.run(arguments="-Q -s --warn=visual-c-missing .", status=0, stderr=None)
expect = "scons: warning: MSVC version '12.9' was not found."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with construction variable
test.write('SConstruct', textwrap.dedent(
    """
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='Warning', tools=['msvc'])
    """
))
test.run(arguments="-Q -s --warn=visual-c-missing .", status=0, stderr=None)
expect = "scons: warning: MSVC version '12.9' was not found."
test.must_contain_all(test.stderr(), expect)

# Test environment construction with construction variable (override global)
test.write('SConstruct', textwrap.dedent(
    """
    from SCons.Tool.MSCommon import msvc_set_notfound_policy
    msvc_set_notfound_policy('Exception')
    DefaultEnvironment(tools=[])
    env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='Ignore', tools=['msvc'])
    """
))
test.run(arguments='-Q -s', stdout='')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
