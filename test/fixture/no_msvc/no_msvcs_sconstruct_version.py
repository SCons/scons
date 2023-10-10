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
SCons.Tool.MSCommon.msvc_set_notfound_policy('error')
env = SCons.Environment.Environment(MSVC_VERSION='14.3')
