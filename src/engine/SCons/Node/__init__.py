"""SCons.Node

The Node package for the SCons software construction utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



from SCons.Errors import BuildError
import string



class Node:
    """The base Node class, for entities that we know how to
    build, or use to build other Nodes.
    """

    def __init__(self):
	self.sources = []
	self.depends = []
	self.derived = 0
	self.env = None

    def build(self):
	sources_str = string.join(map(lambda x: str(x), self.sources))
	stat = self.builder.execute(ENV = self.env.Dictionary('ENV'),
				    target = str(self), source = sources_str)
	if stat != 0:
	    raise BuildError(node = self, stat = stat)
	return stat

    def builder_set(self, builder):
	self.builder = builder

    def env_set(self, env):
	self.env = env

    def has_signature(self):
        return hasattr(self, "signature")

    def set_signature(self, signature):
        self.signature = signature

    def get_signature(self):
        return self.signature

    def add_dependency(self, depend):
	"""Adds dependencies. The depends argument must be a list."""
	self.depends.extend(depend)

    def add_source(self, source):
	"""Adds sources. The source argument must be a list."""
	self.sources.extend(source)
