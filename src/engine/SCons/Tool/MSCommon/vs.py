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

__doc__ = """Module to detect Visual Studio and/or Visual C/C++
"""

import os

import SCons.Errors
import SCons.Util

from SCons.Tool.MSCommon.common import debug, \
                                       read_reg, \
                                       normalize_env, \
                                       get_output, \
                                       parse_output

class VisualStudio:
    """
    An abstract base class for trying to find installed versions of
    Visual Studio.
    """
    def __init__(self, version, **kw):
        self.version = version
        self.__dict__.update(kw)
        self._cache = {}

    #

    def find_batch_file(self):
        """Try to find the Visual Studio or Visual C/C++ batch file.

        Return None if failed or the batch file does not exist.
        """
        pdir = self.get_vc_product_dir()
        if not pdir:
            debug('find_batch_file():  no pdir')
            return None
        batch_file = os.path.normpath(os.path.join(pdir, self.batch_file))
        batch_file = os.path.normpath(batch_file)
        if not os.path.isfile(batch_file):
            debug('find_batch_file():  %s not on file system' % batch_file)
            return None
        return batch_file

    def find_executable(self):
        pdir = self.get_vc_product_dir()
        if not pdir:
            debug('find_executable():  no pdir')
            return None
        executable = os.path.join(pdir, self.executable_path)
        executable = os.path.normpath(executable)
        if not os.path.isfile(executable):
            debug('find_executable():  %s not on file system' % executable)
            return None
        return executable

    def find_vc_product_dir(self):
        if not SCons.Util.can_read_reg:
            debug('find_vc_product_dir():  can not read registry')
            return None
        key = self.hkey_root + '\\' + self.vc_product_dir_key
        try:
            comps = read_reg(key)
        except WindowsError, e:
            debug('find_vc_product_dir():  no registry key %s' % key)
        else:
            if self.batch_file_dir_reg_relpath:
                comps = os.path.join(comps, self.batch_file_dir_reg_relpath)
                comps = os.path.normpath(comps)
            if os.path.exists(comps):
                return comps
            else:
                debug('find_vc_product_dir():  %s not on file system' % comps)

        d = os.environ.get(self.common_tools_var)
        if not d:
            msg = 'find_vc_product_dir():  no %s variable'
            debug(msg % self.common_tools_var)
            return None
        if not os.path.isdir(d):
            debug('find_vc_product_dir():  %s not on file system' % d)
            return None
        if self.batch_file_dir_env_relpath:
            d = os.path.join(d, self.batch_file_dir_env_relpath)
            d = os.path.normpath(d)
        return d

    #

    def get_batch_file(self):
        try:
            return self._cache['batch_file']
        except KeyError:
            batch_file = self.find_batch_file()
            self._cache['batch_file'] = batch_file
            return batch_file

    def get_executable(self):
        try:
            return self._cache['executable']
        except KeyError:
            executable = self.find_executable()
            self._cache['executable'] = executable
            return executable

    def get_supported_arch(self):
        try:
            return self._cache['supported_arch']
        except KeyError:
            # RDEVE: for the time being use hardcoded lists
            # supported_arch = self.find_supported_arch()
            self._cache['supported_arch'] = self.supported_arch
            return self.supported_arch

    def get_vc_product_dir(self):
        try:
            return self._cache['vc_product_dir']
        except KeyError:
            vc_product_dir = self.find_vc_product_dir()
            self._cache['vc_product_dir'] = vc_product_dir
            return vc_product_dir

    def reset(self):
        self._cache = {}

