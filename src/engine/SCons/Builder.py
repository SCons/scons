"""SCons.Builder

XXX

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



import os
import SCons.Node.FS
import SCons.Util
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
	tlist = SCons.Util.scons_str2nodes(target)
	slist = SCons.Util.scons_str2nodes(source)
	for t in tlist:
	    t.builder_set(self)
	    t.env_set(env)
	    t.derived = 1
	    t.add_source(slist)

	if len(tlist) == 1:
	    tlist = tlist[0]
	return tlist

    def execute(self, **kw):
	"""Execute a builder's action to create an output object.
	"""
	return apply(self.action.execute, (), kw)



print_actions = 1;
execute_actions = 1;



def Action(act):
    """A factory for action objects."""
    if type(act) == types.StringType:
	l = string.split(act, "\n")
	if len(l) > 1:
	    act = l
    if callable(act):
	return FunctionAction(act)
    elif type(act) == types.StringType:
	return CommandAction(act)
    elif type(act) == types.ListType:
	return ListAction(act)
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
	ret = 0
	if execute_actions:
	    pid = os.fork()
	    if not pid:
		# Child process.
		args = string.split(cmd)
		try:
		    ENV = kw['ENV']
		except:
		    import SCons.Defaults
		    ENV = SCons.Defaults.ENV
		os.execvpe(args[0], args, ENV)
	    else:
		# Parent process.
		pid, stat = os.waitpid(pid, 0)
		ret = stat >> 8
	return ret



class FunctionAction(ActionBase):
    """Class for Python function actions."""
    def __init__(self, function):
	self.function = function

    def execute(self, **kw):
	# if print_actions:
	# XXX:  WHAT SHOULD WE PRINT HERE?
	if execute_actions:
	    return self.function(kw)

class ListAction(ActionBase):
    """Class for lists of other actions."""
    def __init__(self, list):
	self.list = map(lambda x: Action(x), list)

    def execute(self, **kw):
	for l in self.list:
	    r = apply(l.execute, (), kw)
	    if r != 0:
		return r
	return 0
