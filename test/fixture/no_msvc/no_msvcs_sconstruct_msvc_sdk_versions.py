import SCons
import SCons.Tool.MSCommon

def DummyVsWhere(msvc_version, env):
    # not testing versions with vswhere, so return none
    return None

for key in SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR:
    SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR[key]=[(SCons.Util.HKEY_LOCAL_MACHINE, r'')]

SCons.Tool.MSCommon.vc.find_vc_pdir_vswhere = DummyVsWhere

sdk_version_list = SCons.Tool.MSCommon.msvc_sdk_versions()

print('sdk_version_list='+repr(sdk_version_list))
