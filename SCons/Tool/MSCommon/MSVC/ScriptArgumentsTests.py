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
from SCons.Tool.MSCommon import vcTests

from SCons.Tool.MSCommon.MSVC import Config
from SCons.Tool.MSCommon.MSVC import Util
from SCons.Tool.MSCommon.MSVC import WinSDK
from SCons.Tool.MSCommon.MSVC import ScriptArguments

from SCons.Tool.MSCommon.MSVC.Exceptions import (
    MSVCInternalError,
    MSVCArgumentError,
    MSVCToolsetVersionNotFound,
    MSVCSDKVersionNotFound,
    MSVCSpectreLibsNotFound,
)

def Environment(**kwargs):
    tools_key = 'tools'
    if tools_key not in kwargs:
        tools = []
    else:
        tools = kwargs[tools_key]
        del kwargs[tools_key]
    return SCons.Environment.Base(tools=tools, **kwargs)

class Data:

    # all versions
    ALL_VERSIONS_PAIRS = []

    # installed versions
    INSTALLED_VERSIONS_PAIRS = []

    for vcver in Config.MSVC_VERSION_SUFFIX.keys():
        version_def = Util.msvc_version_components(vcver)
        vc_dir = vc.find_vc_pdir(None, vcver)
        t = (version_def, vc_dir)
        ALL_VERSIONS_PAIRS.append(t)
        if vc_dir:
            INSTALLED_VERSIONS_PAIRS.append(t)

    HAVE_MSVC = True if len(INSTALLED_VERSIONS_PAIRS) else False

    @classmethod
    def msvc_toolset_notfound_dict(cls):
        return vcTests.Data.msvc_toolset_notfound_dict()

    @classmethod
    def msvc_toolset_notfound_version(cls, msvc_version):
        d = cls.msvc_toolset_notfound_dict()
        notfound_versions = d.get(msvc_version,[])
        if not notfound_versions:
            notfound_version = msvc_version + '0.00001'
        else:
            notfound_version = notfound_versions[0]
        return notfound_version

    @classmethod
    def _msvc_sdk_notfound_list(cls, sdk_seen, sdk_list):
        new_sdk_list = []
        if not sdk_list:
            return new_sdk_list
        for sdk_version in sdk_list:
            version = sdk_version
            comps = version.split('.')
            if len(comps) != 4:
                continue
            nloop = 0
            while nloop < 10:
                ival = int(comps[-2])
                if ival == 0:
                    ival = 1000000
                ival -= 1
                version = '{}.{}.{:05d}.{}'.format(comps[0], comps[1], ival, comps[-1])
                if version not in sdk_seen:
                    new_sdk_list.append(version)
                    break
                nloop += 1
        return new_sdk_list

    _msvc_sdk_notfound_dict = {True: None, False: None}

    @classmethod
    def msvc_sdk_notfound_dict(cls, msvc_uwp_app=False):
        if cls._msvc_sdk_notfound_dict[msvc_uwp_app] is None:
            sdk_seen = set()
            sdk_dict = {}
            for symbol in Config.MSVC_VERSION_SUFFIX.keys():
                sdk_list = WinSDK.get_msvc_sdk_version_list(symbol, msvc_uwp_app=msvc_uwp_app)
                if not sdk_list:
                    continue
                sdk_seen.update(sdk_list)
                sdk_dict[symbol] = sdk_list
            for key, val in sdk_dict.items():
                sdk_dict[key] = cls._msvc_sdk_notfound_list(sdk_seen, val)
            cls._msvc_sdk_notfound_dict[msvc_uwp_app] = sdk_dict
        return cls._msvc_sdk_notfound_dict[msvc_uwp_app]

    @classmethod
    def msvc_sdk_notfound_version(cls, msvc_version):
        d = cls.msvc_sdk_notfound_dict()
        notfound_versions = d.get(msvc_version,[])
        if not notfound_versions:
            notfound_version = '10.0.00000.1'
        else:
            notfound_version = notfound_versions[0]
        return notfound_version

