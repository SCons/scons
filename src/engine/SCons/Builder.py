"""SCons.Builder

XXX

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



import os
import SCons.Node.FS
import string
import types



class Builder:
    """Base class for Builders, objects that create output
    nodes (files) from input nodes (files).
    """

    def __init__(self,	name = None,
			action = None,
			input_suffix = None,
			output_suffix = None,
			node_factory = SCons.Node.FS.default_fs.File):
	self.name = name
	self.action = Action(action)
	self.insuffix = input_suffix
	self.outsuffix = output_suffix
	self.node_factory = node_factory
	if not self.insuffix is None and self.insuffix[0] != '.':
	    self.insuffix = '.' + self.insuffix
	if not self.outsuffix is None and self.outsuffix[0] != '.':
	    self.outsuffix = '.' + self.outsuffix

    def __cmp__(self, other):
	return cmp(self.__dict__, other.__dict__)

    def __call__(self, env, target = None, source = None):
	node = self.node_factory(target)
	node.builder_set(self)
	node.env_set(self)

        # XXX REACHING INTO ANOTHER OBJECT (this is only temporary):
        assert type(source) is type("")
        node.sources = source
        node.derived = 1
        sources = string.split(source, " ")
        sources = filter(lambda x: x, sources)
        source_nodes = []
        for source in sources:
            source_node = self.node_factory(source)
            source_node.derived = 0
            source_node.source_nodes = []
            source_nodes.append(source_node)
        node.source_nodes = source_nodes
        
	return node

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	apply(self.action.execute, (), kw)



print_actions = 1;
execute_actions = 1;



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
	if print_actions:
	    self.show(cmd)
	if execute_actions:
	    os.system(cmd)

class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
	self.function = function

    def execute(self, **kw):
	# if print_actions:
	# XXX:  WHAT SHOULD WE PRINT HERE?
	if execute_actions:
	    self.function(kw)
