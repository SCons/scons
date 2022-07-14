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
Test batch file argument functions for Microsoft Visual C/C++.
"""

import unittest

import SCons.Environment

from SCons.Tool.MSCommon import vc

from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC import Util
from SCons.Tool.MSCommon.MSVC import ScriptArguments
from SCons.Tool.MSCommon.MSVC.Exceptions import MSVCInternalError

def Environment(**kwargs):
    tools_key = 'tools'
    if tools_key not in kwargs:
        tools = []
    else:
        tools = kwargs[tools_key]
        del kwargs[tools_key]
    return SCons.Environment.Base(tools=tools, **kwargs)

class ScriptArgumentsTests(unittest.TestCase):

    # all versions
    _all_versions_list = []

    # installed versions
    _vcdir_list = []

    @classmethod
    def setUpClass(cls):
        for vcver in Config.MSVC_VERSION_SUFFIX.keys():
            version_def = Util.msvc_version_components(vcver)
            vc_dir = vc.find_vc_pdir(None, vcver)
            t = (version_def, vc_dir)
            cls._all_versions_list.append(t)
            if vc_dir:
                cls._vcdir_list.append(t)

    def setUp(self):
        self.all_versions_list = self.__class__._all_versions_list
        self.vcdir_list = self.__class__._vcdir_list

    def test_verify(self):
        _MSVC_SDK_VERSIONS = Config.MSVC_SDK_VERSIONS
        msvc_sdk_versions = set(Config.MSVC_SDK_VERSIONS)
        msvc_sdk_versions.add('99.0')
        Config.MSVC_SDK_VERSIONS = msvc_sdk_versions
        with self.assertRaises(MSVCInternalError):
            ScriptArguments.verify()
        Config.MSVC_SDK_VERSIONS = _MSVC_SDK_VERSIONS

    def test_msvc_script_arguments_defaults(self):
        env = Environment()
        func = ScriptArguments.msvc_script_arguments
        # disable forcing sdk and toolset versions as arguments
        force = ScriptArguments.msvc_force_default_arguments(force=False)
        for version_def, vc_dir in self.vcdir_list:
            for arg in ('', 'arch'):
                scriptargs = func(env, version_def.msvc_version, vc_dir, arg)
                self.assertTrue(scriptargs == arg, "{}({},{}) != {} [force=False]".format(
                    func.__name__, repr(version_def.msvc_version), repr(arg), repr(scriptargs)
                ))
        # enable forcing sdk and toolset versions as arguments
        force = ScriptArguments.msvc_force_default_arguments(force=True)
        for version_def, vc_dir in self.vcdir_list:
            scriptargs = func(env, version_def.msvc_version, vc_dir, '')
            for arg in ('', 'arch'):
                scriptargs = func(env, version_def.msvc_version, vc_dir, arg)
                if version_def.msvc_vernum >= 14.0:
                    if arg and scriptargs.startswith(arg):
                        testargs = scriptargs[len(arg):].lstrip()
                    else:
                        testargs = scriptargs
                    self.assertTrue(testargs, "{}({},{}) is empty [force=True]".format(
                        func.__name__, repr(version_def.msvc_version), repr(arg)
                    ))
                else:
                    self.assertTrue(scriptargs == arg, "{}({},{}) != {} [force=True]".format(
                        func.__name__, repr(version_def.msvc_version), repr(arg), repr(scriptargs)
                    ))
        # restore forcing sdk and toolset versions as arguments
        ScriptArguments.msvc_force_default_arguments(force=force)

    def test_msvc_toolset_versions_internal(self):
        func = ScriptArguments._msvc_toolset_versions_internal
        for version_def, vc_dir in self.vcdir_list:
            for full in (True, False):
                for sxs in (True, False):
                    toolset_versions = func(version_def.msvc_version, vc_dir, full=full, sxs=sxs)
                    if version_def.msvc_vernum < 14.1:
                        self.assertTrue(toolset_versions is None, "{}({},{},full={},sxs={}) is not None ({})".format(
                            func.__name__, repr(version_def.msvc_version), repr(vc_dir), repr(full), repr(sxs),
                            repr(toolset_versions)
                        ))
                    elif full:
                        self.assertTrue(len(toolset_versions), "{}({},{},full={},sxs={}) is empty".format(
                            func.__name__, repr(version_def.msvc_version), repr(vc_dir), repr(full), repr(sxs)
                        ))
                    elif sxs:
                        # sxs list can be empty
                        pass
                    else:
                        self.assertFalse(len(toolset_versions), "{}({},{},full={},sxs={}) is not empty".format(
                            func.__name__, repr(version_def.msvc_version), repr(vc_dir), repr(full), repr(sxs)
                        ))

    def test_msvc_toolset_internal(self):
        func = ScriptArguments._msvc_toolset_internal
        for version_def, vc_dir in self.vcdir_list:
            toolset_versions = ScriptArguments._msvc_toolset_versions_internal(version_def.msvc_version, vc_dir, full=True, sxs=True)
            if not toolset_versions:
                continue
            for toolset_version in toolset_versions:
                _ = func(version_def.msvc_version, toolset_version, vc_dir)

    def test_reset(self):
        ScriptArguments.reset()
        self.assertTrue(ScriptArguments._toolset_have140_cache is None, "ScriptArguments._toolset_have140_cache was not reset")
        self.assertFalse(ScriptArguments._toolset_version_cache, "ScriptArguments._toolset_version_cache was not reset")
        self.assertFalse(ScriptArguments._toolset_default_cache, "ScriptArguments._toolset_default_cache was not reset")

if __name__ == "__main__":
    unittest.main()

