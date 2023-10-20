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


import os
import os.path
import unittest

import SCons.Node.FS
import SCons.Warnings
import SCons.Tool.MSCommon.vc
from SCons.Tool.MSCommon.MSVC import VSWhere
from SCons.Tool import MSCommon

import TestCmd

original = os.getcwd()

test = TestCmd.TestCmd(workdir='')

os.chdir(test.workpath(''))

MSVCUnsupportedHostArch = SCons.Tool.MSCommon.vc.MSVCUnsupportedHostArch
MSVCUnsupportedTargetArch = SCons.Tool.MSCommon.vc.MSVCUnsupportedTargetArch

MS_TOOLS_VERSION = '1.1.1'

native_host = SCons.Tool.MSCommon.vc.get_native_host_platform()

class VswhereTestCase(unittest.TestCase):
    @staticmethod
    def _createVSWhere(path) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("Created:%s" % f)

    _existing_path = None

    @classmethod
    def _path_exists(cls, path):
        return (path == cls._existing_path)

    def testDefaults(self) -> None:
        """
        Verify that msvc_find_vswhere() find's files in the specified paths
        """

        restore_vswhere_execs_exist = list(VSWhere._VSWhere.vswhere_executables)

        base_dir = test.workpath('fake_vswhere')
        norm_dir = os.path.normcase(os.path.normpath(base_dir))
        # import pdb; pdb.set_trace()

        test_vswhere_dirs = [
            VSWhere._VSWhere.VSWhereExecutable(
                path=os.path.join(base_dir,t[0][1:]),
                norm=os.path.join(norm_dir,t[1][1:]),
            )
            for t in [
                (os.path.splitdrive(vswexec.path)[1], os.path.splitdrive(vswexec.norm)[1])
                for vswexec in VSWhere._VSWhere.vswhere_executables
            ]
        ]

        for vswexec in test_vswhere_dirs:
            VswhereTestCase._createVSWhere(vswexec.path)
            VSWhere._VSWhere.vswhere_executables = [vswexec]
            find_path = MSCommon.vc.msvc_find_vswhere()
            self.assertTrue(vswexec.path == find_path, "Didn't find vswhere in %s found in %s" % (vswexec.path, find_path))
            os.remove(vswexec.path)

        test_vswhere_dirs = [
            os.path.join(base_dir,d[1:])
            for d in [
                os.path.splitdrive(p)[1]
                for p in VSWhere.VSWHERE_PATHS
            ]
        ]
        MSCommon.vc.path_exists = VswhereTestCase._path_exists

        for vswpath in test_vswhere_dirs:
            VswhereTestCase._createVSWhere(vswpath)
            VswhereTestCase._existing_path = vswpath
            for front in (True, False):
                VSWhere._VSWhere.vswhere_executables = []
                MSCommon.MSVC.VSWhere.vswhere_push_location(vswpath, front=front)
                find_path = MSCommon.vc.msvc_find_vswhere()
                self.assertTrue(vswpath == find_path, "Didn't find vswhere in %s found in %s" % (vswpath, find_path))
            os.remove(vswpath)

        VSWhere._VSWhere.vswhere_executables = restore_vswhere_execs_exist

    # def specifiedVswherePathTest(self):
    #     "Verify that msvc.generate() respects VSWHERE Specified"


