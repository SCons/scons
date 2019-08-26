"""Base Tool class.  All tools should be derived from this.
"""

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log(s):
  logger.debug(s)

class ToolError(Exception):
  pass

class ToolRegistry(object):
  """Registry for all tools.
  Registers (memoizes) tool objects, which are singletons based on
  their class and construction args.
  """
  def __init__(self):
    self.clean()

  def register(self, name, toolclass, *args, **kwargs):
    """Returns a memorized tool object, given the
    tool's class and construction args.
    It is an error if there is already a tool object in the registry
    but the passed-in name doesn't match it."""

    class hashabledict(dict):
      def __hash__(self):
        return hash(frozenset(self))

    log("registering %s, class %s, args %s, %s"%(name, toolclass, args, kwargs))

    if not name:
      raise ToolError("Trying to register tool with no name: class %s"%repr(toolclass))

    key = (toolclass, args, hashabledict(kwargs))
    t = self.tools.get(key)
    if t and t.name != name:
      raise ToolError("Found matching tool %s, but doesn't match name %s"%(t.name, name))

    if not t:
      # create tool
      log("CREATING %s, class %s, args %s, %s"%(name, toolclass, args, kwargs))
      t = toolclass(name, *args, **kwargs)
      self.tools[key] = t
      self.by_name[name] = t
      self.name_by_object[t] = name
    log("ToolRegistry: found %s, name %s"%(t, self.name_by_object[t]))
    return t

  def clean(self):
    self.tools = {}
    self.by_name = {}
    self.name_by_object = {}

  def lookup_by_name(self, name):
    """Return the tool with the given name, otherwise None."""
    return self.by_name.get(name)

the_registry = ToolRegistry()


class Tool(object):
  """base class for all Tools"""

  # Is this needed?  Don't think we ever want to instantiate a base tool.
  # But it seems useful to call from real tools to set things up.
  def __init__(self, toolname, *args, **kwargs):
    log("Tool init: name=%s"%toolname)
    self._name = toolname
    self._args = args
    self._kwargs = kwargs
    self._exists_error = None

  @staticmethod
  def register(toolname, toolclass, *args, **kwargs):
    return the_registry.register(toolname, toolclass, *args, **kwargs)

  @staticmethod
  def lookup(toolname):
    return the_registry.lookup_by_name(toolname)

  @property
  def name(self):
    return self._name

  @classmethod
  def create(name, *args, **kw):
    """Look up tool by name.  Create and return an instance of it."""
    # Tools are memoized by name & args
    tc = tools[name] # this is the tool's class
    return tc(*args, **kw)

  def exists(self, env, use_env):
    """Returns True/False status depending on whether the tool's
    executable exists, i.e. the tool can be used; when the tool isn't
    usable, returns False with an explanatory message in
    exists_error().  Should never throw an exception."""
    self._exists_error = "Base tool never exists; it's not a real tool."
    return False

  def exists_error(self):
    """Returns error string if tool doesn't exist.
    It is only defined to call this just after exists() returns False.
    Any other call gives undefined results."""
    return self._exists_error

  def set_exists_error(self, str):
    """Set the exists_error string.  Should only be called from exists()."""
    self._exists_error = str

  def generate(self, env):
    """Set up the env to use the tool.
    Defines construction variables, sets paths, etc.
    No return value."""
    raise ToolError("Should never call base Tool.generate()")
