"""engine.SCons.SConscript

This module defines the Python API provided to SConscript and SConstruct 
files.

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

import SCons.Builder
import SCons.Defaults
import SCons.Environment
import SCons.Errors
import SCons.Node
import SCons.Node.FS
import SCons.Util

import os
import os.path
import string
import sys

default_targets = []
print_help = 0
arguments = {}

# global exports set by Export():
global_exports = {}

# chdir flag
sconscript_chdir = 0

def SConscriptChdir(flag):
    global sconscript_chdir
    sconscript_chdir = flag

def _scons_add_args(alist):
    global arguments
    for arg in alist:
        a, b = string.split(arg, '=', 2)
        arguments[a] = b

class Frame:
    """A frame on the SConstruct/SConscript call stack"""
    def __init__(self, exports):
        self.globals = BuildDefaultGlobals()
        self.retval = None 
        self.prev_dir = SCons.Node.FS.default_fs.getcwd()
        self.exports = {} # exports from the calling SConscript

        try:
            if SCons.Util.is_List(exports):
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
    old_dir = None
    old_sys_path = sys.path
    try:
        # call:
        if script == "-":
            exec sys.stdin in stack[-1].globals
        else:
            if not isinstance(script, SCons.Node.Node):
                script = SCons.Node.FS.default_fs.File(script)
            if script.exists():
                file = open(str(script), "r")
                SCons.Node.FS.default_fs.chdir(script.dir)
                if sconscript_chdir:
                    old_dir = os.getcwd()
                    os.chdir(str(script.dir))

                # prepend the SConscript directory to sys.path so
                # that Python modules in the SConscript directory can
                # be easily imported.
                sys.path = [os.path.abspath(str(script.dir))] + sys.path

                exec file in stack[-1].globals
            else:
                sys.stderr.write("Ignoring missing SConscript '%s'\n" % script.path)
    finally:
        # pop:
        sys.path = old_sys_path
        frame = stack.pop()
        SCons.Node.FS.default_fs.chdir(frame.prev_dir)
        if old_dir:
            os.chdir(old_dir)
    
    return frame.retval
    
def Default(*targets):
    for t in targets:
        if isinstance(t, SCons.Node.Node):
            default_targets.append(t)
        else:
            default_targets.extend(SCons.Node.arg2nodes(t,
                                         SCons.Node.FS.default_fs.Entry))

def Help(text):
    if print_help:
        print text
        print "Use scons -H for help about command-line options."
        sys.exit(0)

def BuildDir(build_dir, src_dir, duplicate=1):
    SCons.Node.FS.default_fs.BuildDir(build_dir, src_dir, duplicate)

def GetBuildPath(files):
    nodes = SCons.Node.arg2nodes(files, SCons.Node.FS.default_fs.Entry)
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
    globals['Action']            = SCons.Action.Action
    globals['ARGUMENTS']         = arguments
    globals['BuildDir']          = BuildDir
    globals['Builder']           = SCons.Builder.Builder
    globals['CScan']             = SCons.Defaults.CScan
    globals['Default']           = Default
    globals['Dir']               = SCons.Node.FS.default_fs.Dir
    globals['Environment']       = SCons.Environment.Environment
    globals['Export']            = Export
    globals['File']              = SCons.Node.FS.default_fs.File
    globals['GetBuildPath']      = GetBuildPath
    globals['GetCommandHandler'] = SCons.Action.GetCommandHandler
    globals['Help']              = Help
    globals['Import']            = Import
    globals['Library']           = SCons.Defaults.Library
    globals['Object']            = SCons.Defaults.Object
    globals['Program']           = SCons.Defaults.Program
    globals['Return']            = Return
    globals['Scanner']           = SCons.Scanner.Base
    globals['SConscript']        = SConscript
    globals['SConscriptChdir']   = SConscriptChdir
    globals['SetCommandHandler'] = SCons.Action.SetCommandHandler
    globals['WhereIs']           = SCons.Util.WhereIs
    return globals
