"""scons.Node

The Node package for the scons software construction utility.

"""

__revision__ = "Node/__init__.py __REVISION__ __DATE__ __DEVELOPER__"



class Node:
    """The base Node class, for entities that we know how to
    build, or use to build other Nodes.
    """
    def build(self):
	self.builder.execute(target = self.path, source = self.sources)

    def builder_set(self, builder):
	self.builder = builder

    def env_set(self, env):
	self.env = env