# The list of supported Visual Studio versions we know how to detect.
#
# How to look for .bat file ?
#  - VS 2008 Express (x86):
#     * from registry key productdir, gives the full path to vsvarsall.bat. In
#     HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VCEpress\9.0\Setup\VC\productdir
#     * from environmnent variable VS90COMNTOOLS: the path is then ..\..\VC
#     relatively to the path given by the variable.
#
#  - VS 2008 Express (WoW6432: 32 bits on windows x64):
#         Software\Wow6432Node\Microsoft\VCEpress\9.0\Setup\VC\productdir
#
#  - VS 2005 Express (x86):
#     * from registry key productdir, gives the full path to vsvarsall.bat. In
#     HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VCEpress\8.0\Setup\VC\productdir
#     * from environmnent variable VS80COMNTOOLS: the path is then ..\..\VC
#     relatively to the path given by the variable.
#
#  - VS 2005 Express (WoW6432: 32 bits on windows x64): does not seem to have a
#  productdir ?
#
#  - VS 2003 .Net (pro edition ? x86):
#     * from registry key productdir. The path is then ..\Common7\Tools\
#     relatively to the key. The key is in HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VisualStudio\7.1\Setup\VC\productdir
#     * from environmnent variable VS71COMNTOOLS: the path is the full path to
#     vsvars32.bat
#
#  - VS 98 (VS 6):
#     * from registry key productdir. The path is then Bin
#     relatively to the key. The key is in HKEY_LOCAL_MACHINE):
#         Software\Microsoft\VisualStudio\6.0\Setup\VC98\productdir
#
# The first version found in the list is the one used by default if
# there are multiple versions installed.  Barring good reasons to
# the contrary, this means we should list versions from most recent
# to oldest.  Pro versions get listed before Express versions on the
# assumption that, by default, you'd rather use the version you paid
# good money for in preference to whatever Microsoft makes available
# for free.
#
# If you update this list, update the documentation in Tool/msvs.xml.

SupportedVSList = [
    # Visual Studio 2010
    # TODO: find the settings, perhaps from someone with a CTP copy?
    #VisualStudio('TBD',
    #             hkey_root=r'TBD',
    #             common_tools_var='TBD',
    #             batch_file='TBD',
    #             vc_product_dir_key=r'TBD',
    #             batch_file_dir_reg_relpath=None,
    #             batch_file_dir_env_relpath=r'TBD',
    #             executable_path=r'TBD',
    #             default_dirname='TBD',
    #),

    # Visual Studio 2008
    # The batch file we look for is in the VC directory,
    # so the devenv.com executable is up in ..\..\Common7\IDE.
    VisualStudio('9.0',
                 hkey_root=r'Software\Microsoft\VisualStudio\9.0',
                 common_tools_var='VS90COMNTOOLS',
                 batch_file='vcvarsall.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=None,
                 batch_file_dir_env_relpath=r'..\..\VC',
                 executable_path=r'..\Common7\IDE\devenv.com',
                 default_dirname='Microsoft Visual Studio 9',
                 supported_arch=['x86', 'amd64'],
    ),

    # Visual C++ 2008 Express Edition
    # The batch file we look for is in the VC directory,
    # so the VCExpress.exe executable is up in ..\..\Common7\IDE.
    VisualStudio('9.0Exp',
                 hkey_root=r'Software\Microsoft\VisualStudio\9.0',
                 common_tools_var='VS90COMNTOOLS',
                 batch_file='vcvarsall.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=None,
                 batch_file_dir_env_relpath=r'..\..\VC',
                 executable_path=r'..\Common7\IDE\VCExpress.exe',
                 default_dirname='Microsoft Visual Studio 9',
                 supported_arch=['x86'],
    ),

    # Visual Studio 2005
    # The batch file we look for is in the VC directory,
    # so the devenv.com executable is up in ..\..\Common7\IDE.
    VisualStudio('8.0',
                 hkey_root=r'Software\Microsoft\VisualStudio\8.0',
                 common_tools_var='VS80COMNTOOLS',
                 batch_file='vcvarsall.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=None,
                 batch_file_dir_env_relpath=r'..\..\VC',
                 executable_path=r'..\Common7\IDE\devenv.com',
                 default_dirname='Microsoft Visual Studio 8',
                 supported_arch=['x86', 'amd64'],
    ),

    # Visual C++ 2005 Express Edition
    # The batch file we look for is in the VC directory,
    # so the VCExpress.exe executable is up in ..\..\Common7\IDE.
    VisualStudio('8.0Exp',
                 hkey_root=r'Software\Microsoft\VCExpress\8.0',
                 common_tools_var='VS80COMNTOOLS',
                 batch_file='vcvarsall.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=None,
                 batch_file_dir_env_relpath=r'..\..\VC',
                 # The batch file is in the VC directory, so
                 # so the devenv.com executable is next door in ..\IDE.
                 executable_path=r'..\Common7\IDE\VCExpress.exe',
                 default_dirname='Microsoft Visual Studio 8',
                 supported_arch=['x86'],
    ),

    # Visual Studio .NET 2003
    # The batch file we look for is in the Common7\Tools directory,
    # so the devenv.com executable is next door in ..\IDE.
    VisualStudio('7.1',
                 hkey_root=r'Software\Microsoft\VisualStudio\7.1',
                 common_tools_var='VS71COMNTOOLS',
                 batch_file='vsvars32.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=r'..\Common7\Tools',
                 batch_file_dir_env_relpath=None,
                 executable_path=r'..\IDE\devenv.com',
                 default_dirname='Microsoft Visual Studio .NET',
                 supported_arch=['x86'],
    ),

    # Visual Studio .NET
    # The batch file we look for is in the Common7\Tools directory,
    # so the devenv.com executable is next door in ..\IDE.
    VisualStudio('7.0',
                 hkey_root=r'Software\Microsoft\VisualStudio\7.0',
                 common_tools_var='VS70COMNTOOLS',
                 batch_file='vsvars32.bat',
                 vc_product_dir_key=r'Setup\VC\ProductDir',
                 batch_file_dir_reg_relpath=r'..\Common7\Tools',
                 batch_file_dir_env_relpath=None,
                 executable_path=r'..\IDE\devenv.com',
                 default_dirname='Microsoft Visual Studio .NET',
                 supported_arch=['x86'],
    ),

    # Visual Studio 6.0
    VisualStudio('6.0',
                 hkey_root=r'Software\Microsoft\VisualStudio\6.0',
                 common_tools_var='VS60COMNTOOLS',
                 batch_file='vcvars32.bat',
                 vc_product_dir_key='Setup\Microsoft Visual C++\ProductDir',
                 batch_file_dir_reg_relpath='Bin',
                 batch_file_dir_env_relpath=None,
                 executable_path=r'Common\MSDev98\Bin\MSDEV.COM',
                 default_dirname='Microsoft Visual Studio',
                 supported_arch=['x86'],
    ),
]