class MSVcTestCase(unittest.TestCase):

    @staticmethod
    def _createDummyMSVSBase(vc_version, vs_component, vs_dir):
        vs_product_def = SCons.Tool.MSCommon.MSVC.Config.MSVC_VERSION_INTERNAL[vc_version]
        vs_component_key = (vs_product_def.vs_lookup, vs_component)
        msvs_base = SCons.Tool.MSCommon.MSVC.VSDetect.MSVSBase.factory(
            vs_product_def=vs_product_def,
            vs_channel_def=SCons.Tool.MSCommon.MSVC.Config.MSVS_CHANNEL_RELEASE,
            vs_component_def=SCons.Tool.MSCommon.MSVC.Config.MSVS_COMPONENT_INTERNAL[vs_component_key],
            vs_sequence_nbr=1,
            vs_dir=vs_dir,
            vs_version=vs_product_def.vs_version,
        )
        return msvs_base

    @classmethod
    def _createDummyMSVCInstance(cls, vc_version, vs_component, vc_dir):
        msvc_instance = SCons.Tool.MSCommon.MSVC.VSDetect.MSVCInstance.factory(
            msvs_base=cls._createDummyMSVSBase(vc_version, vs_component, vc_dir),
            vc_version_def=SCons.Tool.MSCommon.MSVC.Util.msvc_version_components(vc_version),
            vc_feature_map=None,
            vc_dir=vc_dir,
        )
        return msvc_instance

    @staticmethod
    def _createDummyFile(path, filename, add_bin: bool=True) -> None:
        """
        Creates a dummy cl.exe in the correct directory.
        It will create all missing parent directories as well

        Args:
            path: Relative path to cl.exe for the version about to be tested.
        """

        # print("PATH:%s"%path)

        path = path.replace('\\', os.sep)
        if add_bin:
            create_path = os.path.join(path,'bin')
        else:
            create_path = path
        if create_path and not os.path.isdir(create_path):
            os.makedirs(create_path)

        create_this = os.path.join(create_path, filename)

        # print("Creating: %s"%create_this)
        with open(create_this,'w') as ct:
            ct.write('created')


    def runTest(self) -> None:
        """
        Check that all proper HOST_PLATFORM and TARGET_PLATFORM are handled.
        Verify that improper HOST_PLATFORM and/or TARGET_PLATFORM are properly handled.
        by SCons.Tool.MSCommon.vc._msvc_instance_check_files_exist()
        """

        check = SCons.Tool.MSCommon.vc._msvc_instance_check_files_exist

        # Setup for 14.1 (VS2017) and later tests

        # Create the VC minor/major version file
        tools_version_file = SCons.Tool.MSCommon.vc._VC_TOOLS_VERSION_FILE
        tools_dir = os.path.dirname(tools_version_file)
        if not os.path.isdir(tools_dir):
            os.makedirs(tools_dir)
        try:
            with open(tools_version_file, 'w') as tf:
                tf.write(MS_TOOLS_VERSION)
        except IOError as e:
            print("Failed trying to write :%s :%s" % (tools_version_file, e))

        # Test 14.3 (VS2022) and later
        msvc_instance_VS2022 = MSVcTestCase._createDummyMSVCInstance('14.3', 'Community', '.')
        for host in SCons.Tool.MSCommon.vc._GE2022_HOST_TARGET_CFG.host_all_hosts[native_host]:
            for target in SCons.Tool.MSCommon.vc._GE2022_HOST_TARGET_CFG.host_all_targets[host]:
                _, batfile, clpathcomps = SCons.Tool.MSCommon.vc._GE2022_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host,target)]
                # print("GE 14.3 Got: (%s, %s) -> (%s, %s)"%(host,target,batfile,clpathcomps))
                path = os.path.join('.', "Auxiliary", "Build", batfile)
                MSVcTestCase._createDummyFile(path, batfile, add_bin=False)
                path = os.path.join('.', 'Tools', 'MSVC', MS_TOOLS_VERSION, *clpathcomps)
                MSVcTestCase._createDummyFile(path, 'cl.exe', add_bin=False)
                result=check(msvc_instance_VS2022)
                # print("for:(%s, %s) got :%s"%(host, target, result))
                self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Test 14.2 (VS2019) to 14.1 (VS2017) versions
        msvc_instance_VS2017 = MSVcTestCase._createDummyMSVCInstance('14.1', 'Community', '.')
        for host in SCons.Tool.MSCommon.vc._LE2019_HOST_TARGET_CFG.host_all_hosts[native_host]:
            for target in SCons.Tool.MSCommon.vc._LE2019_HOST_TARGET_CFG.host_all_targets[host]:
                _, batfile, clpathcomps = SCons.Tool.MSCommon.vc._LE2019_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host,target)]
                # print("LE 14.2 Got: (%s, %s) -> (%s, %s)"%(host,target,batfile,clpathcomps))
                path = os.path.join('.', 'Tools', 'MSVC', MS_TOOLS_VERSION, *clpathcomps)
                MSVcTestCase._createDummyFile(path, 'cl.exe', add_bin=False)
                result=check(msvc_instance_VS2017)
                # print("for:(%s, %s) got :%s"%(host, target, result))
                self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Test 14.0 (VS2015) to 10.0 (VS2010) versions
        msvc_instance_VS2010 = MSVcTestCase._createDummyMSVCInstance('10.0', 'Develop', '.')
        for host in SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_CFG.host_all_hosts[native_host]:
            for target in SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_CFG.host_all_targets[host]:
                batarg, batfile, clpathcomps = SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host, target)]
                # print("LE 14.0 Got: (%s, %s) -> (%s, %s, %s)"%(host,target,batarg,batfile,clpathcomps))
                MSVcTestCase._createDummyFile('.', 'vcvarsall.bat', add_bin=False)
                path = os.path.join('.', *clpathcomps)
                MSVcTestCase._createDummyFile(path, batfile, add_bin=False)
                MSVcTestCase._createDummyFile(path, 'cl.exe', add_bin=False)
                result=check(msvc_instance_VS2010)
                # print("for:(%s, %s) got :%s"%(host, target, result))
                self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Test 9.0 (VC2008) to 8.0 (VS2005)
        msvc_instance_VS2005 = MSVcTestCase._createDummyMSVCInstance('8.0', 'Develop', '.')
        for host in SCons.Tool.MSCommon.vc._LE2008_HOST_TARGET_CFG.host_all_hosts[native_host]:
            for target in SCons.Tool.MSCommon.vc._LE2008_HOST_TARGET_CFG.host_all_targets[host]:
                batarg, batfile, clpathcomps = SCons.Tool.MSCommon.vc._LE2008_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host, target)]
                # print("LE 9.0 Got: (%s, %s) -> (%s, %s, %s)"%(host,target,batarg,batfile,clpathcomps))
                MSVcTestCase._createDummyFile('.', 'vcvarsall.bat', add_bin=False)
                path = os.path.join('.', *clpathcomps)
                MSVcTestCase._createDummyFile(path, batfile, add_bin=False)
                MSVcTestCase._createDummyFile(path, 'cl.exe', add_bin=False)
                # check will fail if '9.0' and VCForPython (layout different)
                result=check(msvc_instance_VS2005)
                # print("for:(%s, %s) got :%s"%(host, target, result))
                self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Test 7.1 (VS2003) and earlier
        msvc_instance_VS6 = MSVcTestCase._createDummyMSVCInstance('6.0', 'Develop', '.')
        for host in SCons.Tool.MSCommon.vc._LE2003_HOST_TARGET_CFG.host_all_hosts[native_host]:
            for target in SCons.Tool.MSCommon.vc._LE2003_HOST_TARGET_CFG.host_all_targets[host]:
                batarg, batfile, clpathcomps = SCons.Tool.MSCommon.vc._LE2003_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host, target)]
                # print("LE 7.1 Got: (%s, %s)"%(host,target))
                path = os.path.join('.', *clpathcomps)
                MSVcTestCase._createDummyFile(path, batfile, add_bin=False)
                MSVcTestCase._createDummyFile(path, 'cl.exe', add_bin=False)
                result=check(msvc_instance_VS6)
                # print("for:(%s, %s) got :%s"%(host, target, result))
                self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        check = SCons.Tool.MSCommon.vc.get_host_target

        # Now test bogus value for HOST_ARCH
        env={'TARGET_ARCH':'x86', 'HOST_ARCH':'GARBAGE'}
        try:
            check(env, msvc_instance_VS2022.vc_version_def.msvc_version)
            result = True
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus HOST_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedHostArch:
            pass
        else:
            self.fail('Did not fail when HOST_ARCH specified as: %s' % env['HOST_ARCH'])

        # Now test bogus value for TARGET_ARCH
        env={'TARGET_ARCH':'GARBAGE', 'HOST_ARCH':'x86'}
        try:
            check(env, msvc_instance_VS2022.vc_version_def.msvc_version)
            result = True
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus TARGET_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedTargetArch:
            pass
        else:
            self.fail('Did not fail when TARGET_ARCH specified as: %s' % env['TARGET_ARCH'])

