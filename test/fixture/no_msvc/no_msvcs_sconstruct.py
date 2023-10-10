# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

def DummyVsWhereExecutables(vswhere_env=None):
    # not testing versions with vswhere, so return empty list
    return []

for detect_cfg in SCons.Tool.MSCommon.vc._VSDetectRegistry.DETECT_CONFIG.values():
    detect_cfg.vc_cfg.regkeys.clear()

SCons.Tool.MSCommon.vc._VSWhere.find_executables = DummyVsWhereExecutables
env = SCons.Environment.Environment()
print('MSVC_VERSION=' + str(env.get('MSVC_VERSION')))
