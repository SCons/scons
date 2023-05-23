# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

def DummyVsWhere(msvc_version, env):
    # not testing versions with vswhere, so return none
    return None

for key in SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR:
    SCons.Tool.MSCommon.vc._VCVER_TO_PRODUCT_DIR[key] = [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')
    ]

SCons.Tool.MSCommon.vc.find_vc_pdir_vswhere = DummyVsWhere
msvc_version, msvc_toolset_version = SCons.Tool.MSCommon.msvc_query_version_toolset()
print(f'msvc_version={msvc_version!r}, msvc_toolset_version={msvc_toolset_version!r}')