class Data:

    HAVE_MSVC = True if MSCommon.vc.msvc_default_version() else False

    INSTALLED_VCS_COMPONENTS = MSCommon.vc.get_installed_vcs_components()

    @classmethod
    def _msvc_toolset_notfound_list(cls, toolset_seen, toolset_list):
        new_toolset_list = []
        if not toolset_list:
            return new_toolset_list
        for toolset_version in toolset_list:
            version = toolset_version
            comps = version.split('.')
            if len(comps) != 3:
                continue
            # full versions only
            nloop = 0
            while nloop < 10:
                ival = int(comps[-1])
                if ival == 0:
                    ival = 1000000
                ival -= 1
                version = '{}.{}.{:05d}'.format(comps[0], comps[1], ival)
                if version not in toolset_seen:
                    new_toolset_list.append(version)
                    break
                nloop += 1
        return new_toolset_list

    _msvc_toolset_notfound_dict = None

    @classmethod
    def msvc_toolset_notfound_dict(cls):
        if cls._msvc_toolset_notfound_dict is None:
            toolset_seen = set()
            toolset_dict = {}
            for symbol in MSCommon.vc._VCVER:
                toolset_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=True, sxs=False)
                if not toolset_list:
                    continue
                toolset_seen.update(toolset_list)
                toolset_dict[symbol] = toolset_list
            for key, val in toolset_dict.items():
                toolset_dict[key] = cls._msvc_toolset_notfound_list(toolset_seen, val)
            cls._msvc_toolset_notfound_dict = toolset_dict
        return cls._msvc_toolset_notfound_dict

