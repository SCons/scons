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

# TODO:
#   * supported arch for versions: for old versions of batch file without
#     argument, giving bogus argument cannot be detected, so we have to hardcode
#     this here
#   * print warning when msvc version specified but not found
#   * find out why warning do not print
#   * test on 64 bits XP +  VS 2005 (and VS 6 if possible)
#   * SDK
#   * Assembly
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__doc__ = """Module for Visual C/C++ detection and configuration.
"""

import os
import platform

import SCons.Warnings

import common

debug = common.debug

class VisualCException(Exception):
    pass

class UnsupportedVersion(VisualCException):
    pass

class UnsupportedArch(VisualCException):
    pass

class MissingConfiguration(VisualCException):
    pass

class NoVersionFound(VisualCException):
    pass

class BatchFileExecutionError(VisualCException):
    pass

# Dict to 'canonalize' the arch
_ARCH_TO_CANONICAL = {
    "x86": "x86",
    "amd64": "amd64",
    "i386": "x86",
    "emt64": "amd64",
    "x86_64": "amd64",
    "itanium": "ia64",
    "ia64": "ia64",
}

# Given a (host, target) tuple, return the argument for the bat file. Both host
# and targets should be canonalized.
_HOST_TARGET_ARCH_TO_BAT_ARCH = {
    ("x86", "x86"): "x86",
    ("x86", "amd64"): "x86_amd64",
    ("amd64", "amd64"): "amd64",
    ("amd64", "x86"): "x86",
    ("x86", "ia64"): "x86_ia64"
}

def get_host_target(env):
    host_platform = env.get('HOST_ARCH')
    if not host_platform:
        host_platform = platform.machine()
    target_platform = env.get('TARGET_ARCH')
    if not target_platform:
        target_platform = host_platform

    try:
        host = _ARCH_TO_CANONICAL[host_platform]
    except KeyError, e:
        raise ValueError("Unrecognized host architecture %s" % host_platform)

    try:
        target = _ARCH_TO_CANONICAL[target_platform]
    except KeyError, e:
        raise ValueError("Unrecognized target architecture %s" % target_platform)

    return (host, target)

_VCVER = ["10.0", "9.0", "8.0", "7.1", "7.0", "6.0"]

