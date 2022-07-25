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
Test SCONS_CACHE_MSVC_FORCE_DEFAULTS system environment variable.
"""

import textwrap

from SCons.Tool.MSCommon.vc import get_installed_vcs_components
import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()

installed_versions = get_installed_vcs_components()

default_version = installed_versions[0]

if default_version.msvc_vernum >= 14.0:
    # VS2015 and later

    # force SDK version and toolset version as msvc batch file arguments
    test.write('SConstruct', textwrap.dedent(
        """
        import os
        import json

        cache_file = 'MSCACHE.json'

        os.environ['SCONS_CACHE_MSVC_CONFIG']=cache_file
        os.environ['SCONS_CACHE_MSVC_FORCE_DEFAULTS']='1'

        DefaultEnvironment(tools=[])
        env = Environment(tools=['msvc'])

        envcache_keys = []
        with open(cache_file, 'r') as file:
            envcache_list = json.load(file)
            envcache_keys = [tuple(d['key']) for d in envcache_list]

        if envcache_keys:
            # key = (script, arguments)
            print("SCRIPT_ARGS: {}".format(envcache_keys[0][-1]))
        """
    ))
    test.run(arguments = "-Q -s", status=0, stdout=None)

    cache_arg = test.stdout().strip()

    if default_version.msvc_verstr == '14.0':
        # VS2015: target_arch msvc_sdk_version
        expect = r'^SCRIPT_ARGS: .* [0-9.]+$'
    else:
        # VS2017+ msvc_sdk_version msvc_toolset_version
        expect = r'^SCRIPT_ARGS: [0-9.]+ -vcvars_ver=[0-9.]+$'

    test.must_contain_all(cache_arg, expect, find=TestSCons.match_re)

