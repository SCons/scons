
Design notes
============

The basic idea is that the current concept of a Tool is too low level;
the primary motivating use case is that users (SConscript authors)
should be able to select groups of related tools, *as* a group, with
fallbacks. A Toolchain is that abstraction. All the rest is just there
to make that idea work well. The secondary goal, in service of the
main one, is that Tools need to obey their abstraction, for instance
always calling `exists()`. The new system also creates a distinction
between an abstract tool, such as `intelc`, and a concrete instance of
it, such as `intelc v12 x86`. This is needed so the user can create
chains of either specific or general tools. One restriction I'm
imposing in the new system is that Tools have to be configurable
outside of any Environment; I don't like the current system where
tool-configuration variables ("tool args" basically) are mixed into
the Environment. This poses some challenges for a fully generalizable
system but I think I have a decent handle on that. The current Intel
compiler has an initial attempt at such tool args.

Some use cases:
 * a simple SConstruct should automatically select the "best"
   compiler/linker
 * a non-C-related SConstruct (e.g. doc prep, asset management,
   scientific data handling) shouldn't have to care about compilers,
   linkers or other unrelated tools
 * a SConstruct author should be able to specify toolchains and
   alternatives, and handle failures gracefully
 * it should be possible to write a SConstruct where the tools and
   toolchains can be manipulated by cmd line args if desired
 * it should be possible to specify desired tools generally
   ("gcc/gnulink") or very specifically ("gcc 4.3, x86 cross compiler,
   with gnulink 4.3 - and TeXLive")

User Stories:
=============

* As a SConscript writer, I want to be able to specify tools simply.
* As a SConscript writer, I want to be able to specify that the only tools I need
  are Sphinx and SCSS. Other tools should not be initialized nor slow
  down the build.
* As a SConscript writer, I'd like to be able to enumerate all
  versions of a tool on the system so I can choose which one to use.


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
