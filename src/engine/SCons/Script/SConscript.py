"""SCons.Script.SConscript

This module defines the Python API provided to SConscript and SConstruct 
files.

"""

#
# __COPYRIGHT__
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

import SCons.Action
import SCons.Builder
import SCons.Defaults
import SCons.Environment
import SCons.Errors
import SCons.Node
import SCons.Node.FS
import SCons.Platform
import SCons.Tool
import SCons.Util
import SCons.Options
import SCons

import os
import os.path
import string
import sys

def do_nothing(text): pass
HelpFunction = do_nothing

default_targets = []
clean_targets = {}
arguments = {}
launch_dir = os.path.abspath(os.curdir)

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

# This function is responsible for converting the parameters passed to
# SConscript() calls into a list of files and export variables.  If
# the parameters are invalid, throws SCons.Errors.UserError. Returns a
# tuple (l, e) where l is a list of filenames and e is a list of
# exports.

def GetSConscriptFilenames(ls, kw):
    files = []
    exports = []

    if len(ls) == 0:
        try:
            dirs = map(str, SCons.Util.argmunge(kw["dirs"]))
        except KeyError:
            raise SCons.Errors.UserError, \
                  "Invalid SConscript usage - no parameters"

        name = kw.get('name', 'SConscript')

        if kw.get('exports'):
            exports = SCons.Util.argmunge(kw['exports'])

        files = map(lambda n, name = name: os.path.join(n, name), dirs)

    elif len(ls) == 1:

        files = SCons.Util.argmunge(ls[0])
        if kw.get('exports'):
            exports = SCons.Util.argmunge(kw['exports'])

    elif len(ls) == 2:

        files   = SCons.Util.argmunge(ls[0])
        exports = SCons.Util.argmunge(ls[1])

        if kw.get('exports'):
            exports.extend(SCons.Util.argmunge(kw.get('exports')))

    else:
        raise SCons.Errors.UserError, \
              "Invalid SConscript() usage - too many arguments"

    return (files, exports)

def SConscript(*ls, **kw):
    files, exports = GetSConscriptFilenames(ls, kw)

    # evaluate each SConscript file
    results = []
    for fn in files:
        stack.append(Frame(exports))
        old_dir = None
        old_sys_path = sys.path
        try:
            if fn == "-":
                exec sys.stdin in stack[-1].globals
            else:
                if isinstance(fn, SCons.Node.Node):
                    f = fn
                else:
                    f = SCons.Node.FS.default_fs.File(str(fn))
                if f.rexists():
                    file = open(f.rstr(), "r")
                    SCons.Node.FS.default_fs.chdir(f.dir)
                    if sconscript_chdir:
                        old_dir = os.getcwd()
                        os.chdir(str(f.dir))

                    # prepend the SConscript directory to sys.path so
                    # that Python modules in the SConscript directory can
                    # be easily imported
                    sys.path = [os.path.abspath(str(f.dir))] + sys.path

                    exec file in stack[-1].globals
                else:
                    sys.stderr.write("Ignoring missing SConscript '%s'\n" %
                                     f.path)
                
        finally:
            sys.path = old_sys_path
            frame = stack.pop()
            SCons.Node.FS.default_fs.chdir(frame.prev_dir)
            if old_dir:
                os.chdir(old_dir)

            results.append(frame.retval)

    # if we only have one script, don't return a tuple
    if len(results) == 1:
        return results[0]
    else:
        return tuple(results)
    
def Default(*targets):
    for t in targets:
        if isinstance(t, SCons.Node.Node):
            default_targets.append(t)
        else:
            default_targets.extend(SCons.Node.arg2nodes(t,
                                         SCons.Node.FS.default_fs.Entry))

def Local(*targets):
    for targ in targets:
        if isinstance(targ, SCons.Node.Node):
            targ.set_local()
        else:
            for t in SCons.Node.arg2nodes(targ, SCons.Node.FS.default_fs.Entry):
               t.set_local()

def Help(text):
    HelpFunction(text)

def BuildDir(build_dir, src_dir, duplicate=1):
    SCons.Node.FS.default_fs.BuildDir(build_dir, src_dir, duplicate)

def GetBuildPath(files):
    nodes = SCons.Node.arg2nodes(files, SCons.Node.FS.default_fs.Entry)
    ret = map(str, nodes)
    if len(ret) == 1:
        return ret[0]
    return ret

def FindFile(file, dirs):
    nodes = SCons.Node.arg2nodes(dirs, SCons.Node.FS.default_fs.Dir)
    return SCons.Node.FS.find_file(file, nodes)

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

def GetLaunchDir():
    return launch_dir

def SetBuildSignatureType(type):
    import SCons.Sig
    if type == 'build':
        SCons.Sig.build_signature = 1
    elif type == 'content':
        SCons.Sig.build_signature = 0
    else:
        raise SCons.Errors.UserError, "Unknown build signature type '%s'"%type

def SetContentSignatureType(type):
    import SCons.Script
    if type == 'MD5':
        import SCons.Sig.MD5
        SCons.Script.sig_module = SCons.Sig.MD5
    elif type == 'timestamp':
        import SCons.Sig.TimeStamp
        SCons.Script.sig_module = SCons.Sig.TimeStamp
    else:
        raise SCons.Errors.UserError, "Unknown content signature type '%s'"%type


