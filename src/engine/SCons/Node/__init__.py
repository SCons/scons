"""SCons.Node

The Node package for the SCons software construction utility.

"""

#
# Copyright (c) 2001 Steven Knight
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



from SCons.Errors import BuildError
import string
import types


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
        if type(depend) is not type([]):
            raise TypeError("depend must be a list")
	self.depends.extend(depend)

    def add_source(self, source):
	"""Adds sources. The source argument must be a list."""
        if type(source) is not type([]):
            raise TypeError("source must be a list")
	self.sources.extend(source)

    def children(self):
	return self.sources + self.depends
