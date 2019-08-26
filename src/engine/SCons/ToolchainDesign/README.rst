SCons new toolchain design experiments
######################################

Class definitions
=================
  Tool.py : the new tool class
  Toolchain.py : a chain of tools

Test files
==========
  Tool-test.py : unit tests for Tool.py
  Toolchain-test.py : unit tests for Toolchain.py
  ToolCat.py: a test tool, currently not used

Samples
=======
  tool-example.py: a complete example of using a Tool defined as a class
  tool-module-example.py: example of using a Tool defined as a module (prefix_tool.py)
  prefix_tool.py: test tool for tool-module-example.py
