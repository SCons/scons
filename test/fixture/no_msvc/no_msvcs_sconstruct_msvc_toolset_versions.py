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
toolset_version_list = SCons.Tool.MSCommon.msvc_toolset_versions()
print('toolset_version_list=' + repr(toolset_version_list))
