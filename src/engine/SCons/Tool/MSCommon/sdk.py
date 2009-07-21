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

__doc__ = """Module to detect the Platform/Windows SDK

PSDK 2003 R1 is the earliest version detected.
"""

import os

import SCons.Errors
import SCons.Util

import common

debug = common.debug

# SDK Checks. This is of course a mess as everything else on MS platforms. Here
# is what we do to detect the SDK:
#
# For Windows SDK >= 6.0: just look into the registry entries:
#   HKLM\Software\Microsoft\Microsoft SDKs\Windows
# All the keys in there are the available versions.
#
# For Platform SDK before 6.0 (2003 server R1 and R2, etc...), there does not
# seem to be any sane registry key, so the precise location is hardcoded.
#
# For versions below 2003R1, it seems the PSDK is included with Visual Studio?
#
# Also, per the following:
#     http://benjamin.smedbergs.us/blog/tag/atl/
# VC++ Professional comes with the SDK, VC++ Express does not.

# Location of the SDK (checked for 6.1 only)
_CURINSTALLED_SDK_HKEY_ROOT = \
        r"Software\Microsoft\Microsoft SDKs\Windows\CurrentInstallFolder"


class SDKDefinition:
    """
    An abstract base class for trying to find installed SDK directories.
    """
    def __init__(self, version, **kw):
        self.version = version
        self.__dict__.update(kw)

    def find_sdk_dir(self):
        """Try to find the MS SDK from the registry.

        Return None if failed or the directory does not exist.
        """
        if not SCons.Util.can_read_reg:
            debug('find_sdk_dir(): can not read registry')
            return None

        hkey = self.HKEY_FMT % self.hkey_data

        try:
            sdk_dir = common.read_reg(hkey)
        except WindowsError, e:
            debug('find_sdk_dir(): no SDK registry key %s' % repr(hkey))
            return None

        if not os.path.exists(sdk_dir):
            debug('find_sdk_dir():  %s not on file system' % sdk_dir)
            return None

        ftc = os.path.join(sdk_dir, self.sanity_check_file)
        if not os.path.exists(ftc):
            debug("find_sdk_dir(): sanity check %s not found" % ftc)
            return None

        return sdk_dir

    def get_sdk_dir(self):
        """Return the MSSSDK given the version string."""
        try:
            return self._sdk_dir
        except AttributeError:
            sdk_dir = self.find_sdk_dir()
            self._sdk_dir = sdk_dir
            return sdk_dir

class WindowsSDK(SDKDefinition):
    """
    A subclass for trying to find installed Windows SDK directories.
    """
    HKEY_FMT = r'Software\Microsoft\Microsoft SDKs\Windows\v%s\InstallationFolder'
    def __init__(self, *args, **kw):
        apply(SDKDefinition.__init__, (self,)+args, kw)
        self.hkey_data = self.version

class PlatformSDK(SDKDefinition):
    """
    A subclass for trying to find installed Platform SDK directories.
    """
    HKEY_FMT = r'Software\Microsoft\MicrosoftSDK\InstalledSDKS\%s\Install Dir'
    def __init__(self, *args, **kw):
        apply(SDKDefinition.__init__, (self,)+args, kw)
        self.hkey_data = self.uuid

# The list of support SDKs which we know how to detect.
#
# The first SDK found in the list is the one used by default if there
# are multiple SDKs installed.  Barring good reasons to the contrary,
# this means we should list SDKs with from most recent to oldest.
#
# If you update this list, update the documentation in Tool/mssdk.xml.
SupportedSDKList = [
    WindowsSDK('6.1',
               sanity_check_file=r'bin\SetEnv.Cmd',
               include_subdir='include',
               lib_subdir={
                   'x86'       : ['lib'],
                   'x86_64'    : [r'lib\x64'],
                   'ia64'      : [r'lib\ia64'],
               },
              ),

    WindowsSDK('6.0A',
               sanity_check_file=r'include\windows.h',
               include_subdir='include',
               lib_subdir={
                   'x86'       : ['lib'],
                   'x86_64'    : [r'lib\x64'],
                   'ia64'      : [r'lib\ia64'],
               },
              ),

    WindowsSDK('6.0',
               sanity_check_file=r'bin\gacutil.exe',
               include_subdir='include',
               lib_subdir='lib',
              ),

    PlatformSDK('2003R2',
                sanity_check_file=r'SetEnv.Cmd',
                uuid="D2FF9F89-8AA2-4373-8A31-C838BF4DBBE1"
               ),

    PlatformSDK('2003R1',
                sanity_check_file=r'SetEnv.Cmd',
                uuid="8F9E5EF3-A9A5-491B-A889-C58EFFECE8B3",
               ),
]

SupportedSDKMap = {}
for sdk in SupportedSDKList:
    SupportedSDKMap[sdk.version] = sdk


