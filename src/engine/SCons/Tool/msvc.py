"""engine.SCons.Tool.msvc

Tool-specific initialization for Microsoft Visual C/C++.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

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

import os.path
import string
import types
import re

import SCons.Action
import SCons.Tool
import SCons.Errors
import SCons.Warnings
import SCons.Builder
import SCons.Util
import SCons.Platform.win32
import SCons.Tool.msvs

CSuffixes = ['.c', '.C']
CXXSuffixes = ['.cc', '.cpp', '.cxx', '.c++', '.C++']

def _parse_msvc7_overrides(version):
    """ Parse any overridden defaults for MSVS directory locations in MSVS .NET. """
    
    # First, we get the shell folder for this user:
    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    comps = ""
    try:
        (comps, t) = SCons.Util.RegGetValue(SCons.Util.HKEY_CURRENT_USER,
                                            r'Software\Microsoft\Windows\CurrentVersion' +\
                                            r'\Explorer\Shell Folders\Local AppData')
    except SCons.Util.RegError:
        raise SCons.Errors.InternalError, "The Local AppData directory was not found in the registry."

    comps = comps + '\\Microsoft\\VisualStudio\\' + version + '\\VSComponents.dat'
    dirs = {}

    if os.path.exists(comps):
        # now we parse the directories from this file, if it exists.
        # We only look for entries after: [VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories],
        # since this file could contain a number of things...
        f = open(comps,'r')
        line = f.readline()
        found = 0
        while line:
            line.strip()
            if found == 1:
                (key, val) = line.split('=',1)
                key = key.replace(' Dirs','')
                dirs[key.upper()] = val
            if line.find(r'[VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories]') >= 0:
                found = 1
            if line == '':
                found = 0
            line = f.readline()
        f.close()
    else:
        # since the file didn't exist, we have only the defaults in
        # the registry to work with.
        try:
            K = 'SOFTWARE\\Microsoft\\VisualStudio\\' + version
            K = K + r'\VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories'
            k = SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE,K)
            i = 0
            while 1:
                try:
                    (key,val,t) = SCons.Util.RegEnumValue(k,i)
                    key = key.replace(' Dirs','')
                    dirs[key.upper()] = val
                    i = i + 1
                except SCons.Util.RegError:
                    break
        except SCons.Util.RegError:
            # if we got here, then we didn't find the registry entries:
            raise SCons.Errors.InternalError, "Unable to find MSVC paths in the registry."
    return dirs

def _get_msvc7_path(path, version, platform):
    """
    Get Visual Studio directories from version 7 (MSVS .NET)
    (it has a different registry structure than versions before it)
    """
    # first, look for a customization of the default values in the
    # registry: These are sometimes stored in the Local Settings area
    # for Visual Studio, in a file, so we have to parse it.
    dirs = _parse_msvc7_overrides(version)

    if dirs.has_key(path):
        p = dirs[path]
    else:
        raise SCons.Errors.InternalError, "Unable to retrieve the %s path from MS VC++."%path

    # collect some useful information for later expansions...
    paths = SCons.Tool.msvs.get_msvs_install_dirs(version)

    # expand the directory path variables that we support.  If there
    # is a variable we don't support, then replace that entry with
    # "---Unknown Location VSInstallDir---" or something similar, to clue
    # people in that we didn't find something, and so env expansion doesn't
    # do weird things with the $(xxx)'s
    s = re.compile('\$\(([a-zA-Z0-9_]+?)\)')

    def repl(match):
        key = string.upper(match.group(1))
        if paths.has_key(key):
            return paths[key]
        else:
            return '---Unknown Location %s---' % match.group()

    rv = []
    for entry in p.split(os.pathsep):
        entry = s.sub(repl,entry)
        rv.append(entry)

    return string.join(rv,os.pathsep)

def get_msvc_path (path, version, platform='x86'):
    """
    Get a list of visualstudio directories (include, lib or path).  Return
    a string delimited by ';'. An exception will be raised if unable to
    access the registry or appropriate registry keys not found.
    """

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    # normalize the case for comparisons (since the registry is case
    # insensitive)
    path = string.upper(path)

    if path=='LIB':
        path= 'LIBRARY'

    if float(version) >= 7.0:
        return _get_msvc7_path(path, version, platform)

    path = string.upper(path + ' Dirs')
    K = ('Software\\Microsoft\\Devstudio\\%s\\' +
         'Build System\\Components\\Platforms\\Win32 (%s)\\Directories') % \
        (version,platform)
    for base in (SCons.Util.HKEY_CURRENT_USER,
                 SCons.Util.HKEY_LOCAL_MACHINE):
        try:
            k = SCons.Util.RegOpenKeyEx(base,K)
            i = 0
            while 1:
                try:
                    (p,v,t) = SCons.Util.RegEnumValue(k,i)
                    if string.upper(p) == path:
                        return v
                    i = i + 1
                except SCons.Util.RegError:
                    break
        except SCons.Util.RegError:
            pass

    # if we got here, then we didn't find the registry entries:
    raise SCons.Errors.InternalError, "The %s path was not found in the registry."%path

def _get_msvc6_default_paths(version):
    """Return a 3-tuple of (INCLUDE, LIB, PATH) as the values of those
    three environment variables that should be set in order to execute
    the MSVC 6.0 tools properly, if the information wasn't available
    from the registry."""
    MVSdir = None
    paths = {}
    exe_path = ''
    lib_path = ''
    include_path = ''
    try:
        paths = SCons.Tool.msvs.get_msvs_install_dirs(version)
        MVSdir = paths['VSINSTALLDIR']
    except (SCons.Util.RegError, SCons.Errors.InternalError, KeyError):
        if os.environ.has_key('MSDEVDIR'):
            MVSdir = os.path.normpath(os.path.join(os.environ['MSDEVDIR'],'..','..'))
        else:
            MVSdir = r'C:\Program Files\Microsoft Visual Studio'
    if MVSdir:
        if SCons.Util.can_read_reg and paths.has_key('VCINSTALLDIR'):
            MVSVCdir = paths['VCINSTALLDIR']
        else:
            MVSVCdir = os.path.join(MVSdir,'VC98')

        MVSCommondir = r'%s\Common' % MVSdir
        include_path = r'%s\ATL\include;%s\MFC\include;%s\include' % (MVSVCdir, MVSVCdir, MVSVCdir)
        lib_path = r'%s\MFC\lib;%s\lib' % (MVSVCdir, MVSVCdir)
        exe_path = r'%s\MSDev98\bin;%s\bin' % (MVSCommondir, MVSVCdir)
    return (include_path, lib_path, exe_path)

def _get_msvc7_default_paths(version):
    """Return a 3-tuple of (INCLUDE, LIB, PATH) as the values of those
    three environment variables that should be set in order to execute
    the MSVC .NET tools properly, if the information wasn't available
    from the registry."""
            
    MVSdir = None
    paths = {}
    exe_path = ''
    lib_path = ''
    include_path = ''
    try:
        paths = SCons.Tool.msvs.get_msvs_install_dirs(version)
        MVSdir = paths['VSINSTALLDIR']
    except (KeyError, SCons.Util.RegError, SCons.Errors.InternalError):
        if os.environ.has_key('VSCOMNTOOLS'):
            MVSdir = os.path.normpath(os.path.join(os.environ['VSCOMNTOOLS'],'..','..'))
        else:
            # last resort -- default install location
            MVSdir = r'C:\Program Files\Microsoft Visual Studio .NET'

    if not MVSdir:
        if SCons.Util.can_read_reg and paths.has_key('VCINSTALLDIR'):
            MVSVCdir = paths['VCINSTALLDIR']
        else:
            MVSVCdir = os.path.join(MVSdir,'Vc7')

        MVSCommondir = r'%s\Common7' % MVSdir
        include_path = r'%s\atlmfc\include;%s\include' % (MVSVCdir, MVSVCdir, MVSVCdir)
        lib_path = r'%s\atlmfc\lib;%s\lib' % (MVSVCdir, MVSVCdir)
        exe_path = r'%s\Tools\bin;%s\Tools;%s\bin' % (MVSCommondir, MVSCommondir, MVSVCdir)
    return (include_path, lib_path, exe_path)

def get_msvc_paths(version=None):
    """Return a 3-tuple of (INCLUDE, LIB, PATH) as the values
    of those three environment variables that should be set
    in order to execute the MSVC tools properly."""
    exe_path = ''
    lib_path = ''
    include_path = ''

    if not version and not SCons.Util.can_read_reg:
        version = '6.0'
            
    try:
        if not version:
            version = SCons.Tool.msvs.get_visualstudio_versions()[0] #use highest version

        include_path = get_msvc_path("include", version)
        lib_path = get_msvc_path("lib", version)
        exe_path = get_msvc_path("path", version)

    except (SCons.Util.RegError, SCons.Errors.InternalError):
        # Could not get all the configured directories from the
        # registry.  However, some of the configured directories only
        # appear if the user changes them from the default.
        # Therefore, we'll see if we can get the path to the MSDev
        # base installation from the registry and deduce the default
        # directories.
        if float(version) >= 7.0:
            return _get_msvc7_default_paths(version)
        else:
            return _get_msvc6_default_paths(version)
            
    return (include_path, lib_path, exe_path)

def get_msvc_default_paths(version = None):
    """Return a 3-tuple of (INCLUDE, LIB, PATH) as the values of those
    three environment variables that should be set in order to execute
    the MSVC tools properly.  This will only return the default
    locations for the tools, not the values used by MSVS in their
    directory setup area.  This can help avoid problems with different
    developers having different settings, and should allow the tools
    to run in most cases."""

    if not version and not SCons.Util.can_read_reg:
        version = '6.0'

    try:
        if not version:
            version = SCons.Tool.msvs.get_visualstudio_versions()[0] #use highest version
    except:
        pass

    if float(version) >= 7.0:
        return _get_msvc7_default_paths(version)
    else:
        return _get_msvc6_default_paths(version)

def validate_vars(env):
    """Validate the PDB, PCH, and PCHSTOP construction variables."""
    if env.has_key('PCH') and env['PCH']:
        if not env.has_key('PCHSTOP'):
            raise SCons.Errors.UserError, "The PCHSTOP construction must be defined if PCH is defined."
        if not SCons.Util.is_String(env['PCHSTOP']):
            raise SCons.Errors.UserError, "The PCHSTOP construction variable must be a string: %r"%env['PCHSTOP']

def pch_emitter(target, source, env):
    """Sets up the PDB dependencies for a pch file, and adds the object
    file target."""

    validate_vars(env)

    pch = None
    obj = None

    for t in target:
        if SCons.Util.splitext(str(t))[1] == '.pch':
            pch = t
        if SCons.Util.splitext(str(t))[1] == '.obj':
            obj = t

    if not obj:
        obj = SCons.Util.splitext(str(pch))[0]+'.obj'

    target = [pch, obj] # pch must be first, and obj second for the PCHCOM to work

    if env.has_key('PDB') and env['PDB']:
        env.SideEffect(env['PDB'], target)
        env.Precious(env['PDB'])

    return (target, source)

def object_emitter(target, source, env):
    """Sets up the PDB and PCH dependencies for an object file."""

    validate_vars(env)

    if env.has_key('PDB') and env['PDB']:
        env.SideEffect(env['PDB'], target)
        env.Precious(env['PDB'])

    if env.has_key('PCH') and env['PCH']:
        env.Depends(target, env['PCH'])

    return (target, source)

pch_builder = SCons.Builder.Builder(action='$PCHCOM', suffix='.pch', emitter=pch_emitter)
res_builder = SCons.Builder.Builder(action='$RCCOM', suffix='.res')

def generate(env):
    """Add Builders and construction variables for MSVC++ to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)

    env['CCPDBFLAGS'] = '${(PDB and "/Zi /Fd%s"%File(PDB)) or ""}'
    env['CCPCHFLAGS'] = '${(PCH and "/Yu%s /Fp%s"%(PCHSTOP or "",File(PCH))) or ""}'
    env['CCCOMFLAGS'] = '$CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET $CCPCHFLAGS $CCPDBFLAGS'
    env['CC']         = 'cl'
    env['CCFLAGS']    = '/nologo'
    env['CCCOM']      = '$CC $CCFLAGS $CCCOMFLAGS' 
    env['SHCC']       = '$CC'
    env['SHCCFLAGS']  = '$CCFLAGS'
    env['SHCCCOM']    = '$SHCC $SHCCFLAGS $CCCOMFLAGS'
    env['CXX']        = '$CC'
    env['CXXFLAGS']   = '$CCFLAGS $( /TP $)'
    env['CXXCOM']     = '$CXX $CXXFLAGS $CCCOMFLAGS'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = '$CXXFLAGS'
    env['SHCXXCOM']   = '$SHCXX $SHCXXFLAGS $CCCOMFLAGS'
    env['CPPDEFPREFIX']  = '/D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '/I'
    env['INCSUFFIX']  = ''
    env['OBJEMITTER'] = object_emitter
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

    env['RC'] = 'rc'
    env['RCFLAGS'] = ''
    env['RCCOM'] = '$RC $_CPPDEFFLAGS $_CPPINCFLAGS $RCFLAGS /fo$TARGET $SOURCES'
    CScan = env.get_scanner('.c')
    if CScan:
        CScan.add_skey('.rc')
    env['BUILDERS']['RES'] = res_builder

    try:
        version = SCons.Tool.msvs.get_default_visualstudio_version(env)

        if env.has_key('MSVS_IGNORE_IDE_PATHS') and env['MSVS_IGNORE_IDE_PATHS']:
            include_path, lib_path, exe_path = get_msvc_default_paths(version)
        else:
            include_path, lib_path, exe_path = get_msvc_paths(version)

        # since other tools can set these, we just make sure that the
        # relevant stuff from MSVS is in there somewhere.
        env.PrependENVPath('INCLUDE', include_path)
        env.PrependENVPath('LIB', lib_path)
        env.PrependENVPath('PATH', exe_path)
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        pass

    env['CFILESUFFIX'] = '.c'
    env['CXXFILESUFFIX'] = '.cc'

    env['PCHCOM'] = '$CXX $CXXFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS /c $SOURCES /Fo${TARGETS[1]} /Yc$PCHSTOP /Fp${TARGETS[0]} $CCPDBFLAGS'
    env['BUILDERS']['PCH'] = pch_builder

def exists(env):
    try:
        v = SCons.Tool.msvs.get_visualstudio_versions()
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        pass
    
    if not v:
        return env.Detect('cl')
    else:
        # there's at least one version of MSVS installed.
        return True
