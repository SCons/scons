# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

def DummyVsWhere(msvc_version, vswhere_exe):
    # not testing versions with vswhere, so return none
    return None

for key in SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR:
    SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR[key] = [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')
    ]

SCons.Tool.MSCommon.vc._find_vc_pdir_vswhere = DummyVsWhere
env = SCons.Environment.Environment(tools=['myignoredefaultmsvctool'])

