"""SCons.Util

Various utility functions go here.

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


import types
import string
import SCons.Node.FS

def scons_str2nodes(arg, node_factory=SCons.Node.FS.default_fs.File):
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
	    nodes.append(node_factory(v))
	# Do we enforce the following restriction?  Maybe, but it
	# also restricts what we can do for allowing people to
	# use the engine with alternate Node implementations...
	# Perhaps this should be split in two, with the SCons.Node
	# logic in a wrapper somewhere under SCons.Node, and the
	# string-parsing logic here...?
	#elif not issubclass(v.__class__, SCons.Node.Node):
	#    raise TypeError
	else:
	    nodes.append(v)

    return nodes
