"""scons.Builder

XXX

"""

__revision__ = "Builder.py __REVISION__ __DATE__ __DEVELOPER__"



import os
import types
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
	self.action = Action(action)
	self.insuffix = input_suffix
	self.outsuffix = output_suffix
	self.node_class = node_class
	if not self.insuffix is None and self.insuffix[0] != '.':
	    self.insuffix = '.' + self.insuffix
	if not self.outsuffix is None and self.outsuffix[0] != '.':
	    self.outsuffix = '.' + self.outsuffix

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def __call__(self, env, target = None, source = None):
	node = lookup(self.node_class, target)
	node.builder_set(self)
	node.env_set(self)
	node.sources = source	# XXX REACHING INTO ANOTHER OBJECT
	return node

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	apply(self.action.execute, (), kw)



def Action(act):
    """A factory for action objects."""
    if type(act) == types.FunctionType:
	return FunctionAction(act)
    elif type(act) == types.StringType:
	return CommandAction(act)
    else:
	return None

class ActionBase:
    """Base class for actions that create output objects.
    
    We currently expect Actions will only be accessible through
    Builder objects, so they don't yet merit their own module."""
    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def show(self, string):
	print string

class CommandAction(ActionBase):
    """Class for command-execution actions."""
    def __init__(self, string):
	self.command = string

    def execute(self, **kw):
	cmd = self.command % kw
	self.show(cmd)
	os.system(cmd)

class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
	self.function = function

    def execute(self, **kw):
	# XXX:  WHAT SHOULD WE PRINT HERE?
	self.function(kw)
