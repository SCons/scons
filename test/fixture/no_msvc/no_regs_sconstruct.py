# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

for key in SCons.Tool.MSCommon.vc._VSPRODUCT_REGISTRY_VCDIR:
    SCons.Tool.MSCommon.vc._VSPRODUCT_REGISTRY_VCDIR[key] = [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'')
    ]

env = SCons.Environment.Environment()
