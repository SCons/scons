"""SCons.Environment

XXX

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



import copy
import re
import types



def Command():
    pass	# XXX

def Install():
    pass	# XXX

def InstallAs():
    pass	# XXX



_cv = re.compile(r'%([_a-zA-Z]\w*|{[_a-zA-Z]\w*})')
_self = None



def _deepcopy_atomic(x, memo):
	return x
copy._deepcopy_dispatch[types.ModuleType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.ClassType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.FunctionType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.MethodType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.TracebackType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.FrameType] = _deepcopy_atomic
copy._deepcopy_dispatch[types.FileType] = _deepcopy_atomic



class Environment:
    """Base class for construction Environments.  These are
    the primary objects used to communicate dependency and
    construction information to the build engine.

    Keyword arguments supplied when the construction Environment
    is created are construction variables used to initialize the
    Environment.
    """

    def __init__(self, **kw):
	self.Dictionary = {}
	if kw.has_key('BUILDERS'):
	    builders = kw['BUILDERS']
	    if not type(builders) is types.ListType:
		kw['BUILDERS'] = [builders]
	else:
	    import SCons.Defaults
	    kw['BUILDERS'] = SCons.Defaults.Builders[:]
	self.Dictionary.update(copy.deepcopy(kw))

	class BuilderWrapper:
	    """Wrapper class that allows an environment to
	    be associated with a Builder at instantiation.
	    """
	    def __init__(self, env, builder):
		self.env = env
		self.builder = builder
	
	    def __call__(self, target = None, source = None):
		return self.builder(self.env, target, source)

	    def execute(self, **kw):
		apply(self.builder.execute, (), kw)

	for b in kw['BUILDERS']:
	    setattr(self, b.name, BuilderWrapper(self, b))



    def __cmp__(self, other):
	return cmp(self.Dictionary, other.Dictionary)

    def Builders(self):
	pass	# XXX

    def Copy(self, **kw):
	"""Return a copy of a construction Environment.  The
	copy is like a Python "deep copy"--that is, independent
	copies are made recursively of each objects--except that
	a reference is copied when an object is not deep-copyable
	(like a function).  There are no references to any mutable
	objects in the original Environment.
	"""
	clone = copy.deepcopy(self)
	apply(clone.Update, (), kw)
	return clone

    def Scanners(self):
	pass	# XXX

    def	Update(self, **kw):
	"""Update an existing construction Environment with new
	construction variables and/or values.
	"""
	self.Dictionary.update(copy.deepcopy(kw))

    def subst(self, string):
	"""Recursively interpolates construction variables from the
	Environment into the specified string, returning the expanded
	result.  Construction variables are specified by a % prefix
	in the string and begin with an initial underscore or
	alphabetic character followed by any number of underscores
	or alphanumeric characters.  The construction variable names
	may be surrounded by curly braces to separate the name from
	trailing characters.
	"""
	global _self
	_self = self	# XXX NOT THREAD SAFE, BUT HOW ELSE DO WE DO THIS?
	def repl(m):
	    key = m.group(1)
	    if key[:1] == '{' and key[-1:] == '}':
		key = key[1:-1]
	    if _self.Dictionary.has_key(key): return _self.Dictionary[key]
	    else: return ''
	n = 1
	while n != 0:
	    string, n = _cv.subn(repl, string)
	return string
