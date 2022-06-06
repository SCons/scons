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
Test scons with an invalid MSVC version when at least one MSVC is present.
"""

import sys

import TestSCons
import SCons.Tool.MSCommon.vc as msvc

test = TestSCons.TestSCons()

if sys.platform != 'win32':
    test.skip_test("Not win32 platform. Skipping test\n")

test.skip_if_not_msvc()

installed_msvc_versions = msvc.get_installed_vcs()
# MSVC guaranteed to be at least one version on the system or else
# skip_if_not_msvc() function would have skipped the test

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(MSVC_VERSION='12.9')
""")
test.run(arguments='-Q -s', stdout='')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='ignore')
""")
test.run(arguments='-Q -s', stdout='')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='warning')
""")
test.run(arguments='-Q -s', stdout='')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='error')
""")
test.run(arguments='-Q -s', status=2, stderr=r"^.*MSVCVersionNotFound.+", match=TestSCons.match_re_dotall)

test.write('SConstruct', """\
env = Environment(MSVC_VERSION='12.9', MSVC_NOTFOUND_POLICY='bad_value')
""")
test.run(arguments='-Q -s', status=2, stderr=r"^.* Value specified for MSVC_NOTFOUND_POLICY.+", match=TestSCons.match_re_dotall)


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