class Patch:

    class MSCommon:

        class vc:

            class msvc_default_version:

                msvc_default_version = MSCommon.vc.msvc_default_version

                @classmethod
                def msvc_default_version_none(cls):
                    return None

                @classmethod
                def enable_none(cls):
                    hook = cls.msvc_default_version_none
                    MSCommon.vc.msvc_default_version = hook
                    return hook

                @classmethod
                def restore(cls) -> None:
                    MSCommon.vc.msvc_default_version = cls.msvc_default_version

class MsvcSdkVersionsTests(unittest.TestCase):
    """Test msvc_sdk_versions"""

    def run_valid_default_msvc(self) -> None:
        symbol = MSCommon.vc.msvc_default_version()
        version_def = MSCommon.msvc_version_components(symbol)
        for msvc_uwp_app in (True, False):
            sdk_list = MSCommon.vc.msvc_sdk_versions(version=None, msvc_uwp_app=msvc_uwp_app)
            if symbol and version_def.msvc_vernum >= 14.0:
                self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(None)))
            else:
                self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(None)))

    def test_valid_default_msvc(self) -> None:
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            if Data.HAVE_MSVC:
                for msvc_uwp_app in (True, False):
                    sdk_list = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)
                    if version_def.msvc_vernum >= 14.0:
                        self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(symbol)))
                    else:
                        self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(symbol)))

    def test_valid_vcver_toolsets(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            toolset_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if toolset_list is None:
                continue
            for toolset in toolset_list:
                extended_def = MSCommon.msvc_extended_version_components(toolset)
                for msvc_uwp_app in (True, False):
                    sdk_list = MSCommon.vc.msvc_sdk_versions(
                        version=extended_def.msvc_toolset_version,
                        msvc_uwp_app=msvc_uwp_app
                    )
                    self.assertTrue(sdk_list, "SDK list is empty for msvc toolset version {}".format(repr(toolset)))

    def test_invalid_vcver(self) -> None:
        for symbol in ['6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

    def test_invalid_vcver_toolsets(self) -> None:
        for symbol in ['14.31.123456', '14.31.1.1']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

class MsvcToolsetVersionsTests(unittest.TestCase):
    """Test msvc_toolset_versions"""

    def run_valid_default_msvc(self) -> None:
        symbol = MSCommon.vc.msvc_default_version()
        version_def = MSCommon.msvc_version_components(symbol)
        toolset_none_list = MSCommon.vc.msvc_toolset_versions(msvc_version=None, full=False, sxs=False)
        toolset_full_list = MSCommon.vc.msvc_toolset_versions(msvc_version=None, full=True, sxs=False)
        toolset_sxs_list = MSCommon.vc.msvc_toolset_versions(msvc_version=None, full=False, sxs=True)
        toolset_all_list = MSCommon.vc.msvc_toolset_versions(msvc_version=None, full=True, sxs=True)
        if symbol and version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
            # sxs list could be empty
            self.assertTrue(toolset_full_list, "Toolset full list is empty for msvc version {}".format(repr(None)))
            self.assertTrue(toolset_all_list, "Toolset all list is empty for msvc version {}".format(repr(None)))
        else:
            self.assertFalse(toolset_full_list, "Toolset full list is not empty for msvc version {}".format(repr(None)))
            self.assertFalse(toolset_sxs_list, "Toolset sxs list is not empty for msvc version {}".format(repr(None)))
            self.assertFalse(toolset_all_list, "Toolset all list is not empty for msvc version {}".format(repr(None)))
        self.assertFalse(toolset_none_list, "Toolset none list is not empty for msvc version {}".format(repr(None)))

    def test_valid_default_msvc(self) -> None:
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            toolset_none_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=False, sxs=False)
            toolset_full_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=True, sxs=False)
            toolset_sxs_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=False, sxs=True)
            toolset_all_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
                # sxs list could be empty
                self.assertTrue(toolset_full_list, "Toolset full list is empty for msvc version {}".format(repr(symbol)))
                self.assertTrue(toolset_all_list, "Toolset all list is empty for msvc version {}".format(repr(symbol)))
            else:
                self.assertFalse(toolset_full_list, "Toolset full list is not empty for msvc version {}".format(repr(symbol)))
                self.assertFalse(toolset_sxs_list, "Toolset sxs list is not empty for msvc version {}".format(repr(symbol)))
                self.assertFalse(toolset_all_list, "Toolset all list is not empty for msvc version {}".format(repr(symbol)))
            self.assertFalse(toolset_none_list, "Toolset none list is not empty for msvc version {}".format(repr(symbol)))

    def test_invalid_vcver(self) -> None:
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                _ = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol)

