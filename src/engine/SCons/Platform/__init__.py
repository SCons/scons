"""SCons.Platform

SCons platform selection.

This looks for modules that define a callable object that can modify a
construction environment as appropriate for a given platform.

Note that we take a more simplistic view of "platform" than Python does.
We're looking for a single string that determines a set of
tool-independent variables with which to initialize a construction
environment.  Consequently, we'll examine both sys.platform and os.name
(and anything else that might come in to play) in order to return some
specification which is unique enough for our purposes.

Note that because this subsysem just *selects* a callable that can
modify a construction environment, it's possible for people to define
their own "platform specification" in an arbitrary callable function.
No one needs to use or tie in to this subsystem in order to roll
their own platform definition.
"""

#
# Copyright (c) 2001, 2002 Steven Knight
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

import imp
import os
import sys

import SCons.Errors

def platform_default():
    """Return the platform string for our execution environment.

    The returned value should map to one of the SCons/Platform/*.py
    files.  Since we're architecture independent, though, we don't
    care about the machine architecture.
    """
    if os.name == 'posix':
        if sys.platform == 'cygwin':
            return 'cygwin'
	return 'posix'
    else:
        return sys.platform

def platform_module(name = platform_default()):
    """Return the imported module for the platform.

    This looks for a module name that matches the specified argument.
    If the name is unspecified, we fetch the appropriate default for
    our execution environment.
    """
    full_name = 'SCons.Platform.' + name
    if not sys.modules.has_key(full_name):
        try:
            file, path, desc = imp.find_module(name,
                                        sys.modules['SCons.Platform'].__path__)
            imp.load_module(full_name, file, path, desc)
        except ImportError:
            raise SCons.Errors.UserError, "No platform named '%s'" % name
        if file:
            file.close()
    return sys.modules[full_name]

def DefaultToolList(name = platform_default()):
    """Select a default tool list for the specified platform.
    """
    module = platform_module(name)
    return module.tool_list()

class PlatformSpec:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
def Platform(name = platform_default()):
    """Select a canned Platform specification.
    """
    module = platform_module(name)
    spec = PlatformSpec(name)
    spec.__call__ = module.generate
    return spec
