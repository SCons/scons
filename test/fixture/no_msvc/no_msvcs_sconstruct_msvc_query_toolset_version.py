# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

def DummyVsWhereExecutables(env=None):
    # not testing versions with vswhere, so return empty list
    return []

for key in SCons.Tool.MSCommon.vc._VSPRODUCT_REGISTRY_VCDIR:
    SCons.Tool.MSCommon.vc._VSPRODUCT_REGISTRY_VCDIR[key] = [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'')
    ]

SCons.Tool.MSCommon.vc._find_vswhere_executables = DummyVsWhereExecutables
msvc_version, msvc_toolset_version = SCons.Tool.MSCommon.msvc_query_version_toolset()
print(f'msvc_version={msvc_version!r}, msvc_toolset_version={msvc_toolset_version!r}')
