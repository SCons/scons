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
from SCons.Tool import MSCommon

import TestCmd

original = os.getcwd()

test = TestCmd.TestCmd(workdir='')

os.chdir(test.workpath(''))

MSVCUnsupportedHostArch = SCons.Tool.MSCommon.vc.MSVCUnsupportedHostArch
MSVCUnsupportedTargetArch = SCons.Tool.MSCommon.vc.MSVCUnsupportedTargetArch

MS_TOOLS_VERSION = '1.1.1'


class VswhereTestCase(unittest.TestCase):
    @staticmethod
    def _createVSWhere(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write("Created:%s" % f)

    def testDefaults(self):
        """
        Verify that msvc_find_vswhere() find's files in the specified paths
        """
        # import pdb; pdb.set_trace()
        vswhere_dirs = [os.path.splitdrive(p)[1] for p in SCons.Tool.MSCommon.vc.VSWHERE_PATHS]
        base_dir = test.workpath('fake_vswhere')
        test_vswhere_dirs = [os.path.join(base_dir,d[1:]) for d in vswhere_dirs]

        SCons.Tool.MSCommon.vc.VSWHERE_PATHS = test_vswhere_dirs
        for vsw in test_vswhere_dirs:
            VswhereTestCase._createVSWhere(vsw)
            find_path = SCons.Tool.MSCommon.vc.msvc_find_vswhere()
            self.assertTrue(vsw == find_path, "Didn't find vswhere in %s found in %s" % (vsw, find_path))
            os.remove(vsw)

    # def specifiedVswherePathTest(self):
    #     "Verify that msvc.generate() respects VSWHERE Specified"


class MSVcTestCase(unittest.TestCase):

    @staticmethod
    def _createDummyCl(path, add_bin=True):
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

        create_this = os.path.join(create_path,'cl.exe')

        # print("Creating: %s"%create_this)
        with open(create_this,'w') as ct:
            ct.write('created')


    def runTest(self):
        """
        Check that all proper HOST_PLATFORM and TARGET_PLATFORM are handled.
        Verify that improper HOST_PLATFORM and/or TARGET_PLATFORM are properly handled.
        by SCons.Tool.MSCommon.vc._check_cl_exists_in_vc_dir()
        """

        check = SCons.Tool.MSCommon.vc._check_cl_exists_in_vc_dir

        env={'TARGET_ARCH':'x86'}
        _, clpathcomps = SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_BATCHARG_CLPATHCOMPS[('x86','x86')]
        path = os.path.join('.', *clpathcomps)
        MSVcTestCase._createDummyCl(path, add_bin=False)

        # print("retval:%s"%check(env, '.', '8.0'))


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


        # Now walk all the valid combinations of host/target for 14.1 (VS2017) and later
        vc_ge2017_list = SCons.Tool.MSCommon.vc._GE2017_HOST_TARGET_CFG.all_pairs

        for host, target in vc_ge2017_list:
            batfile, clpathcomps = SCons.Tool.MSCommon.vc._GE2017_HOST_TARGET_BATCHFILE_CLPATHCOMPS[(host,target)]
            # print("GT 14 Got: (%s, %s) -> (%s, %s)"%(host,target,batfile,clpathcomps))

            env={'TARGET_ARCH':target, 'HOST_ARCH':host}
            path = os.path.join('.', 'Tools', 'MSVC', MS_TOOLS_VERSION, *clpathcomps)
            MSVcTestCase._createDummyCl(path, add_bin=False)
            result=check(env, '.', '14.1')
            # print("for:(%s, %s) got :%s"%(host, target, result))
            self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Now test bogus value for HOST_ARCH
        env={'TARGET_ARCH':'x86', 'HOST_ARCH':'GARBAGE'}
        try:
            result=check(env, '.', '14.1')
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus HOST_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedHostArch:
            pass
        else:
            self.fail('Did not fail when HOST_ARCH specified as: %s' % env['HOST_ARCH'])

        # Now test bogus value for TARGET_ARCH
        env={'TARGET_ARCH':'GARBAGE', 'HOST_ARCH':'x86'}
        try:
            result=check(env, '.', '14.1')
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus TARGET_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedTargetArch:
            pass
        else:
            self.fail('Did not fail when TARGET_ARCH specified as: %s' % env['TARGET_ARCH'])

        # Test 14.0 (VS2015) to 8.0 (VS2005) versions
        vc_le2015_list = SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_CFG.all_pairs

        for host, target in vc_le2015_list:
            batarg, clpathcomps = SCons.Tool.MSCommon.vc._LE2015_HOST_TARGET_BATCHARG_CLPATHCOMPS[(host, target)]
            # print("LE 14 Got: (%s, %s) -> (%s, %s)"%(host,target,batarg,clpathcomps))
            env={'TARGET_ARCH':target, 'HOST_ARCH':host}
            path = os.path.join('.', *clpathcomps)
            MSVcTestCase._createDummyCl(path, add_bin=False)
            result=check(env, '.', '9.0')
            # print("for:(%s, %s) got :%s"%(host, target, result))
            self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Now test bogus value for HOST_ARCH
        env={'TARGET_ARCH':'x86', 'HOST_ARCH':'GARBAGE'}
        try:
            result=check(env, '.', '9.0')
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus HOST_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedHostArch:
            pass
        else:
            self.fail('Did not fail when HOST_ARCH specified as: %s' % env['HOST_ARCH'])

        # Now test bogus value for TARGET_ARCH
        env={'TARGET_ARCH':'GARBAGE', 'HOST_ARCH':'x86'}
        try:
            result=check(env, '.', '9.0')
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus TARGET_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedTargetArch:
            pass
        else:
            self.fail('Did not fail when TARGET_ARCH specified as: %s' % env['TARGET_ARCH'])

        # Test 7.1 (VS2003) and earlier
        vc_le2003_list = SCons.Tool.MSCommon.vc._LE2003_HOST_TARGET_CFG.all_pairs

        for host, target in vc_le2003_list:
            # print("LE 7.1 Got: (%s, %s)"%(host,target))
            env={'TARGET_ARCH':target, 'HOST_ARCH':host}
            path = os.path.join('.')
            MSVcTestCase._createDummyCl(path)
            result=check(env, '.', '6.0')
            # print("for:(%s, %s) got :%s"%(host, target, result))
            self.assertTrue(result, "Checking host: %s target: %s" % (host, target))

        # Now test bogus value for HOST_ARCH
        env={'TARGET_ARCH':'x86', 'HOST_ARCH':'GARBAGE'}
        try:
            result=check(env, '.', '6.0')
            # print("for:%s got :%s"%(env, result))
            self.assertFalse(result, "Did not fail with bogus HOST_ARCH host: %s target: %s" % (env['HOST_ARCH'], env['TARGET_ARCH']))
        except MSVCUnsupportedHostArch:
            pass
        else:
            self.fail('Did not fail when HOST_ARCH specified as: %s' % env['HOST_ARCH'])

        # Now test bogus value for TARGET_ARCH
        env={'TARGET_ARCH':'GARBAGE', 'HOST_ARCH':'x86'}
        try:
            result=check(env, '.', '6.0')
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
                def restore(cls):
                    MSCommon.vc.msvc_default_version = cls.msvc_default_version

class MsvcSdkVersionsTests(unittest.TestCase):
    """Test msvc_sdk_versions"""

    def run_valid_default_msvc(self):
        symbol = MSCommon.vc.msvc_default_version()
        version_def = MSCommon.msvc_version_components(symbol)
        for msvc_uwp_app in (True, False):
            sdk_list = MSCommon.vc.msvc_sdk_versions(version=None, msvc_uwp_app=msvc_uwp_app)
            if symbol and version_def.msvc_vernum >= 14.0:
                self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(None)))
            else:
                self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(None)))

    def test_valid_default_msvc(self):
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self):
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            for msvc_uwp_app in (True, False):
                sdk_list = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)
                if Data.HAVE_MSVC and version_def.msvc_vernum >= 14.0:
                    self.assertTrue(sdk_list, "SDK list is empty for msvc version {}".format(repr(symbol)))
                else:
                    self.assertFalse(sdk_list, "SDK list is not empty for msvc version {}".format(repr(symbol)))

    def test_valid_vcver_toolsets(self):
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

    def test_invalid_vcver(self):
        for symbol in ['6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

    def test_invalid_vcver_toolsets(self):
        for symbol in ['14.31.123456', '14.31.1.1']:
            for msvc_uwp_app in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_sdk_versions(version=symbol, msvc_uwp_app=msvc_uwp_app)

class MsvcToolsetVersionsTests(unittest.TestCase):
    """Test msvc_toolset_versions"""

    def run_valid_default_msvc(self):
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

    def test_valid_default_msvc(self):
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self):
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

    def test_invalid_vcver(self):
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                _ = MSCommon.vc.msvc_toolset_versions(msvc_version=symbol)

