"""scons.Builder

XXX

"""

__revision__ = "Builder.py __REVISION__ __DATE__ __DEVELOPER__"



import os
from types import *
from scons.Node.FS import Dir, File, lookup



class Builder:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,	name = None,
			action = None,
			input_suffix = None,
			output_suffix = None,
			node_class = File):
	self.name = name
	self.action = action
	self.insuffix = input_suffix
	self.outsuffix = output_suffix
	self.node_class = node_class
	if not self.insuffix is None and self.insuffix[0] != '.':
	    self.insuffix = '.' + self.insuffix
	if not self.outsuffix is None and self.outsuffix[0] != '.':
	    self.outsuffix = '.' + self.outsuffix

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def __call__(self, target = None, source = None):
	node = lookup(self.node_class, target)
	node.builder_set(self)
	node.sources = source	# XXX REACHING INTO ANOTHER OBJECT
	return node

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	# XXX THIS SHOULD BE DONE BY TURNING Builder INTO A FACTORY
	# FOR SUBCLASSES FOR StringType AND FunctionType
	t = type(self.action)
	if t == StringType:
	    cmd = self.action % kw
	    print cmd
	    os.system(cmd)
	elif t == FunctionType:
	    # XXX WHAT SHOULD WE PRINT HERE
	    self.action(kw)
