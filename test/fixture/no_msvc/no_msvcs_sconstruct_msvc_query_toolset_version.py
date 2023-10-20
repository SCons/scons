# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

def DummyVsWhereExecutables(vswhere_env=None):
    # not testing versions with vswhere, so return empty list
    return []

for detect_cfg in SCons.Tool.MSCommon.MSVC.VSDetect._VSDetectRegistry.DETECT_CONFIG.values():
    detect_cfg.vc_cfg.regkeys.clear()

SCons.Tool.MSCommon.MSVC.VSWhere.vswhere_get_executables = DummyVsWhereExecutables
msvc_version, msvc_toolset_version = SCons.Tool.MSCommon.msvc_query_version_toolset()
print(f'msvc_version={msvc_version!r}, msvc_toolset_version={msvc_toolset_version!r}')