SupportedVSMap = {}
for vs in SupportedVSList:
    SupportedVSMap[vs.version] = vs


# Finding installed versions of Visual Studio isn't cheap, because it
# goes not only to the registry but also to the disk to sanity-check
# that there is, in fact, a Visual Studio directory there and that the
# registry entry isn't just stale.  Find this information once, when
# requested, and cache it.

InstalledVSList = None
InstalledVSMap = None

def get_installed_visual_studios():
    global InstalledVSList
    global InstalledVSMap
    if InstalledVSList is None:
        InstalledVSList = []
        InstalledVSMap = {}
        for vs in SupportedVSList:
            debug('trying to find VS %s' % vs.version)
            if vs.get_executable():
                debug('found VS %s' % vs.version)
                InstalledVSList.append(vs)
                InstalledVSMap[vs.version] = vs
    return InstalledVSList

def reset_installed_visual_studios():
    global InstalledVSList
    global InstalledVSMap
    InstalledVSList = None
    InstalledVSMap = None
    for vs in SupportedVSList:
        vs.reset()


# We may be asked to update multiple construction environments with
# SDK information.  When doing this, we check on-disk for whether
# the SDK has 'mfc' and 'atl' subdirectories.  Since going to disk
# is expensive, cache results by directory.

#SDKEnvironmentUpdates = {}
#
#def set_sdk_by_directory(env, sdk_dir):
#    global SDKEnvironmentUpdates
#    try:
#        env_tuple_list = SDKEnvironmentUpdates[sdk_dir]
#    except KeyError:
#        env_tuple_list = []
#        SDKEnvironmentUpdates[sdk_dir] = env_tuple_list
#
#        include_path = os.path.join(sdk_dir, 'include')
#        mfc_path = os.path.join(include_path, 'mfc')
#        atl_path = os.path.join(include_path, 'atl')
#
#        if os.path.exists(mfc_path):
#            env_tuple_list.append(('INCLUDE', mfc_path))
#        if os.path.exists(atl_path):
#            env_tuple_list.append(('INCLUDE', atl_path))
#        env_tuple_list.append(('INCLUDE', include_path))
#
#        env_tuple_list.append(('LIB', os.path.join(sdk_dir, 'lib')))
#        env_tuple_list.append(('LIBPATH', os.path.join(sdk_dir, 'lib')))
#        env_tuple_list.append(('PATH', os.path.join(sdk_dir, 'bin')))
#
#    for variable, directory in env_tuple_list:
#        env.PrependENVPath(variable, directory)

