"""SCons.Builder

XXX

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
	tlist = SCons.Util.scons_str2nodes(target, self.node_factory)
	slist = SCons.Util.scons_str2nodes(source, self.node_factory)
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

class BuilderProxy:
    """This base class serves as a proxy to a builder object,
    exposing the same interface, but just forwarding calls to
    the underlying object."""
    def __init__(self, builder):
        self.subject = builder

    def __call__(self, env, target = None, source = None):
        return self.subject.__call__(env, target, source)

    def execute(self, **kw):
        return apply(self.subject.execute, (), kw)
    
    def __cmp__(self, other):
        return cmp(self.__dict__, other.__dict__)

    def __getattr__(self, name):
        assert 'subject' in self.__dict__.keys(), \
               "You must call __init__() on the BuilderProxy base."
        return getattr(self.subject, name)
    
class TargetNamingBuilder(BuilderProxy):
    """This is a simple Builder Proxy that decorates the names
    of a Builder's targets prior to passing them to the underlying
    Builder.  You can use this to simplify the syntax of a target
    file.  For instance, you might want to call a Library builder
    with a target of "foo" and expect to get "libfoo.a" back."""

    def __init__(self, builder, prefix='', suffix=''):
        """
        builder - The underlying Builder object
        
        prefix - text to prepend to target names (may contain
        environment variables)

        suffix - text to append to target names (may contain
        environment variables)
        """
        BuilderProxy.__init__(self, builder)
        self.prefix=prefix
        self.suffix=suffix

    def __call__(self, env, target = None, source = None):
        tlist = SCons.Util.scons_str2nodes(target,
                                           self.subject.node_factory)
        tlist_decorated = []
        for tnode in tlist:
            path, fn = os.path.split(tnode.path)
            tlist_decorated.append(self.subject.
                                   node_factory(os.path.join(path,
                                                             env.subst(self.prefix) +
                                                             fn +
                                                             env.subst(self.suffix))))
        return self.subject.__call__(env, target=tlist_decorated, source=source)

class MultiStepBuilder(Builder):
    """This is a builder subclass that can build targets in
    multiple steps according to the suffixes of the source files.
    Given one or more "subordinate" builders in its constructor,
    this class will apply those builders to any files matching
    the builder's input_suffix, using a file of the same name
    as the source, but with input_suffix changed to output_suffix.
    The targets of these builders then become sources for this
    builder.
    """
    def __init__(self,  name = None,
			action = None,
			input_suffix = None,
			output_suffix = None,
                        node_factory = SCons.Node.FS.default_fs.File,
                        builders = []):
        Builder.__init__(self, name, action, input_suffix, output_suffix,
                         node_factory)
        self.builder_dict = {}
        for bld in builders:
            if bld.insuffix and bld.outsuffix:
                self.builder_dict[bld.insuffix] = bld

    def __call__(self, env, target = None, source = None):
        slist = SCons.Util.scons_str2nodes(source, self.node_factory)
        final_sources = []
        for snode in slist:
            path, ext = os.path.splitext(snode.path)
            if self.builder_dict.has_key(ext):
                bld = self.builder_dict[ext]
                tgt = bld(env,
                          target=[ path+bld.outsuffix, ],
                          source=snode)
                if not type(tgt) is types.ListType:
                    final_sources.append(tgt)
                else:
                    final_sources.extend(tgt)
            else:
                final_sources.append(snode)
        return Builder.__call__(self, env, target=target,
                                source=final_sources)

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
