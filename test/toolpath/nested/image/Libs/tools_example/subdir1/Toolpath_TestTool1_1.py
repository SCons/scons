# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

def generate(env):
    env['Toolpath_TestTool1_1'] = 1

def exists(env):
    return 1
