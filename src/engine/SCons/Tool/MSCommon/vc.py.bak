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

__doc__ = """Module for Visual C/C++ detection and configuration.
"""

import os
import platform

import SCons.Warnings

import common

debug = common.debug

class VisualC:
    """
    An base class for finding installed versions of Visual C/C++.
    """
    def __init__(self, version, **kw):
        self.version = version
        self.__dict__.update(kw)
        self._cache = {}

    def vcbin_arch(self):
        if common.is_win64():
            result = {
                'x86_64' : ['amd64', r'BIN\x86_amd64'],
                'ia64'   : [r'BIN\ia64'],
            }.get(target_arch, [])
        else:
            result = {
                'x86_64' : ['x86_amd64'],
                'ia64'   : ['x86_ia64'],
            }.get(target_arch, [])
        # TODO(1.5)
        #return ';'.join(result)
        return string.join(result, ';')

    # Support for searching for an appropriate .bat file.
    # The map is indexed by (target_architecture, host_architecture).
    # Entries where the host_architecture is None specify the
    # cross-platform "default" .bat file if there isn't sn entry
    # specific to the current host architecture.

    batch_file_map = {
        ('x86_64', 'x86_64') : [
            r'bin\amd64\vcvarsamd64.bat',
            r'bin\x86_amd64\vcvarsx86_amd64.bat',
            r'bin\vcvarsx86_amd64.bat',
        ],
        ('x86_64', 'x86') : [
            r'bin\x86_amd64\vcvarsx86_amd64.bat',
        ],
        ('ia64', 'ia64') : [
            r'bin\ia64\vcvarsia64.bat',
            r'bin\x86_ia64\vcvarsx86_ia64.bat',
        ],
        ('ia64', None) : [
            r'bin\x86_ia64\vcvarsx86_ia64.bat',
        ],
        ('x86', None) : [
            r'bin\vcvars32.bat',
        ],
    }

    def find_batch_file(self, target_architecture, host_architecture):
        key = (target_architecture, host_architecture)
        potential_batch_files = self.batch_file_map.get(key)
        if not potential_batch_files:
            key = (target_architecture, None)
            potential_batch_files = self.batch_file_map.get(key)
        if potential_batch_files:
            product_dir = self.get_vc_dir()
            for batch_file in potential_batch_files:
                bf = os.path.join(product_dir, batch_file)
                if os.path.isfile(bf):
                    return bf
        return None

    def find_vc_dir(self):
        root = 'Software\\'
        if common.is_win64():
            root = root + 'Wow6432Node\\'
        for key in self.hkeys:
            key = root + key
            try:
                comps = common.read_reg(key)
            except WindowsError, e:
                debug('find_vc_dir(): no VC registry key %s' % repr(key))
            else:
                debug('find_vc_dir(): found VC in registry: %s' % comps)
                if os.path.exists(comps):
                    return comps
                else:
                    debug('find_vc_dir(): reg says dir is %s, but it does not exist. (ignoring)'\
                              % comps)
                    return None
        return None

    #

    def get_batch_file(self, target_architecture, host_architecture):
        try:
            return self._cache['batch_file']
        except KeyError:
            batch_file = self.find_batch_file(target_architecture, host_architecture)
            self._cache['batch_file'] = batch_file
            return batch_file

    def get_vc_dir(self):
        try:
            return self._cache['vc_dir']
        except KeyError:
            vc_dir = self.find_vc_dir()
            self._cache['vc_dir'] = vc_dir
            return vc_dir
        
    def reset(self):
        self._cache={}
        