_VCVER_TO_PRODUCT_DIR = {
        '10.0': [
            r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'],
        '9.0': [
            r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir',
            r'Microsoft\VCExpress\9.0\Setup\VC\ProductDir'],
        '8.0': [
            r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir',
            r'Microsoft\VCExpress\8.0\Setup\VC\ProductDir'],
        '7.1': [
            r'Microsoft\VisualStudio\7.1\Setup\VC\ProductDir'],
        '7.0': [
            r'Microsoft\VisualStudio\7.0\Setup\VC\ProductDir'],
        '6.0': [
            r'Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir']
}

def msvc_version_to_maj_min(msvc_version):
    t = msvc_version.split(".")
    if not len(t) == 2:
        raise ValueError("Unrecognized version %s" % msvc_version)
    try:
        maj = int(t[0])
        min = int(t[1])
        return maj, min
    except ValueError, e:
        raise ValueError("Unrecognized version %s" % msvc_version)

def is_host_target_supported(host_target, msvc_version):
    """Return True if the given (host, target) tuple is supported given the
    msvc version.

    Parameters
    ----------
    host_target: tuple
        tuple of (canonalized) host-target, e.g. ("x86", "amd64") for cross
        compilation from 32 bits windows to 64 bits.
    msvc_version: str
        msvc version (major.minor, e.g. 10.0)

    Note
    ----
    This only check whether a given version *may* support the given (host,
    target), not that the toolchain is actually present on the machine.
    """
    # We assume that any Visual Studio version supports x86 as a target
    if host_target[1] != "x86":
        maj, min = msvc_version_to_maj_min(msvc_version)
        if maj < 8:
            return False

    return True

def find_vc_pdir(msvc_version):
    """Try to find the product directory for the given
    version.

    Note
    ----
    If for some reason the requested version could not be found, an
    exception which inherits from VisualCException will be raised."""
    root = 'Software\\'
    if common.is_win64():
        root = root + 'Wow6432Node\\'
    try:
        hkeys = _VCVER_TO_PRODUCT_DIR[msvc_version]
    except KeyError:
        debug("Unknown version of MSVC: %s" % msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    for key in hkeys:
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
                raise MissingConfiguration("registry dir %s not found on the filesystem" % comps)
    return None

def find_batch_file(msvc_version):
    pdir = find_vc_pdir(msvc_version)
    if pdir is None:
        raise NoVersionFound("No version of Visual Studio found")

    vernum = float(msvc_version)
    if 7 <= vernum < 8:
        pdir = os.path.join(pdir, os.pardir, "Common7", "Tools")
        batfilename = os.path.join(pdir, "vsvars32.bat")
    elif vernum < 7:
        pdir = os.path.join(pdir, "Bin")
        batfilename = os.path.join(pdir, "vcvars32.bat")
    else: # >= 8
        batfilename = os.path.join(pdir, "vcvarsall.bat")

    if os.path.exists(batfilename):
        return batfilename
    else:
        debug("Not found: %s" % batfilename)
        return None

__INSTALLED_VCS_RUN = None

def cached_get_installed_vcs():
    global __INSTALLED_VCS_RUN

    if __INSTALLED_VCS_RUN is None:
        ret = get_installed_vcs()
        __INSTALLED_VCS_RUN = ret

    return __INSTALLED_VCS_RUN

def get_installed_vcs():
    installed_versions = []
    for ver in _VCVER:
        debug('trying to find VC %s' % ver)
        try:
            if find_vc_pdir(ver):
                debug('found VC %s' % ver)
                installed_versions.append(ver)
            else:
                debug('find_vc_pdir return None for ver %s' % ver)
        except VisualCException, e:
            debug('did not find VC %s: caught exception %s' % (ver, str(e)))
    return installed_versions

def script_env(script, args=None):
    stdout = common.get_output(script, args)
    # Stupid batch files do not set return code: we take a look at the
    # beginning of the output for an error message instead
    olines = stdout.splitlines()
    if olines[0].startswith("The specified configuration type is missing"):
        raise BatchFileExecutionError("\n".join(olines[:2]))

    return common.parse_output(stdout)

def get_default_version(env):
    debug('get_default_version()')

    msvc_version = env.get('MSVC_VERSION')
    msvs_version = env.get('MSVS_VERSION')

    if msvs_version and not msvc_version:
        SCons.Warnings.warn(
                SCons.Warnings.DeprecatedWarning,
                "MSVS_VERSION is deprecated: please use MSVC_VERSION instead ")
        return msvs_version
    elif msvc_version and msvs_version:
        if not msvc_version == msvs_version:
            SCons.Warnings.warn(
                    SCons.Warnings.VisualVersionMismatch,
                    "Requested msvc version (%s) and msvs version (%s) do " \
                    "not match: please use MSVC_VERSION only to request a " \
                    "visual studio version, MSVS_VERSION is deprecated" \
                    % (msvc_version, msvs_version))
        return msvs_version
    if not msvc_version:
        installed_vcs = cached_get_installed_vcs()
        debug('installed_vcs:%s' % installed_vcs)
        if not installed_vcs:
            msg = 'No installed VCs'
            debug('msv %s\n' % repr(msg))
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
            return None
        msvc_version = installed_vcs[0]
        debug('msvc_setup_env: using default installed MSVC version %s\n' % repr(msvc_version))

    return msvc_version

def msvc_setup_env_once(env):
    try:
        has_run  = env["MSVC_SETUP_RUN"]
    except KeyError:
        has_run = False

    if not has_run:
        msvc_setup_env(env)
        env["MSVC_SETUP_RUN"] = True

def msvc_setup_env(env):
    debug('msvc_setup_env()')

    version = get_default_version(env)
    if version is None:
        warn_msg = "No version of Visual Studio compiler found - C/C++ " \
                   "compilers most likely not set correctly"
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None
    debug('msvc_setup_env: using specified MSVC version %s\n' % repr(version))

    # XXX: we set-up both MSVS version for backward
    # compatibility with the msvs tool
    env['MSVC_VERSION'] = version
    env['MSVS_VERSION'] = version
    env['MSVS'] = {}

    try:
        script = find_batch_file(version)
    except VisualCException, e:
        msg = str(e)
        debug('Caught exception while looking for batch file (%s)' % msg)
        warn_msg = "VC version %s not installed - C/C++ compilers most " \
                   "likely not set correctly" % version
        warn_msg += " \n Install versions are: %s" % cached_get_installed_vcs()
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None

    use_script = env.get('MSVC_USE_SCRIPT', True)
    if SCons.Util.is_String(use_script):
        debug('use_script 1 %s\n' % repr(use_script))
        d = script_env(use_script)
    elif use_script:
        host_platform, target_platform = get_host_target(env)
        host_target = (host_platform, target_platform)
        if not is_host_target_supported(host_target, version):
            raise UnsupportedVersion(
                    "host, target = %s not supported for MSVC version %s" %
                    (host_target, version))
        arg = _HOST_TARGET_ARCH_TO_BAT_ARCH[host_target]
        debug('use_script 2 %s, args:%s\n' % (repr(script), arg))
        try:
            d = script_env(script, args=arg)
        except BatchFileExecutionError, e:
            msg = "MSVC error while executing %s with args %s (error was %s)" % \
                  (script, arg, str(e))
            raise SCons.Errors.UserError(msg)
    else:
        debug('MSVC_USE_SCRIPT set to False')
        warn_msg = "MSVC_USE_SCRIPT set to False, assuming environment " \
                   "set correctly."
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None

    for k, v in d.items():
        env.PrependENVPath(k, v, delete_existing=True)

def msvc_exists(version=None):
    vcs = cached_get_installed_vcs()
    if version is None:
        return len(vcs) > 0
    return version in vcs
    
