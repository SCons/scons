"""SCons.Util

Various utility functions go here.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"


import types
import string
import SCons.Node.FS

def scons_str2nodes(arg, fs=SCons.Node.FS.default_fs):
    """This function converts a string or list into a list of Node instances.
    It follows the rules outlined in the SCons design document by accepting
    any of the following inputs:
	- A single string containing names separated by spaces. These will be
	  split apart at the spaces.
	- A single Node instance,
	- A list containingg either strings or Node instances. Any strings
	  in the list are not split at spaces.
    In all cases, the function returns a list of Node instances."""

    narg = arg
    if type(arg) is types.StringType:
	narg = string.split(arg)
    elif type(arg) is not types.ListType:
	narg = [arg]

    nodes = []
    for v in narg:
	if type(v) is types.StringType:
	    nodes.append(fs.File(v))
	elif issubclass(v.__class__, SCons.Node.Node):
	    nodes.append(v)
	else:
	    raise TypeError

    return nodes
