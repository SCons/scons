"""engine.SCons.SConscript

This module defines the Python API provided to SConscript and SConstruct 
files.

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

__revision__ = "src/engine/SCons/SConscript.py __REVISION__ __DATE__ __DEVELOPER__"

import SCons.Errors
import SCons.Builder
import SCons.Defaults
import SCons.Node
import SCons.Node.FS
import SCons.Environment
import string
import sys

default_targets = []
print_help = 0

# global exports set by Export():
global_exports = {}

class Frame:
    """A frame on the SConstruct/SConscript call stack"""
    def __init__(self, exports):
        self.globals = BuildDefaultGlobals()
        self.retval = None 
        self.prev_dir = SCons.Node.FS.default_fs.getcwd()
        self.exports = {} # exports from the calling SConscript

        try:
            if type(exports) == type([]):
                for export in exports:
                    self.exports[export] = stack[-1].globals[export]
            else:
                for export in string.split(exports):
                    self.exports[export] = stack[-1].globals[export]
        except KeyError, x:
            raise SCons.Errors.UserError, "Export of non-existant variable '%s'"%x

        
# the SConstruct/SConscript call stack:
stack = []

# For documentation on the methods in this file, see the scons man-page

def Return(*vars):
    retval = []
    try:
        for var in vars:
            for v in string.split(var):
                retval.append(stack[-1].globals[v])
    except KeyError, x:
        raise SCons.Errors.UserError, "Return of non-existant variable '%s'"%x
        
    if len(retval) == 1:
        stack[-1].retval = retval[0]
    else:
        stack[-1].retval = tuple(retval)

def SConscript(script, exports=[]):
    retval = ()

    # push:
    stack.append(Frame(exports))

    # call:
    if script == "-":
        exec sys.stdin in stack[-1].globals
    else:
        f = SCons.Node.FS.default_fs.File(script)
        if f.exists():
            file = open(str(f), "r")
            SCons.Node.FS.default_fs.chdir(f.dir)
            exec file in stack[-1].globals
        else:
            sys.stderr.write("Ignoring missing SConscript '%s'\n" % f.path)
    

    # pop:
    frame = stack.pop()
    SCons.Node.FS.default_fs.chdir(frame.prev_dir)
    
    return frame.retval
    
def Default(*targets):
    for t in targets:
        if isinstance(t, SCons.Node.Node):
            default_targets.append(t)
        else:
            for s in string.split(t):
                default_targets.append(s)

def Help(text):
    if print_help:
        print text
        print "Use scons -H for help about command-line options."
        sys.exit(0)

def BuildDir(build_dir, src_dir):
    SCons.Node.FS.default_fs.BuildDir(build_dir, src_dir)

def GetBuildPath(files):
    nodes = SCons.Util.scons_str2nodes(files,
                                       SCons.Node.FS.default_fs.Entry)
    ret = map(str, nodes)
    if len(ret) == 1:
        return ret[0]
    return ret

def Export(*vars):
    try:
        for var in vars:
            for v in string.split(var):
                global_exports[v] = stack[-1].globals[v]
    except KeyError, x:
        raise SCons.Errors.UserError, "Export of non-existant variable '%s'"%x

def Import(*vars):
    try:
        for var in vars:
            for v in string.split(var):
                if stack[-1].exports.has_key(v):
                    stack[-1].globals[v] = stack[-1].exports[v]
                else:
                    stack[-1].globals[v] = global_exports[v]
    except KeyError,x:
        raise SCons.Errors.UserError, "Import of non-existant variable '%s'"%x

def BuildDefaultGlobals():
    """
    Create a dictionary containing all the default globals for 
    SConscruct and SConscript files.
    """

    globals = {}
    globals['Builder'] = SCons.Builder.Builder
    globals['Environment'] = SCons.Environment.Environment
    globals['Object'] = SCons.Defaults.Object
    globals['Program'] = SCons.Defaults.Program
    globals['Library'] = SCons.Defaults.Library
    globals['CScan'] = SCons.Defaults.CScan
    globals['SConscript'] = SConscript
    globals['Default'] = Default
    globals['Help'] = Help
    globals['BuildDir'] = BuildDir
    globals['GetBuildPath'] = GetBuildPath
    globals['Export'] = Export
    globals['Import'] = Import
    globals['Return'] = Return
    return globals
