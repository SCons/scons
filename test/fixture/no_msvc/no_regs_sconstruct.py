# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import SCons
import SCons.Tool.MSCommon

DefaultEnvironment(tools=[])

for detect_cfg in SCons.Tool.MSCommon.vc._VSDetectRegistry.DETECT_CONFIG.values():
    detect_cfg.vc_cfg.regkeys.clear()

env = SCons.Environment.Environment()
