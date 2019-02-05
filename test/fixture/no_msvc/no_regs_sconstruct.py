import SCons
import SCons.Tool.MSCommon

for key in SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR:
    SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR[key]=[(SCons.Util.HKEY_LOCAL_MACHINE, r'')]

env = SCons.Environment.Environment()