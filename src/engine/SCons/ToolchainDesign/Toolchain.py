"""Toolchain -- a Toolchain is a list of related tools and other
toolchains, forming a tree of related tools.  Toolchains may be "And"
(all tools must exist) or "Or" (first existing tool in the chain is
used), or other less-used variants.  Toolchains are used to group
related tools together, such as a compiler and linker, or LaTeX and
PDF. "Or" toolchains can be used for instance to select the best
compiler/linker for a given system configuration.

An AndToolchain is a list of Tools, all of which must exist for the
toolchain to be allowed to be used. (A simple Tool can be used
anywhere an AndToolchain is found.) A Toolchain is either an
AndToolchain, or an OR-list of Toolchains (an OrToolchain), in which
case each toolchain is tried in order and the first one to succeed is
used. Any element within a Toolchain may be marked as optional; such a
tool will be used if the toolchain is used and if it exists, but
doesn't need to exist to satisfy its toolchain.
"""

# XXX: optional tools/toolchains

def log(s):
  print(s)

class ToolchainError(Exception):
  pass

class OptionalElement(object):
  """Wrapper for any object that marks it as optional."""
  def __init__(self, base_object):
    self.base_object = base_object
  def exists(self):
    return self.base_object.exists()

class Toolchain(object):
  """Base class for Toolchains"""
  def __init__(self, tools):
    self.tools = tools
    pass

  @staticmethod
  def is_element_optional(element):
    """Returns true or false, plus the element itself.
    """
    if isinstance(element, OptionalElement):
      return (True, element.base_object)
    else:
      return (False, element)

  def tool_list(self):
    """Return list of all the enabled tools in this chain.  This
    always returns a list of Tools, never Toolchains.  The
    Toolchains are expanded into their Tools.  If there are no
    existing tools, returns empty list [].  Calls exists() on each
    element.
    """
    raise ToolchainError, "Toolchain subclasses should override this"

  def generate(self, env):
    """Call all the enabled tools' generate() methods."""
    for element in self.tool_list():
      element.generate(env)

class AndToolchain(Toolchain):
  """A toolchain all of whose tools must exist"""
  def __init__(self, tools):
    # XXX: could check for single tool, make it a list here
    super(AndToolchain, self).__init__(tools)

  def exists(self):
    """Returns True iff all the required elements in this toolchain exist.
    Recurses into elements which are Toolchains.
    """
    for element in self.tools:
      is_optional, element = self.is_element_optional(element)
      if not is_optional and not element.exists():
        return False
    return True

  def tool_list(self):
    if not self.exists():
      return []

    full_list = []
    for element in self.tools:
      is_optional, element = self.is_element_optional(element)
      if isinstance(element, Toolchain):
        # Don't care about optionalness here because
        # tool_list() will check existence if needed
        full_list.extend(element.tool_list())
      else:
        if not is_optional or element.exists():
          full_list.append(element)
    return full_list

class OrToolchain(Toolchain):
  """A toolchain which uses the first element which exists.
  Note that as with any Toolchain, elements may be other Toolchains."""
  def __init__(self, tools):
    super(OrToolchain, self).__init__(tools)

  def exists(self):
    """Returns True iff any element in this toolchain exists.
    Recurses into elements which are Toolchains.
    Optional/required doesn't come into things here.
    """
    for element in self.tools:
      is_optional, element = self.is_element_optional(element)
      if element.exists():
        return True
    return False

  def tool_list(self):
    """Returns a list of tools from the first existing element
    of this list.  Optional/required doesn't come into things here."""
    full_list = []
    for element in self.tools:
      is_optional, element = self.is_element_optional(element)
      if element.exists():
        if isinstance(element, Toolchain):
          return element.tool_list()
        else:
          return [element]
    # No tools found
    return []

class GeneratorToolchain(Toolchain):
  """A toolchain that uses a callback to create its tool list on
  request.  This is the most general form of toolchain because the
  callbacks can be anything.  The calling sequence and
  pre/post-conditions for this type of toolchain are still TBD."""
  def __init__(self, exists_callback, tool_list_callback, **kwargs):
    super(GeneratorToolchain, self).__init__(tools)
    self.args = kwargs
    self.exists_callback = exists_callback
    self.tool_list_callback = tool_list_callback

  def exists(self):
    return self.exists_callback(**args)

  def tool_list(self):
    return self.tool_list_callback(**args)

