"""Full example of defining, registering and using a tool as a module.

This is "sort of" a SConstruct.  Run it as scons -f <thisfile>
"""

import os, os.path
import Tool
import Toolchain

import prefix_tool              # our tool!

env=Environment()

prefix_tool = Tool.Tool.lookup('prefix-tool')
if not prefix_tool.exists():
  print "NO PREFIX TOOL: %s"%prefix_tool.exists_error()
prefix_tool.generate(env)

env.Prefix(target='tgt', source='src', PREFIX='foo: ')
