# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

DefaultEnvironment(tools=[])
env = Environment()
env.Program('main.exe', ['main.c'])