class MsvcToolsetVersionsSpectreTests(unittest.TestCase):

    def run_valid_default_msvc(self) -> None:
        symbol = MSCommon.vc.msvc_default_version()
        version_def = MSCommon.msvc_version_components(symbol)
        spectre_toolset_list = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=None)
        if symbol and version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
            # spectre toolset list can empty (may not be installed)
            pass
        else:
            self.assertFalse(spectre_toolset_list, "Toolset spectre list is not empty for msvc version {}".format(repr(None)))

    def test_valid_default_msvc(self) -> None:
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            spectre_toolset_list = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=symbol)
            if version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
                # spectre toolset list can empty (may not be installed)
                pass
            else:
                self.assertFalse(spectre_toolset_list, "Toolset spectre list is not empty for msvc version {}".format(repr(symbol)))

    def test_invalid_vcver(self) -> None:
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                _ = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=symbol)

class MsvcQueryVersionToolsetTests(unittest.TestCase):
    """Test msvc_query_toolset_version"""

    def run_valid_default_msvc(self, have_msvc) -> None:
        for prefer_newest in (True, False):
            msvc_version, msvc_toolset_version = MSCommon.vc.msvc_query_version_toolset(
                version=None, prefer_newest=prefer_newest
            )
            expect = (have_msvc and msvc_version) or (not have_msvc and not msvc_version)
            self.assertTrue(expect, "unexpected msvc_version {} for for msvc version {}".format(
                repr(msvc_version), repr(None)
            ))
            version_def = MSCommon.msvc_version_components(msvc_version)
            if have_msvc and version_def.msvc_vernum > 14.0:
                # VS2017 and later for toolset version
                self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc version {}".format(
                    repr(None)
                ))

    def test_valid_default_msvc(self) -> None:
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc(have_msvc=False)
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc(have_msvc=Data.HAVE_MSVC)

    def test_valid_vcver(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            for prefer_newest in (True, False):
                msvc_version, msvc_toolset_version = MSCommon.vc.msvc_query_version_toolset(
                    version=symbol, prefer_newest=prefer_newest
                )
                self.assertTrue(msvc_version, "msvc_version is undefined for msvc version {}".format(repr(symbol)))
                if version_def.msvc_vernum > 14.0:
                    # VS2017 and later for toolset version
                    self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc version {}".format(
                        repr(symbol)
                    ))

    def test_valid_vcver_toolsets(self) -> None:
        for symbol in MSCommon.vc._VCVER:
            toolset_list = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol, full=True, sxs=True)
            if toolset_list is None:
                continue
            for toolset in toolset_list:
                extended_def = MSCommon.msvc_extended_version_components(toolset)
                for prefer_newest in (True, False):
                    version = extended_def.msvc_toolset_version
                    msvc_version, msvc_toolset_version = MSCommon.vc.msvc_query_version_toolset(
                        version=version, prefer_newest=prefer_newest
                    )
                    self.assertTrue(msvc_version, "msvc_version is undefined for msvc toolset version {}".format(repr(toolset)))
                    if extended_def.msvc_vernum > 14.0:
                        # VS2017 and later for toolset version
                        self.assertTrue(msvc_toolset_version, "msvc_toolset_version is undefined for msvc toolset version {}".format(
                            repr(toolset)
                        ))

    def test_msvc_query_version_toolset_notfound(self) -> None:
        toolset_notfound_dict = Data.msvc_toolset_notfound_dict()
        for toolset_notfound_list in toolset_notfound_dict.values():
            for toolset in toolset_notfound_list[:1]:
                for prefer_newest in (True, False):
                    with self.assertRaises(MSCommon.vc.MSVCToolsetVersionNotFound):
                        _ = MSCommon.vc.msvc_query_version_toolset(version=toolset, prefer_newest=prefer_newest)

    def test_invalid_vcver(self) -> None:
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)

    def test_invalid_vcver_toolsets(self) -> None:
        for symbol in ['14.16.00000Exp', '14.00.00001', '14.31.123456', '14.31.1.1']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)


if __name__ == "__main__":
    unittest.main()