# The list of supported Visual C/C++ versions we know how to detect.
#
# The first VC found in the list is the one used by default if there
# are multiple VC installed.  Barring good reasons to the contrary,
# this means we should list VC with from most recent to oldest.
#
# If you update this list, update the documentation in Tool/vc.xml.
SupportedVCList = [
    VisualC('9.0',
            hkeys=[
                r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir',
                r'Microsoft\VCExpress\9.0\Setup\VC\ProductDir',
            ],
            default_install=r'Microsoft Visual Studio 9.0\VC',
            common_tools_var='VS90COMNTOOLS',
            vc_subdir=r'\VC',
            batch_file_base='vcvars',
            supported_arch=['x86', 'x86_64', 'ia64'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86'       : r'ATLMFC\LIB',
                'x86_64'    : r'ATLMFC\LIB\amd64',
                'ia64'      : r'ATLMFC\LIB\ia64',
            },
            crt_lib_subdir = {
                'x86_64'    : r'LIB\amd64',
                'ia64'      : r'LIB\ia64',
            },
    ),
    VisualC('8.0',
            hkeys=[
                r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir',
                r'Microsoft\VCExpress\8.0\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio 8\VC',
            common_tools_var='VS80COMNTOOLS',
            vc_subdir=r'\VC',
            batch_file_base='vcvars',
            supported_arch=['x86', 'x86_64', 'ia64'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86'       : r'ATLMFC\LIB',
                'x86_64'    : r'ATLMFC\LIB\amd64',
                'ia64'      : r'ATLMFC\LIB\ia64',
            },
            crt_lib_subdir = {
                'x86_64'    : r'LIB\amd64',
                'ia64'      : r'LIB\ia64',
            },
    ),
    VisualC('7.1',
            hkeys=[
                r'Microsoft\VisualStudio\7.1\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio 7.1.NET 2003\VC7',
            common_tools_var='VS71COMNTOOLS',
            vc_subdir=r'\VC7',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'ATLMFC\LIB',
            },
    ),
    VisualC('7.0',
            hkeys=[
                r'Microsoft\VisualStudio\7.0\Setup\VC\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio .NET\VC7',
            common_tools_var='VS70COMNTOOLS',
            vc_subdir=r'\VC7',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATLMFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'ATLMFC\LIB',
            },
    ),
    VisualC('6.0',
            hkeys=[
                r'Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir',
            ],
            default_install=r'%s\Microsoft Visual Studio\VC98',
            common_tools_var='VS60COMNTOOLS',
            vc_subdir=r'\VC98',
            batch_file_base='vcvars',
            supported_arch=['x86'],
            atlmc_include_subdir = [r'ATL\INCLUDE', r'MFC\INCLUDE'],
            atlmfc_lib_subdir = {
                'x86' : r'MFC\LIB',
            },
    ),
]

SupportedVCMap = {}
for vc in SupportedVCList:
    SupportedVCMap[vc.version] = vc


# Finding installed versions of Visual C/C++ isn't cheap, because it goes
# not only to the registry but also to the disk to sanity-check that there
# is, in fact, something installed there and that the registry entry isn't
# just stale.  Find this information once, when requested, and cache it.

InstalledVCList = None
InstalledVCMap  = None

def get_installed_vcs():
    global InstalledVCList
    global InstalledVCMap
    if InstalledVCList is None:
        InstalledVCList = []
        InstalledVCMap = {}
        for vc in SupportedVCList:
            debug('trying to find VC %s' % vc.version)
            if vc.get_vc_dir():
                debug('found VC %s' % vc.version)
                InstalledVCList.append(vc)
                InstalledVCMap[vc.version] = vc
    return InstalledVCList


def set_vc_by_version(env, msvc):
    if not SupportedVCMap.has_key(msvc):
        msg = "VC version %s is not supported" % repr(msvc)
        raise SCons.Errors.UserError, msg
    get_installed_vcs()
    vc = InstalledVCMap.get(msvc)
    if not vc:
        msg = "VC version %s is not installed" % repr(msvc)
        raise SCons.Errors.UserError, msg
    set_vc_by_directory(env, vc.get_vc_dir())

# New stuff

def script_env(script, args=None):
    stdout = common.get_output(script, args)
    return common.parse_output(stdout)

def get_default_version(env):
    debug('get_default_version()')

    msvc_version = env.get('MSVC_VERSION')
    if not msvc_version:
        installed_vcs = get_installed_vcs()
        debug('InstalledVCMap:%s'%InstalledVCMap)
        if not installed_vcs:
            msg = 'No installed VCs'
            debug('msv %s\n' % repr(msg))
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
            return None
        msvc = installed_vcs[0]
        msvc_version = msvc.version
        debug('msvc_setup_env: using default installed MSVC version %s\n' % repr(msvc_version))

    return msvc_version

# Dict to 'canonalize' the arch
_ARCH_TO_CANONICAL = {
        "x86": "x86",
        "amd64": "amd64",
        "i386": "x86",
        "emt64": "amd64",
        "x86_64": "amd64"
}

# Given a (host, target) tuple, return the argument for the bat file. Both host
# and targets should be canonalized.
_HOST_TARGET_ARCH_TO_BAT_ARCH = {
        ("x86", "x86"): "x86",
        ("x86", "amd64"): "x86_amd64",
        ("amd64", "amd64"): "amd64",
        ("amd64", "x86"): "x86"
}

def get_host_target(env):
    host_platform = env.get('HOST_ARCH')
    if not host_platform:
      #host_platform = get_default_host_platform()
      host_platform = platform.machine()
    target_platform = env.get('TARGET_ARCH')
    if not target_platform:
      target_platform = host_platform

    return (_ARCH_TO_CANONICAL[host_platform], 
            _ARCH_TO_CANONICAL[target_platform])

def msvc_setup_env_once(env):
    try:
        has_run  = env["MSVC_SETUP_RUN"]
    except KeyError:
        has_run = False

    if not has_run:
        msvc_setup_env(env)
        env["MSVC_SETUP_RUN"] = False

def msvc_setup_env(env):
    debug('msvc_setup_env()')

    version = get_default_version(env)
    host_platform, target_platform = get_host_target(env)
    debug('msvc_setup_env: using specified MSVC version %s\n' % repr(version))
    env['MSVC_VERSION'] = version

    msvc = InstalledVCMap.get(version)
    if not msvc:
        msg = 'VC version %s not installed' % version
        debug('msv %s\n' % repr(msg))
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
        return None

    use_script = env.get('MSVC_USE_SCRIPT', True)
    if SCons.Util.is_String(use_script):
        debug('use_script 1 %s\n' % repr(use_script))
        d = script_env(use_script)
    elif use_script:
        # XXX: this is VS 2008 specific, fix this
        script = os.path.join(msvc.find_vc_dir(), "vcvarsall.bat")

        arg = _HOST_TARGET_ARCH_TO_BAT_ARCH[(host_platform, target_platform)]
        debug('use_script 2 %s, args:%s\n' % (repr(script), arg))
        d = script_env(script, args=arg)
    else:
        debug('msvc.get_default_env()\n')
        d = msvc.get_default_env()

    for k, v in d.items():
        env.PrependENVPath(k, v, delete_existing=True)
      
def msvc_exists(version=None):
    vcs = get_installed_vcs()
    if version is None:
        return len(vcs) > 0
    return InstalledVCMap.has_key(version)
    
    
def reset_installed_vcs():
    global InstalledVCList
    global InstalledVCMap
    InstalledVCList = None
    InstalledVCMap  = None
    for vc in SupportedVCList:
        vc.reset()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
