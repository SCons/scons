"""SCons.Tool.mslink

Tool-specific initialization for the Microsoft linker.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

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

import os.path
import string

import SCons.Action
import SCons.Defaults
import SCons.Errors
import SCons.Util
import msvc

from SCons.Platform.win32 import TempFileMunge
from SCons.Tool.msvc import get_msdev_paths
    
def win32LinkGenerator(env, target, source, for_signature):
    args = [ '$LINK', '$LINKFLAGS', '/OUT:%s' % target[0],
             '$(', '$_LIBDIRFLAGS', '$)', '$_LIBFLAGS' ]
    
    if env.has_key('PDB') and env['PDB']:
        args.extend(['/PDB:%s'%target[0].File(env['PDB']), '/DEBUG'])

    args.extend(map(SCons.Util.to_String, source))
    return TempFileMunge(env, args, for_signature)

def win32LibGenerator(target, source, env, for_signature):
    listCmd = [ "$SHLINK", "$SHLINKFLAGS" ]
    no_import_lib = env.get('no_import_lib', 0)

    if env.has_key('PDB') and env['PDB']:
        listCmd.extend(['/PDB:%s'%target[0].File(env['PDB']), '/DEBUG'])

    for tgt in target:
        ext = os.path.splitext(str(tgt))[1]
        if ext == env.subst("$LIBSUFFIX"):
            # Put it on the command line as an import library.
            if no_import_lib:
                raise SCons.Errors.UserError, "%s: You cannot specify a .lib file as a target of a shared library build if no_import_library is nonzero." % tgt
            listCmd.append("${WIN32IMPLIBPREFIX}%s" % tgt)
        else:
            listCmd.append("${WIN32DLLPREFIX}%s" % tgt)

    listCmd.extend([ '$_LIBDIRFLAGS', '$_LIBFLAGS' ])
    for src in source:
        ext = os.path.splitext(str(src))[1]
        if ext == env.subst("$WIN32DEFSUFFIX"):
            # Treat this source as a .def file.
            listCmd.append("${WIN32DEFPREFIX}%s" % src)
        else:
            # Just treat it as a generic source file.
            listCmd.append(str(src))

    return TempFileMunge(env, listCmd, for_signature)

def win32LibEmitter(target, source, env):
    msvc.validate_vars(env)
    
    dll = None
    no_import_lib = env.get('no_import_lib', 0)
    
    for tgt in target:
        ext = os.path.splitext(str(tgt))[1]
        if ext == env.subst("$SHLIBSUFFIX"):
            dll = tgt
            break
    if not dll:
        raise SCons.Errors.UserError, "A shared library should have exactly one target with the suffix: %s" % env.subst("$SHLIBSUFFIX")

    if env.has_key("WIN32_INSERT_DEF") and \
       env["WIN32_INSERT_DEF"] and \
       not '.def' in map(lambda x: os.path.splitext(str(x))[1],
                         source):

        # append a def file to the list of sources
        source.append("%s%s" % (os.path.splitext(str(dll))[0],
                                env.subst("$WIN32DEFSUFFIX")))

    if env.has_key('PDB') and env['PDB']:
        env.SideEffect(env['PDB'], target)
        env.Precious(env['PDB'])

    if not no_import_lib and \
       not env.subst("$LIBSUFFIX") in \
       map(lambda x: os.path.splitext(str(x))[1], target):
        # Append an import library to the list of targets.
        target.append("%s%s%s" % (env.subst("$LIBPREFIX"),
                                  os.path.splitext(str(dll))[0],
                                  env.subst("$LIBSUFFIX")))
    return (target, source)

def prog_emitter(target, source, env):
    msvc.validate_vars(env)
    
    if env.has_key('PDB') and env['PDB']:
        env.SideEffect(env['PDB'], target)
        env.Precious(env['PDB'])
        
    return (target,source)

ShLibAction = SCons.Action.CommandGenerator(win32LibGenerator)
LinkAction = SCons.Action.CommandGenerator(win32LinkGenerator)

def generate(env, platform):
    """Add Builders and construction variables for ar to an Environment."""
    env['BUILDERS']['SharedLibrary'] = SCons.Defaults.SharedLibrary
    env['BUILDERS']['Program'] = SCons.Defaults.Program
    
    env['SHLINK']      = '$LINK'
    env['SHLINKFLAGS'] = '$LINKFLAGS /dll'
    env['SHLINKCOM']   = ShLibAction
    env['SHLIBEMITTER']= win32LibEmitter
    env['LINK']        = 'link'
    env['LINKFLAGS']   = '/nologo'
    env['LINKCOM']     = LinkAction
    env['PROGEMITTER'] = prog_emitter
    env['LIBDIRPREFIX']='/LIBPATH:'
    env['LIBDIRSUFFIX']=''
    env['LIBLINKPREFIX']=''
    env['LIBLINKSUFFIX']='$LIBSUFFIX'

    env['WIN32DEFPREFIX']        = '/def:'
    env['WIN32DEFSUFFIX']        = '.def'
    env['WIN32DLLPREFIX']        = '/out:'
    env['WIN32IMPLIBPREFIX']     = '/implib:'
    env['WIN32_INSERT_DEF']      = 0

    include_path, lib_path, exe_path = get_msdev_paths()
    env['ENV']['LIB']            = lib_path
    env['ENV']['PATH']           = exe_path

def exists(env):
    return env.Detect('link')