def detect_msvs():
    return (len(get_installed_visual_studios()) > 0)

def get_vs_by_version(msvs):
    if not SupportedVSMap.has_key(msvs):
        msg = "Visual Studio version %s is not supported" % repr(msvs)
        raise SCons.Errors.UserError, msg
    get_installed_visual_studios()
    vs = InstalledVSMap.get(msvs)
    # Some check like this would let us provide a useful error message
    # if they try to set a Visual Studio version that's not installed.
    # However, we also want to be able to run tests (like the unit
    # tests) on systems that don't, or won't ever, have it installed.
    # It might be worth resurrecting this, with some configurable
    # setting that the tests can use to bypass the check.
    #if not vs:
    #    msg = "Visual Studio version %s is not installed" % repr(msvs)
    #    raise SCons.Errors.UserError, msg
    return vs

def get_default_version(env):
    """Returns the default version string to use for MSVS.

    If no version was requested by the user through the MSVS environment
    variable, query all the available the visual studios through
    query_versions, and take the highest one.

    Return
    ------
    version: str
        the default version.
    """
    if not env.has_key('MSVS') or not SCons.Util.is_Dict(env['MSVS']):
        # TODO(1.5):
        #versions = [vs.version for vs in get_installed_visual_studios()]
        versions = map(lambda vs: vs.version, get_installed_visual_studios())
        env['MSVS'] = {'VERSIONS' : versions}
    else:
        versions = env['MSVS'].get('VERSIONS', [])

    if not env.has_key('MSVS_VERSION'):
        if versions:
            env['MSVS_VERSION'] = versions[0] #use highest version by default
        else:
            env['MSVS_VERSION'] = SupportedVSList[0].version

    env['MSVS']['VERSION'] = env['MSVS_VERSION']

    return env['MSVS_VERSION']

def get_default_arch(env):
    """Return the default arch to use for MSVS

    if no version was requested by the user through the MSVS_ARCH environment
    variable, select x86

    Return
    ------
    arch: str
    """
    arch = env.get('MSVS_ARCH', 'x86')

    msvs = InstalledVSMap.get(env['MSVS_VERSION'])

    if not msvs:
        arch = 'x86'
    elif not arch in msvs.get_supported_arch():
        fmt = "Visual Studio version %s does not support architecture %s"
        raise SCons.Errors.UserError, fmt % (env['MSVS_VERSION'], arch)

    return arch

def merge_default_version(env):
    version = get_default_version(env)
    arch = get_default_arch(env)

    msvs = get_vs_by_version(version)
    if msvs is None:
        return
    batfilename = msvs.get_batch_file()

    # XXX: I think this is broken. This will silently set a bogus tool instead
    # of failing, but there is no other way with the current scons tool
    # framework
    if batfilename is not None:

        vars = ('LIB', 'LIBPATH', 'PATH', 'INCLUDE')

        msvs_list = get_installed_visual_studios()
        # TODO(1.5):
        #vscommonvarnames = [ vs.common_tools_var for vs in msvs_list ]
        vscommonvarnames = map(lambda vs: vs.common_tools_var, msvs_list)
        nenv = normalize_env(env['ENV'], vscommonvarnames + ['COMSPEC'])
        output = get_output(batfilename, arch, env=nenv)
        vars = parse_output(output, vars)

        for k, v in vars.items():
            env.PrependENVPath(k, v, delete_existing=1)

def query_versions():
    """Query the system to get available versions of VS. A version is
    considered when a batfile is found."""
    msvs_list = get_installed_visual_studios()
    # TODO(1.5)
    #versions = [ msvs.version for msvs in msvs_list ]
    versions = map(lambda msvs:  msvs.version, msvs_list)
    return versions

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
