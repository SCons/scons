"""SCons.Tool

SCons tool selection.

This looks for modules that define a callable object that can modify
a construction environment as appropriate for a given tool (or tool
chain).

Note that because this subsysem just *selects* a callable that can
modify a construction environment, it's possible for people to define
their own "tool specification" in an arbitrary callable function.  No
one needs to use or tie in to this subsystem in order to roll their own
tool definition.
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
import SCons.Defaults

class ToolSpec:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
    
def Tool(name, platform = None):
    """Select a canned Tool specification.
    """
    full_name = 'SCons.Tool.' + name
    if not sys.modules.has_key(full_name):
        try:
            file, path, desc = imp.find_module(name,
                                        sys.modules['SCons.Tool'].__path__)
            imp.load_module(full_name, file, path, desc)
        except ImportError:
            raise SCons.Errors.UserError, "No tool named '%s'" % name
        if file:
            file.close()
    spec = ToolSpec(name)
    spec.__call__ = sys.modules[full_name].generate
    return spec

def createObjBuilders(env):
    """This is a utility function that creates the Object
    and SharedObject Builders in an Environment if they
    are not there already.

    If they are there already, we return the existing ones.

    This is a separate function because soooo many Tools
    use this functionality.

    The return is a 2-tuple of (StaticObject, SharedObject)
    """

    try:
        static_obj = env['BUILDERS']['Object']
    except KeyError:
        static_obj = SCons.Defaults.StaticObject()
        env['BUILDERS']['Object'] = static_obj
        env['BUILDERS']['StaticObject'] = static_obj

    try:
        shared_obj = env['BUILDERS']['SharedObject']
    except KeyError:
        shared_obj = SCons.Defaults.SharedObject()
        env['BUILDERS']['SharedObject'] = shared_obj

    return (static_obj, shared_obj)

def createCFileBuilders(env):
    """This is a utility function that creates the CFile/CXXFile
    Builders in an Environment if they
    are not there already.

    If they are there already, we return the existing ones.

    This is a separate function because soooo many Tools
    use this functionality.

    The return is a 2-tuple of (CFile, CXXFile)
    """

    try:
        c_file = env['BUILDERS']['CFile']
    except KeyError:
        c_file = SCons.Defaults.CFile()
        env['BUILDERS']['CFile'] = c_file

    try:
        cxx_file = env['BUILDERS']['CXXFile']
    except KeyError:
        cxx_file = SCons.Defaults.CXXFile()
        env['BUILDERS']['CXXFile'] = cxx_file

    return (c_file, cxx_file)