# Finding installed SDKs isn't cheap, because it goes not only to the
# registry but also to the disk to sanity-check that there is, in fact,
# an SDK installed there and that the registry entry isn't just stale.
# Find this information once, when requested, and cache it.

InstalledSDKList = None
InstalledSDKMap = None

def get_installed_sdks():
    global InstalledSDKList
    global InstalledSDKMap
    if InstalledSDKList is None:
        InstalledSDKList = []
        InstalledSDKMap = {}
        for sdk in SupportedSDKList:
            debug('trying to find SDK %s' % sdk.version)
            if sdk.get_sdk_dir():
                debug('found SDK %s' % sdk.version)
                InstalledSDKList.append(sdk)
                InstalledSDKMap[sdk.version] = sdk
    return InstalledSDKList


# We may be asked to update multiple construction environments with
# SDK information.  When doing this, we check on-disk for whether
# the SDK has 'mfc' and 'atl' subdirectories.  Since going to disk
# is expensive, cache results by directory.

SDKEnvironmentUpdates = {}

def set_sdk_by_directory(env, sdk_dir):
    global SDKEnvironmentUpdates
    try:
        env_tuple_list = SDKEnvironmentUpdates[sdk_dir]
    except KeyError:
        env_tuple_list = []
        SDKEnvironmentUpdates[sdk_dir] = env_tuple_list

        include_path = os.path.join(sdk_dir, 'include')
        mfc_path = os.path.join(include_path, 'mfc')
        atl_path = os.path.join(include_path, 'atl')

        if os.path.exists(mfc_path):
            env_tuple_list.append(('INCLUDE', mfc_path))
        if os.path.exists(atl_path):
            env_tuple_list.append(('INCLUDE', atl_path))
        env_tuple_list.append(('INCLUDE', include_path))

        env_tuple_list.append(('LIB', os.path.join(sdk_dir, 'lib')))
        env_tuple_list.append(('LIBPATH', os.path.join(sdk_dir, 'lib')))
        env_tuple_list.append(('PATH', os.path.join(sdk_dir, 'bin')))

    for variable, directory in env_tuple_list:
        env.PrependENVPath(variable, directory)


# TODO(sgk):  currently unused; remove?
def get_cur_sdk_dir_from_reg():
    """Try to find the platform sdk directory from the registry.

    Return None if failed or the directory does not exist"""
    if not SCons.Util.can_read_reg:
        debug('SCons cannot read registry')
        return None

    try:
        val = common.read_reg(_CURINSTALLED_SDK_HKEY_ROOT)
        debug("Found current sdk dir in registry: %s" % val)
    except WindowsError, e:
        debug("Did not find current sdk in registry")
        return None

    if not os.path.exists(val):
        debug("Current sdk dir %s not on fs" % val)
        return None

    return val

def get_sdk_by_version(mssdk):
    if not SupportedSDKMap.has_key(mssdk):
        msg = "SDK version %s is not supported" % repr(mssdk)
        raise SCons.Errors.UserError, msg
    get_installed_sdks()
    return InstalledSDKMap.get(mssdk)

def get_default_sdk():
    """Set up the default Platform/Windows SDK."""
    get_installed_sdks()
    if not InstalledSDKList:
        return None
    return InstalledSDKList[0]

def mssdk_setup_env(env):
    debug('msvs_setup_env()')
    if env.has_key('MSSDK_DIR'):
        sdk_dir = env['MSSDK_DIR']
        if sdk_dir is None:
            return
        sdk_dir = env.subst(sdk_dir)
    elif env.has_key('MSSDK_VERSION'):
        sdk_version = env['MSSDK_VERSION']
        if sdk_version is None:
            msg = "SDK version %s is not installed" % repr(mssdk)
            raise SCons.Errors.UserError, msg
        sdk_version = env.subst(sdk_version)
        mssdk = get_sdk_by_version(sdk_version)
        sdk_dir = mssdk.get_sdk_dir()
    elif env.has_key('MSVS_VERSION'):
        msvs_version = env['MSVS_VERSION']
        debug('Getting MSVS_VERSION from env:%s'%msvs_version)
        if msvs_version is None:
            return
        msvs_version = env.subst(msvs_version)
        import vs
        msvs = vs.get_vs_by_version(msvs_version)
        debug('msvs is :%s'%msvs)
        sdk_version = msvs.sdk_version
        if not sdk_version:
            return
        mssdk = get_sdk_by_version(sdk_version)
        if not mssdk:
            mssdk = get_default_sdk()
            if not mssdk:
                return
        sdk_dir = mssdk.get_sdk_dir()
    else:
        mssdk = get_default_sdk()
        if not mssdk:
            return
        sdk_dir = mssdk.get_sdk_dir()

    set_sdk_by_directory(env, sdk_dir)

    #print "No MSVS_VERSION: this is likely to be a bug"

def mssdk_exists(version=None):
    sdks = get_installed_sdks()
    if version is None:
        return len(sdks) > 0
    return sdks.has_key(version)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