class Patch:

    class Config:

        class MSVC_SDK_VERSIONS:

            MSVC_SDK_VERSIONS = Config.MSVC_SDK_VERSIONS

            @classmethod
            def enable_copy(cls):
                hook = set(cls.MSVC_SDK_VERSIONS)
                Config.MSVC_SDK_VERSIONS = hook
                return hook

            @classmethod
            def restore(cls):
                Config.MSVC_SDK_VERSIONS = cls.MSVC_SDK_VERSIONS

class ScriptArgumentsTests(unittest.TestCase):

    def test_verify(self):
        MSVC_SDK_VERSIONS = Patch.Config.MSVC_SDK_VERSIONS.enable_copy()
        MSVC_SDK_VERSIONS.add('99.0')
        with self.assertRaises(MSVCInternalError):
            ScriptArguments.verify()
        Patch.Config.MSVC_SDK_VERSIONS.restore()

    def test_msvc_script_arguments_defaults(self):
        func = ScriptArguments.msvc_script_arguments
        env = Environment()
        # disable forcing sdk and toolset versions as arguments
        force = ScriptArguments.msvc_force_default_arguments(force=False)
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
            for arg in ('', 'arch'):
                scriptargs = func(env, version_def.msvc_version, vc_dir, arg)
                self.assertTrue(scriptargs == arg, "{}({},{}) != {} [force=False]".format(
                    func.__name__, repr(version_def.msvc_version), repr(arg), repr(scriptargs)
                ))
        # enable forcing sdk and toolset versions as arguments
        ScriptArguments.msvc_force_default_arguments(force=True)
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
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
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
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
        if not Data.HAVE_MSVC:
            return
        func = ScriptArguments._msvc_toolset_internal
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
            toolset_versions = ScriptArguments._msvc_toolset_versions_internal(version_def.msvc_version, vc_dir, full=True, sxs=True)
            if not toolset_versions:
                continue
            for toolset_version in toolset_versions:
                _ = func(version_def.msvc_version, toolset_version, vc_dir)

    def run_msvc_script_args_none(self):
        func = ScriptArguments.msvc_script_arguments
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
            for kwargs in [
                {'MSVC_SCRIPT_ARGS': None},
                {'MSVC_SCRIPT_ARGS': None, 'MSVC_UWP_APP': None},
                {'MSVC_SCRIPT_ARGS': None, 'MSVC_TOOLSET_VERSION': None},
                {'MSVC_SCRIPT_ARGS': None, 'MSVC_SDK_VERSION': None},
                {'MSVC_SCRIPT_ARGS': None, 'MSVC_SPECTRE_LIBS': None},
            ]:
                env = Environment(**kwargs)
                _ = func(env, version_def.msvc_version, vc_dir, '')

    def run_msvc_script_args(self):
        func = ScriptArguments.msvc_script_arguments
        for version_def, vc_dir in Data.INSTALLED_VERSIONS_PAIRS:
            if version_def.msvc_vernum >= 14.1:
                # VS2017 and later

                # should not raise exception (argument not validated)
                env = Environment(MSVC_SCRIPT_ARGS='undefinedsymbol')
                _ = func(env, version_def.msvc_version, vc_dir, '')

                for kwargs in [
                    {'MSVC_UWP_APP': False, 'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_UWP_APP': '0',   'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_UWP_APP': False, 'MSVC_SCRIPT_ARGS': 'store'},
                    {'MSVC_UWP_APP': '0',   'MSVC_SCRIPT_ARGS': 'store'},
                    {'MSVC_SPECTRE_LIBS': False, 'MSVC_SCRIPT_ARGS': '-vcvars_spectre_libs=spectre'},
                    {'MSVC_SPECTRE_LIBS': 'True', 'MSVC_SCRIPT_ARGS': '-vcvars_spectre_libs=spectre'}, # not boolean ignored
                ]:
                    env = Environment(**kwargs)
                    _ = func(env, version_def.msvc_version, vc_dir, '')

                for msvc_uwp_app in (True, False):

                    sdk_list = WinSDK.get_msvc_sdk_version_list(version_def.msvc_version, msvc_uwp_app=msvc_uwp_app)
                    for sdk_version in sdk_list:

                        if sdk_version == '8.1' and msvc_uwp_app:

                            for exc, kwargs in [
                                (False, {'MSVC_SCRIPT_ARGS': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app}),
                                (True,  {'MSVC_SDK_VERSION': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app}),
                            ]:
                                env = Environment(**kwargs)
                                if exc:
                                    with self.assertRaises(MSVCArgumentError):
                                        _ = func(env, version_def.msvc_version, vc_dir, '')
                                else:
                                    _ = func(env, version_def.msvc_version, vc_dir, '')

                        else:

                            for kwargs in [
                                {'MSVC_SCRIPT_ARGS': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app},
                                {'MSVC_SDK_VERSION': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app},
                            ]:
                                env = Environment(**kwargs)
                                _ = func(env, version_def.msvc_version, vc_dir, '')

                for kwargs in [
                    {'MSVC_SCRIPT_ARGS': '-vcvars_ver={}'.format(version_def.msvc_verstr)},
                    {'MSVC_TOOLSET_VERSION': version_def.msvc_verstr},
                ]:
                    env = Environment(**kwargs)
                    _ = func(env, version_def.msvc_version, vc_dir, '')

                msvc_toolset_notfound_version = Data.msvc_toolset_notfound_version(version_def.msvc_version)

                for kwargs in [
                    {'MSVC_TOOLSET_VERSION': msvc_toolset_notfound_version},
                ]:
                    env = Environment(**kwargs)
                    with self.assertRaises(MSVCToolsetVersionNotFound):
                        _ = func(env, version_def.msvc_version, vc_dir, '')

                msvc_sdk_notfound_version = Data.msvc_sdk_notfound_version(version_def.msvc_version)

                for kwargs in [
                    {'MSVC_SDK_VERSION': msvc_sdk_notfound_version},
                ]:
                    env = Environment(**kwargs)
                    with self.assertRaises(MSVCSDKVersionNotFound):
                        _ = func(env, version_def.msvc_version, vc_dir, '')

                for kwargs, exc_t in [
                    ({'MSVC_UWP_APP': True,
                      'MSVC_SCRIPT_ARGS': 'uwp'
                      }, (MSVCArgumentError, ),
                     ),
                    ({'MSVC_UWP_APP': True,
                      'MSVC_SCRIPT_ARGS': 'uwp undefined store'
                      }, (MSVCArgumentError, ),
                     ),
                    ({'MSVC_TOOLSET_VERSION': version_def.msvc_verstr,
                      'MSVC_SCRIPT_ARGS': "-vcvars_ver={}".format(version_def.msvc_verstr)
                      },
                     (MSVCArgumentError, ),
                     ),
                    ({'MSVC_TOOLSET_VERSION': version_def.msvc_verstr,
                      'MSVC_SCRIPT_ARGS': "-vcvars_ver={}".format(version_def.msvc_verstr)
                      },
                     (MSVCArgumentError, ),
                     ),
                    ({'MSVC_TOOLSET_VERSION': version_def.msvc_verstr,
                      'MSVC_SCRIPT_ARGS': "-vcvars_ver={0} undefined -vcvars_ver={0}".format(version_def.msvc_verstr)
                      },
                     (MSVCArgumentError, ),
                     ),
                    ({'MSVC_SDK_VERSION': '9.1',
                      },
                     (MSVCArgumentError, ),
                     ),
                    ({'MSVC_SPECTRE_LIBS': True,
                      'MSVC_SCRIPT_ARGS': '-vcvars_spectre_libs=spectre undefined -vcvars_spectre_libs=spectre'
                      },
                     (MSVCArgumentError, MSVCSpectreLibsNotFound),
                     ),
                    ({'MSVC_SPECTRE_LIBS': True,
                      'MSVC_SCRIPT_ARGS': '-vcvars_spectre_libs=spectre'
                      },
                     (MSVCArgumentError, MSVCSpectreLibsNotFound),
                     ),
                    ({'MSVC_SPECTRE_LIBS': True,
                      'MSVC_UWP_APP': True,
                      },
                     (MSVCArgumentError, MSVCSpectreLibsNotFound),
                     ),
                    ({'MSVC_SPECTRE_LIBS': True,
                      'MSVC_TOOLSET_VERSION': '14.00.00000',
                      },
                     (MSVCArgumentError, MSVCSpectreLibsNotFound, MSVCToolsetVersionNotFound),
                     ),
                ]:
                    env = Environment(**kwargs)
                    with self.assertRaises(exc_t):
                        _ = func(env, version_def.msvc_version, vc_dir, '')

            elif version_def.msvc_verstr == '14.0':
                # VS2015: MSVC_SDK_VERSION and MSVC_UWP_APP

                env = Environment(MSVC_SCRIPT_ARGS='undefinedsymbol')
                _ = func(env, version_def.msvc_version, vc_dir, '')

                for msvc_uwp_app in (True, False):

                    sdk_list = WinSDK.get_msvc_sdk_version_list(version_def.msvc_version, msvc_uwp_app=msvc_uwp_app)
                    for sdk_version in sdk_list:

                        for kwargs in [
                            {'MSVC_SCRIPT_ARGS': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app},
                            {'MSVC_SDK_VERSION': sdk_version, 'MSVC_UWP_APP': msvc_uwp_app},
                        ]:
                            env = Environment(**kwargs)
                            _ = func(env, version_def.msvc_version, vc_dir, '')

                for kwargs in [
                    {'MSVC_SPECTRE_LIBS': True, 'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_TOOLSET_VERSION': version_def.msvc_verstr, 'MSVC_SCRIPT_ARGS': None},
                ]:
                    env = Environment(**kwargs)
                    with self.assertRaises(MSVCArgumentError):
                        _ = func(env, version_def.msvc_version, vc_dir, '')

            else:
                # VS2013 and earlier: no arguments

                env = Environment(MSVC_SCRIPT_ARGS='undefinedsymbol')
                with self.assertRaises(MSVCArgumentError):
                    _ = func(env, version_def.msvc_version, vc_dir, '')

                for kwargs in [
                    {'MSVC_UWP_APP': True, 'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_UWP_APP': '1',  'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_SPECTRE_LIBS': True, 'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_TOOLSET_VERSION': version_def.msvc_verstr, 'MSVC_SCRIPT_ARGS': None},
                    {'MSVC_SDK_VERSION': '10.0.00000.0', 'MSVC_SCRIPT_ARGS': None},
                ]:
                    env = Environment(**kwargs)
                    with self.assertRaises(MSVCArgumentError):
                        _ = func(env, version_def.msvc_version, vc_dir, '')

    def test_msvc_script_args_none(self):
        force = ScriptArguments.msvc_force_default_arguments(force=False)
        self.run_msvc_script_args_none()
        if Data.HAVE_MSVC:
            ScriptArguments.msvc_force_default_arguments(force=True)
            self.run_msvc_script_args_none()
        ScriptArguments.msvc_force_default_arguments(force=force)

    def test_msvc_script_args(self):
        force = ScriptArguments.msvc_force_default_arguments(force=False)
        self.run_msvc_script_args()
        ScriptArguments.msvc_force_default_arguments(force=True)
        self.run_msvc_script_args()
        ScriptArguments.msvc_force_default_arguments(force=force)

    def test_reset(self):
        ScriptArguments.reset()
        self.assertTrue(ScriptArguments._toolset_have140_cache is None, "ScriptArguments._toolset_have140_cache was not reset")
        self.assertFalse(ScriptArguments._toolset_version_cache, "ScriptArguments._toolset_version_cache was not reset")
        self.assertFalse(ScriptArguments._toolset_default_cache, "ScriptArguments._toolset_default_cache was not reset")

if __name__ == "__main__":
    unittest.main()