class Options(SCons.Options.Options):
    def Update(self, env):
        return SCons.Options.Options.Update(self, env, arguments)

def CheckVersion(major,minor,version_string):
    """Return 0 if 'major' and 'minor' are greater than the version
    in 'version_string', and 1 otherwise."""
    version = string.split(string.split(version_string, ' ')[0], '.')
    if major > int(version[0]) or (major == int(version[0]) and minor > int(version[1])):
        return 0
    else:
        return 1

def EnsureSConsVersion(major, minor):
    """Exit abnormally if the SCons version is not late enough."""
    if not CheckVersion(major,minor,SCons.__version__):
        print "SCons %d.%d or greater required, but you have SCons %s" %(major,minor,SCons.__version__)
        sys.exit(2)

def EnsurePythonVersion(major, minor):
    """Exit abnormally if the Python version is not late enough."""
    if not CheckVersion(major,minor,sys.version):
	v = string.split(sys.version, " ", 1)[0]
        print "Python %d.%d or greater required, but you have Python %s" %(major,minor,v)
        sys.exit(2)

def GetJobs():
    return SCons.Script.get_num_jobs(SCons.Script.options)

def SetJobs(num):
    try:
        tmp = int(num)
        if tmp < 1:
            raise ValueError
        SCons.Script.num_jobs = tmp
    except ValueError, x:
        raise SCons.Errors.UserError, "A positive integer is required: %s"%repr(num)
    
def Clean(target, files):
    if not isinstance(target, SCons.Node.Node):
        target = SCons.Node.FS.default_fs.Entry(target, create=1)

    if not SCons.Util.is_List(files):
        files = [files]

    nodes = []
    for f in files:
        if isinstance(f, SCons.Node.Node):
            nodes.append(f)
        else:
            nodes.extend(SCons.Node.arg2nodes(f, SCons.Node.FS.default_fs.Entry))

    s = str(target)
    if clean_targets.has_key(s):
        clean_targets[s].extend(nodes)
    else:
        clean_targets[s] = nodes

def AddPreAction(files, action):
    nodes = SCons.Node.arg2nodes(files, SCons.Node.FS.default_fs.Entry)
    for n in nodes:
        n.add_pre_action(SCons.Action.Action(action))

def AddPostAction(files, action):
    nodes = SCons.Node.arg2nodes(files, SCons.Node.FS.default_fs.Entry)
    for n in nodes:
        n.add_post_action(SCons.Action.Action(action))

def BuildDefaultGlobals():
    """
    Create a dictionary containing all the default globals for 
    SConscruct and SConscript files.
    """

    globals = {}
    globals['Action']            = SCons.Action.Action
    globals['AddPostAction']     = AddPostAction
    globals['AddPreAction']      = AddPreAction
    globals['ARGUMENTS']         = arguments
    globals['BuildDir']          = BuildDir
    globals['Builder']           = SCons.Builder.Builder
    globals['Clean']             = Clean
    globals['CScan']             = SCons.Defaults.CScan
    globals['Default']           = Default
    globals['Dir']               = SCons.Node.FS.default_fs.Dir
    globals['EnsurePythonVersion'] = EnsurePythonVersion
    globals['EnsureSConsVersion'] = EnsureSConsVersion
    globals['Environment']       = SCons.Environment.Environment
    globals['Export']            = Export
    globals['File']              = SCons.Node.FS.default_fs.File
    globals['FindFile']          = FindFile
    globals['GetBuildPath']      = GetBuildPath
    globals['GetCommandHandler'] = SCons.Action.GetCommandHandler
    globals['GetJobs']           = GetJobs
    globals['GetLaunchDir']      = GetLaunchDir
    globals['Help']              = Help
    globals['Import']            = Import
    globals['Library']           = SCons.Defaults.StaticLibrary
    globals['Literal']           = SCons.Util.Literal
    globals['Local']             = Local
    globals['Object']            = SCons.Defaults.StaticObject
    globals['Options']           = Options
    globals['ParseConfig']       = SCons.Util.ParseConfig
    globals['Platform']          = SCons.Platform.Platform
    globals['Program']           = SCons.Defaults.Program
    globals['Repository']        = SCons.Node.FS.default_fs.Repository
    globals['Return']            = Return
    globals['SConscript']        = SConscript
    globals['SConscriptChdir']   = SConscriptChdir
    globals['Scanner']           = SCons.Scanner.Base
    globals['SetBuildSignatureType'] = SetBuildSignatureType
    globals['SetCommandHandler'] = SCons.Action.SetCommandHandler
    globals['SetContentSignatureType'] = SetContentSignatureType
    globals['SetJobs']           = SetJobs
    globals['SharedLibrary']     = SCons.Defaults.SharedLibrary
    globals['SharedObject']      = SCons.Defaults.SharedObject
    globals['Split']             = SCons.Util.Split
    globals['StaticLibrary']     = SCons.Defaults.StaticLibrary
    globals['StaticObject']      = SCons.Defaults.StaticObject
    globals['Tool']              = SCons.Tool.Tool
    globals['WhereIs']           = SCons.Util.WhereIs
    return globals