class MsvcToolsetVersionsSpectreTests(unittest.TestCase):

    def run_valid_default_msvc(self):
        symbol = MSCommon.vc.msvc_default_version()
        version_def = MSCommon.msvc_version_components(symbol)
        spectre_toolset_list = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=None)
        if symbol and version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
            # spectre toolset list can empty (may not be installed)
            pass
        else:
            self.assertFalse(spectre_toolset_list, "Toolset spectre list is not empty for msvc version {}".format(repr(None)))

    def test_valid_default_msvc(self):
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc()
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc()

    def test_valid_vcver(self):
        for symbol in MSCommon.vc._VCVER:
            version_def = MSCommon.msvc_version_components(symbol)
            spectre_toolset_list = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=symbol)
            if version_def in Data.INSTALLED_VCS_COMPONENTS and version_def.msvc_vernum >= 14.1:
                # spectre toolset list can empty (may not be installed)
                pass
            else:
                self.assertFalse(spectre_toolset_list, "Toolset spectre list is not empty for msvc version {}".format(repr(symbol)))

    def test_invalid_vcver(self):
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                _ = MSCommon.vc.msvc_toolset_versions_spectre(msvc_version=symbol)

class MsvcQueryVersionToolsetTests(unittest.TestCase):
    """Test msvc_query_toolset_version"""

    def run_valid_default_msvc(self, have_msvc):
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

    def test_valid_default_msvc(self):
        if Data.HAVE_MSVC:
            Patch.MSCommon.vc.msvc_default_version.enable_none()
            self.run_valid_default_msvc(have_msvc=False)
            Patch.MSCommon.vc.msvc_default_version.restore()
        self.run_valid_default_msvc(have_msvc=Data.HAVE_MSVC)

    def test_valid_vcver(self):
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

    def test_valid_vcver_toolsets(self):
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

    def test_msvc_query_version_toolset_notfound(self):
        toolset_notfound_dict = Data.msvc_toolset_notfound_dict()
        for toolset_notfound_list in toolset_notfound_dict.values():
            for toolset in toolset_notfound_list[:1]:
                for prefer_newest in (True, False):
                    with self.assertRaises(MSCommon.vc.MSVCToolsetVersionNotFound):
                        _ = MSCommon.vc.msvc_query_version_toolset(version=toolset, prefer_newest=prefer_newest)

    def test_invalid_vcver(self):
        for symbol in ['12.9', '6.0Exp', '14.3Exp', '99', '14.1Bug']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)

    def test_invalid_vcver_toolsets(self):
        for symbol in ['14.16.00000Exp', '14.00.00001', '14.31.123456', '14.31.1.1']:
            for prefer_newest in (True, False):
                with self.assertRaises(MSCommon.vc.MSVCArgumentError):
                    _ = MSCommon.vc.msvc_query_version_toolset(version=symbol, prefer_newest=prefer_newest)


if __name__ == "__main__":
    unittest.main()
