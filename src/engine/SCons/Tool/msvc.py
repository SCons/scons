"""engine.SCons.Tool.msvc

Tool-specific initialization for Microsoft Visual C/C++.

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
import SCons.Tool
import SCons.Errors

CSuffixes = ['.c', '.C']
CXXSuffixes = ['.cc', '.cpp', '.cxx', '.c++', '.C++']

def get_devstudio_versions():
    """
    Get list of devstudio versions from the Windows registry.  Return a
    list of strings containing version numbers; an exception will be raised
    if we were unable to access the registry (eg. couldn't import
    a registry-access module) or the appropriate registry keys weren't
    found.
    """

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    K = 'Software\\Microsoft\\Devstudio'
    L = []
    for base in (SCons.Util.HKEY_CLASSES_ROOT,
                 SCons.Util.HKEY_LOCAL_MACHINE,
                 SCons.Util.HKEY_CURRENT_USER,
                 SCons.Util.HKEY_USERS):
        try:
            k = SCons.Util.RegOpenKeyEx(base,K)
            i = 0
            while 1:
                try:
                    p = SCons.Util.RegEnumKey(k,i)
                    if p[0] in '123456789' and p not in L:
                        L.append(p)
                except SCons.Util.RegError:
                    break
                i = i + 1
        except SCons.Util.RegError:
            pass

    if not L:
        raise SCons.Errors.InternalError, "DevStudio was not found."

    L.sort()
    L.reverse()
    return L

def get_msvc_path (path, version, platform='x86'):
    """
    Get a list of devstudio directories (include, lib or path).  Return
    a string delimited by ';'. An exception will be raised if unable to
    access the registry or appropriate registry keys not found.
    """

    if not SCons.Util.can_read_reg:
        raise SCons.Errors.InternalError, "No Windows registry module was found"

    if path=='lib':
        path= 'Library'
    path = string.upper(path + ' Dirs')
    K = ('Software\\Microsoft\\Devstudio\\%s\\' +
         'Build System\\Components\\Platforms\\Win32 (%s)\\Directories') % \
        (version,platform)
    for base in (SCons.Util.HKEY_CLASSES_ROOT,
                 SCons.Util.HKEY_LOCAL_MACHINE,
                 SCons.Util.HKEY_CURRENT_USER,
                 SCons.Util.HKEY_USERS):
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
    raise SCons.Errors.InternalError, "%s was not found in the registry."%path

def get_msdev_dir(version):
    """Returns the root directory of the MSDev installation from the
    registry if it can be found, otherwise we guess."""
    if SCons.Util.can_read_reg:
        K = ('Software\\Microsoft\\Devstudio\\%s\\' +
             'Products\\Microsoft Visual C++') % \
             version
        for base in (SCons.Util.HKEY_LOCAL_MACHINE,
                     SCons.Util.HKEY_CURRENT_USER):
            try:
                k = SCons.Util.RegOpenKeyEx(base,K)
                val, tok = SCons.Util.RegQueryValueEx(k, 'ProductDir')
                return os.path.split(val)[0]
            except SCons.Util.RegError:
                pass

def get_msdev_paths(version=None):
    """Return a 3-tuple of (INCLUDE, LIB, PATH) as the values
    of those three environment variables that should be set
    in order to execute the MSVC tools properly."""
    exe_path = ''
    lib_path = ''
    include_path = ''
    try:
        if not version:
            version = get_devstudio_versions()[0] #use highest version
        include_path = get_msvc_path("include", version)
        lib_path = get_msvc_path("lib", version)
        exe_path = get_msvc_path("path", version) + ";" + os.environ['PATH']
    except (SCons.Util.RegError, SCons.Errors.InternalError):
        # Could not get the configured directories from the registry.
        # However, the configured directories only appear if the user
        # changes them from the default.  Therefore, we'll see if
        # we can get the path to the MSDev base installation from
        # the registry and deduce the default directories.
        MVSdir = None
        if version:
            MVSdir = get_msdev_dir(version)
        if MVSdir:
            MVSVCdir = r'%s\VC98' % MVSdir
            MVSCommondir = r'%s\Common' % MVSdir
            include_path = r'%s\atl\include;%s\mfc\include;%s\include' % (MVSVCdir, MVSVCdir, MVSVCdir)
            lib_path = r'%s\mfc\lib;%s\lib' % (MVSVCdir, MVSVCdir)
            try:
                extra_path = os.pathsep + os.environ['PATH']
            except KeyError:
                extra_path = ''
            exe_path = (r'%s\MSDev98\Bin;%s\Bin' % (MVSCommondir, MVSVCdir)) + extra_path
        else:
            # The DevStudio environment variables don't exist,
            # so just use the variables from the source environment.
            MVSdir = r'C:\Program Files\Microsoft Visual Studio'
            MVSVCdir = r'%s\VC98' % MVSdir
            MVSCommondir = r'%s\Common' % MVSdir
            try:
                include_path = os.environ['INCLUDE']
            except KeyError:
                include_path = ''
            try:
                lib_path = os.environ['LIB']
            except KeyError:
                lib_path = ''
            try:
                exe_path = os.environ['PATH']
            except KeyError:
                exe_path = ''
    return (include_path, lib_path, exe_path)

def generate(env, platform):
    """Add Builders and construction variables for MSVC++ to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)

    env['CC']         = 'cl'
    env['CCFLAGS']    = '/nologo'
    env['CCCOM']      = '$CC $CCFLAGS $CPPFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET'
    env['SHCC']       = '$CC'
    env['SHCCFLAGS']  = '$CCFLAGS'
    env['SHCCCOM']    = '$SHCC $SHCCFLAGS $CPPFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET'
    env['CXX']        = '$CC'
    env['CXXFLAGS']   = '$CCFLAGS'
    env['CXXCOM']     = '$CXX $CXXFLAGS $CPPFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = '$CXXFLAGS'
    env['SHCXXCOM']   = '$SHCXX $SHCXXFLAGS $CPPFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET'
    env['INCPREFIX']  = '/I'
    env['INCSUFFIX']  = '' 

    include_path, lib_path, exe_path = get_msdev_paths()
    env['ENV']['INCLUDE'] = include_path
    env['ENV']['PATH']    = exe_path
    
    env['CFILESUFFIX'] = '.c'
    env['CXXFILESUFFIX'] = '.cc'
    
