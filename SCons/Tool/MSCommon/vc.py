# MIT License
#
# Copyright The SCons Foundation
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

"""
MS Compilers: Visual C/C++ detection and configuration.

# TODO:
#   * gather all the information from a single vswhere call instead
#     of calling repeatedly (use json format?)
#   * support passing/setting location for vswhere in env.
#   * supported arch for versions: for old versions of batch file without
#     argument, giving bogus argument cannot be detected, so we have to hardcode
#     this here
#   * print warning when msvc version specified but not found
#   * find out why warning do not print
#   * test on 64 bits XP +  VS 2005 (and VS 6 if possible)
#   * SDK
#   * Assembly
"""

import SCons.compat

import subprocess
import os
import platform
from pathlib import Path
from string import digits as string_digits
from subprocess import PIPE
import re
from collections import (
    namedtuple,
    OrderedDict,
)

import SCons.Util
import SCons.Warnings
from SCons.Tool import find_program_path

from . import common
from .common import CONFIG_CACHE, debug
from .sdk import get_installed_sdks


class VisualCException(Exception):
    pass

class UnsupportedVersion(VisualCException):
    pass

class MSVCUnsupportedHostArch(VisualCException):
    pass

class MSVCUnsupportedTargetArch(VisualCException):
    pass

class MissingConfiguration(VisualCException):
    pass

class NoVersionFound(VisualCException):
    pass

class BatchFileExecutionError(VisualCException):
    pass

class MSVCScriptNotFound(VisualCException):
    pass

class MSVCUseSettingsError(VisualCException):
    pass

class MSVCVersionNotFound(VisualCException):
    pass

# MSVC_NOTFOUND_POLICY:
#     error:  raise exception
#     warn:   issue warning and continue
#     ignore: continue
_MSVC_NOTFOUND_POLICY_DEFAULT = False
_MSVC_NOTFOUND_POLICY = _MSVC_NOTFOUND_POLICY_DEFAULT

_MSVC_NOTFOUND_POLICY_INTERNAL_SYMBOL = {}
_MSVC_NOTFOUND_POLICY_SYMBOLS_PUBLIC = []
_MSVC_NOTFOUND_POLICY_SYMBOLS_DICT = {}

for value, symbol_list in [
    (True,  ['Error',   'Exception']),
    (False, ['Warning', 'Warn']),
    (None,  ['Ignore',  'Suppress']),
]:
    _MSVC_NOTFOUND_POLICY_INTERNAL_SYMBOL[value] = symbol_list[0].lower()
    for symbol in symbol_list:
        _MSVC_NOTFOUND_POLICY_SYMBOLS_PUBLIC.append(symbol.lower())
        _MSVC_NOTFOUND_POLICY_SYMBOLS_DICT[symbol] = value
        _MSVC_NOTFOUND_POLICY_SYMBOLS_DICT[symbol.lower()] = value
        _MSVC_NOTFOUND_POLICY_SYMBOLS_DICT[symbol.upper()] = value

# Dict to 'canonalize' the arch
_ARCH_TO_CANONICAL = {
    "amd64"     : "amd64",
    "emt64"     : "amd64",
    "i386"      : "x86",
    "i486"      : "x86",
    "i586"      : "x86",
    "i686"      : "x86",
    "ia64"      : "ia64",      # deprecated
    "itanium"   : "ia64",      # deprecated
    "x86"       : "x86",
    "x86_64"    : "amd64",
    "arm"       : "arm",
    "arm64"     : "arm64",
    "aarch64"   : "arm64",
}

# The msvc batch files report errors via stdout.  The following
# regular expression attempts to match known msvc error messages
# written to stdout.
re_script_output_error = re.compile(
    r'^(' + r'|'.join([
        r'VSINSTALLDIR variable is not set',             # 2002-2003
        r'The specified configuration type is missing',  # 2005+
        r'Error in script usage',                        # 2005+
        r'ERROR\:',                                      # 2005+
        r'\!ERROR\!',                                    # 2015-2015
        r'\[ERROR\:',                                    # 2017+
        r'\[ERROR\]',                                    # 2017+
        r'Syntax\:',                                     # 2017+
    ]) + r')'
)

# Lists of compatible host/target combinations are derived from a set of defined
# constant data structures for each host architecture. The derived data structures
# implicitly handle the differences in full versions and express versions of visual
# studio. The host/target combination search lists are contructed in order of
# preference. The construction of the derived data structures is independent of actual
# visual studio installations.  The host/target configurations are used in both the
# initial msvc detection and when finding a valid batch file for a given host/target
# combination.
#
# HostTargetConfig description:
#
#     label:
#         Name used for identification.
#
#     host_all_hosts:
#         Defined list of compatible architectures for each host architecture.
#
#     host_all_targets:
#         Defined list of target architectures for each host architecture.
#
#     host_def_targets:
#         Defined list of default target architectures for each host architecture.
#
#     all_pairs:
#         Derived list of all host/target combination tuples.
#
#     host_target_map:
#         Derived list of all compatible host/target combinations for each
#         supported host/target combination.
#
#     host_all_targets_map:
#         Derived list of all compatible host/target combinations for each
#         supported host.  This is used in the initial check that cl.exe exists
#         in the requisite visual studio vc host/target directory for a given host.
#
#     host_def_targets_map:
#         Derived list of default compatible host/target combinations for each
#         supported host.  This is used for a given host when the user does not
#         request a target archicture.
#
#     target_host_map:
#         Derived list of compatible host/target combinations for each supported
#         target/host combination.  This is used for a given host and target when
#         the user requests a target architecture.

_HOST_TARGET_CONFIG_NT = namedtuple("HostTargetConfig", [
    # defined
    "label",                # name for debugging/output
    "host_all_hosts",       # host_all_hosts[host] -> host_list
    "host_all_targets",     # host_all_targets[host] -> target_list
    "host_def_targets",     # host_def_targets[host] -> target_list
    # derived
    "all_pairs",            # host_target_list
    "host_target_map",      # host_target_map[host][target] -> host_target_list
    "host_all_targets_map", # host_all_targets_map[host][target] -> host_target_list
    "host_def_targets_map", # host_def_targets_map[host][target] -> host_target_list
    "target_host_map",      # target_host_map[target][host] -> host_target_list
])

def _host_target_config_factory(*, label, host_all_hosts, host_all_targets, host_def_targets):

    def _make_host_target_map(all_hosts, all_targets):
        # host_target_map[host][target] -> host_target_list
        host_target_map = {}
        for host, host_list in all_hosts.items():
            host_target_map[host] = {}
            for host_platform in host_list:
                for target_platform in all_targets[host_platform]:
                    if target_platform not in host_target_map[host]:
                        host_target_map[host][target_platform] = []
                    host_target_map[host][target_platform].append((host_platform, target_platform))
        return host_target_map

    def _make_host_all_targets_map(all_hosts, host_target_map, all_targets):
        # host_all_target_map[host] -> host_target_list
        # special host key '_all_' contains all (host,target) combinations
        all = '_all_'
        host_all_targets_map = {}
        host_all_targets_map[all] = []
        for host, host_list in all_hosts.items():
            host_all_targets_map[host] = []
            for host_platform in host_list:
                # all_targets[host_platform]: all targets for compatible host
                for target in all_targets[host_platform]:
                    for host_target in host_target_map[host_platform][target]:
                        for host_key in (host, all):
                            if host_target not in host_all_targets_map[host_key]:
                                host_all_targets_map[host_key].append(host_target)
        return host_all_targets_map

    def _make_host_def_targets_map(all_hosts, host_target_map, def_targets):
        # host_def_targets_map[host] -> host_target_list
        host_def_targets_map = {}
        for host, host_list in all_hosts.items():
            host_def_targets_map[host] = []
            for host_platform in host_list:
                # def_targets[host]: default targets for true host
                for target in def_targets[host]:
                    for host_target in host_target_map[host_platform][target]:
                        if host_target not in host_def_targets_map[host]:
                            host_def_targets_map[host].append(host_target)
        return host_def_targets_map

    def _make_target_host_map(all_hosts, host_all_targets_map):
        # target_host_map[target][host] -> host_target_list
        target_host_map = {}
        for host_platform in all_hosts.keys():
            for host_target in host_all_targets_map[host_platform]:
                _, target = host_target
                if target not in target_host_map:
                    target_host_map[target] = {}
                if host_platform not in target_host_map[target]:
                    target_host_map[target][host_platform] = []
                if host_target not in target_host_map[target][host_platform]:
                    target_host_map[target][host_platform].append(host_target)
        return target_host_map

    host_target_map = _make_host_target_map(host_all_hosts, host_all_targets)
    host_all_targets_map = _make_host_all_targets_map(host_all_hosts, host_target_map, host_all_targets)
    host_def_targets_map = _make_host_def_targets_map(host_all_hosts, host_target_map, host_def_targets)
    target_host_map = _make_target_host_map(host_all_hosts, host_all_targets_map)

    all_pairs = host_all_targets_map['_all_']
    del host_all_targets_map['_all_']

    host_target_cfg = _HOST_TARGET_CONFIG_NT(
        label = label,
        host_all_hosts = dict(host_all_hosts),
        host_all_targets = host_all_targets,
        host_def_targets = host_def_targets,
        all_pairs = all_pairs,
        host_target_map = host_target_map,
        host_all_targets_map = host_all_targets_map,
        host_def_targets_map = host_def_targets_map,
        target_host_map = target_host_map,
    )

    return host_target_cfg

# 14.1 (VS2017) and later

# Given a (host, target) tuple, return a tuple containing the batch file to
# look for and a tuple of path components to find cl.exe. We can't rely on returning
# an arg to use for vcvarsall.bat, because that script will run even if given
# a host/target pair that isn't installed.
#
# Starting with 14.1 (VS2017), the batch files are located in directory
# <VSROOT>/VC/Auxiliary/Build.  The batch file name is the first value of the
# stored tuple.
#
# The build tools are organized by host and target subdirectories under each toolset
# version directory.  For example,  <VSROOT>/VC/Tools/MSVC/14.31.31103/bin/Hostx64/x64.
# The cl path fragment under the toolset version folder is the second value of
# the stored tuple.

_GE2017_HOST_TARGET_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('amd64', 'x86')   : ('vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('amd64', 'arm')   : ('vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('amd64', 'arm64') : ('vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

    ('x86',   'amd64') : ('vcvarsx86_amd64.bat',   ('bin', 'Hostx86', 'x64')),
    ('x86',   'x86')   : ('vcvars32.bat',          ('bin', 'Hostx86', 'x86')),
    ('x86',   'arm')   : ('vcvarsx86_arm.bat',     ('bin', 'Hostx86', 'arm')),
    ('x86',   'arm64') : ('vcvarsx86_arm64.bat',   ('bin', 'Hostx86', 'arm64')),

}

_GE2017_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'GE2017',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm64', ['amd64', 'x86']),
        ('arm',   ['x86']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86', 'arm64', 'arm'],
        'x86':   ['x86', 'amd64', 'arm', 'arm64'],
        'arm64': [],
        'arm':   [],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm64': ['arm64', 'arm'],
        'arm':   ['arm'],
    },

)

# debug("_GE2017_HOST_TARGET_CFG: %s", _GE2017_HOST_TARGET_CFG)

# 14.0 (VS2015) to 8.0 (VS2005)

# Given a (host, target) tuple, return a tuple containing the argument for
# the batch file and a tuple of the path components to find cl.exe.
#
# In 14.0 (VS2015) and earlier, the original x86 tools are in the tools
# bin directory (i.e., <VSROOT>/VC/bin).  Any other tools are in subdirectory
# named for the the host/target pair or a single name if the host==target.

_LE2015_HOST_TARGET_BATCHARG_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('amd64',     ('bin', 'amd64')),
    ('amd64', 'x86')   : ('amd64_x86', ('bin', 'amd64_x86')),
    ('amd64', 'arm')   : ('amd64_arm', ('bin', 'amd64_arm')),

    ('x86',   'amd64') : ('x86_amd64', ('bin', 'x86_amd64')),
    ('x86',   'x86')   : ('x86',       ('bin', )),
    ('x86',   'arm')   : ('x86_arm',   ('bin', 'x86_arm')),
    ('x86',   'ia64')  : ('x86_ia64',  ('bin', 'x86_ia64')),

    ('arm',   'arm')   : ('arm',       ('bin', 'arm')),
    ('ia64',  'ia64')  : ('ia64',      ('bin', 'ia64')),

}

_LE2015_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2015',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm',   ['arm']),
        ('ia64',  ['ia64']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86', 'arm'],
        'x86':   ['x86', 'amd64', 'arm', 'ia64'],
        'arm':   ['arm'],
        'ia64':  ['ia64'],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm':   ['arm'],
        'ia64':  ['ia64'],
    },

)

# debug("_LE2015_HOST_TARGET_CFG: %s", _LE2015_HOST_TARGET_CFG)

# 7.1 (VS2003) and earlier

# For 7.1 (VS2003) and earlier, there are only x86 targets and the batch files
# take no arguments.

_LE2003_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2003',

    host_all_hosts = OrderedDict([
        ('amd64', ['x86']),
        ('x86',   ['x86']),
    ]),

    host_all_targets = {
        'amd64': ['x86'],
        'x86':   ['x86'],
    },

    host_def_targets = {
        'amd64': ['x86'],
        'x86':   ['x86'],
    },

)

# debug("_LE2003_HOST_TARGET_CFG: %s", _LE2003_HOST_TARGET_CFG)

_CL_EXE_NAME = 'cl.exe'

def get_msvc_version_numeric(msvc_version):
    """Get the raw version numbers from a MSVC_VERSION string, so it
    could be cast to float or other numeric values. For example, '14.0Exp'
    would get converted to '14.0'.

    Args:
        msvc_version: str
            string representing the version number, could contain non
            digit characters

    Returns:
        str: the value converted to a numeric only string

    """
    return ''.join([x for  x in msvc_version if x in string_digits + '.'])

def get_host_platform(host_platform):

    host_platform = host_platform.lower()

    # Solaris returns i86pc for both 32 and 64 bit architectures
    if host_platform == 'i86pc':
        if platform.architecture()[0] == "64bit":
            host_platform = "amd64"
        else:
            host_platform = "x86"

    try:
        host =_ARCH_TO_CANONICAL[host_platform]
    except KeyError:
        msg = "Unrecognized host architecture %s"
        raise MSVCUnsupportedHostArch(msg % repr(host_platform)) from None

    return host

_native_host_platform = None

def get_native_host_platform():
    global _native_host_platform

    if _native_host_platform is None:

        _native_host_platform = get_host_platform(platform.machine())

    return _native_host_platform

def get_host_target(env, msvc_version, all_host_targets=False):

    vernum = float(get_msvc_version_numeric(msvc_version))

    if vernum > 14:
        # 14.1 (VS2017) and later
        host_target_cfg = _GE2017_HOST_TARGET_CFG
    elif 14 >= vernum >= 8:
        # 14.0 (VS2015) to 8.0 (VS2005)
        host_target_cfg = _LE2015_HOST_TARGET_CFG
    else:
        # 7.1 (VS2003) and earlier
        host_target_cfg = _LE2003_HOST_TARGET_CFG

    host_arch = env.get('HOST_ARCH') if env else None
    debug("HOST_ARCH:%s", str(host_arch))

    if host_arch:
        host_platform = get_host_platform(host_arch)
    else:
        host_platform = get_native_host_platform()

    target_arch = env.get('TARGET_ARCH') if env else None
    debug("TARGET_ARCH:%s", str(target_arch))

    if target_arch:

        try:
            target_platform = _ARCH_TO_CANONICAL[target_arch.lower()]
        except KeyError:
            all_archs = str(list(_ARCH_TO_CANONICAL.keys()))
            raise MSVCUnsupportedTargetArch(
                "Unrecognized target architecture %s\n\tValid architectures: %s"
                % (repr(target_arch), all_archs)
            ) from None

        target_host_map = host_target_cfg.target_host_map

        try:
            host_target_list = target_host_map[target_platform][host_platform]
        except KeyError:
            host_target_list = []
            warn_msg = "unsupported host, target combination ({}, {}) for MSVC version {}".format(
                repr(host_platform), repr(target_platform), msvc_version
            )
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
            debug(warn_msg)

    else:

        target_platform = None

        if all_host_targets:
            host_targets_map = host_target_cfg.host_all_targets_map
        else:
            host_targets_map = host_target_cfg.host_def_targets_map

        try:
            host_target_list = host_targets_map[host_platform]
        except KeyError:
            msg = "Unrecognized host architecture %s for version %s"
            raise MSVCUnsupportedHostArch(msg % (repr(host_platform), msvc_version)) from None

    return (host_platform, target_platform, host_target_list)

# If you update this, update SupportedVSList in Tool/MSCommon/vs.py, and the
# MSVC_VERSION documentation in Tool/msvc.xml.
_VCVER = [
    "14.3",
    "14.2",
    "14.1", "14.1Exp",
    "14.0", "14.0Exp",
    "12.0", "12.0Exp",
    "11.0", "11.0Exp",
    "10.0", "10.0Exp",
    "9.0", "9.0Exp",
    "8.0", "8.0Exp",
    "7.1",
    "7.0",
    "6.0"]

# if using vswhere, configure command line arguments to probe for installed VC editions
_VCVER_TO_VSWHERE_VER = {
    '14.3': [
        ["-version", "[17.0, 18.0)"],  # default: Enterprise, Professional, Community  (order unpredictable?)
        ["-version", "[17.0, 18.0)", "-products", "Microsoft.VisualStudio.Product.BuildTools"],  # BuildTools
    ],
    '14.2': [
        ["-version", "[16.0, 17.0)"],  # default: Enterprise, Professional, Community  (order unpredictable?)
        ["-version", "[16.0, 17.0)", "-products", "Microsoft.VisualStudio.Product.BuildTools"],  # BuildTools
    ],
    '14.1': [
        ["-version", "[15.0, 16.0)"],  # default: Enterprise, Professional, Community (order unpredictable?)
        ["-version", "[15.0, 16.0)", "-products", "Microsoft.VisualStudio.Product.BuildTools"],  # BuildTools
    ],
    '14.1Exp': [
        ["-version", "[15.0, 16.0)", "-products", "Microsoft.VisualStudio.Product.WDExpress"],  # Express
    ],
}

_VCVER_TO_PRODUCT_DIR = {
    '14.3': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')],  # not set by this version
    '14.2': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')],  # not set by this version
    '14.1': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')],  # not set by this version
    '14.1Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')],  # not set by this version
    '14.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\14.0\Setup\VC\ProductDir')],
    '14.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\14.0\Setup\VC\ProductDir')],
    '12.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\12.0\Setup\VC\ProductDir'),
    ],
    '12.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\12.0\Setup\VC\ProductDir'),
    ],
    '11.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\11.0\Setup\VC\ProductDir'),
    ],
    '11.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\11.0\Setup\VC\ProductDir'),
    ],
    '10.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'),
    ],
    '10.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\10.0\Setup\VC\ProductDir'),
    ],
    '9.0': [
        (SCons.Util.HKEY_CURRENT_USER, r'Microsoft\DevDiv\VCForPython\9.0\installdir',),
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir',),
    ],
    '9.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\9.0\Setup\VC\ProductDir'),
    ],
    '8.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir'),
    ],
    '8.0Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\8.0\Setup\VC\ProductDir'),
    ],
    '7.1': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\7.1\Setup\VC\ProductDir'),
    ],
    '7.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\7.0\Setup\VC\ProductDir'),
    ],
    '6.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir'),
    ]
}


def msvc_version_to_maj_min(msvc_version):
    msvc_version_numeric = get_msvc_version_numeric(msvc_version)

    t = msvc_version_numeric.split(".")
    if not len(t) == 2:
        raise ValueError("Unrecognized version %s (%s)" % (msvc_version,msvc_version_numeric))
    try:
        maj = int(t[0])
        min = int(t[1])
        return maj, min
    except ValueError as e:
        raise ValueError("Unrecognized version %s (%s)" % (msvc_version,msvc_version_numeric)) from None


VSWHERE_PATHS = [os.path.join(p,'vswhere.exe') for p in  [
    os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer"),
    os.path.expandvars(r"%ProgramFiles%\Microsoft Visual Studio\Installer"),
    os.path.expandvars(r"%ChocolateyInstall%\bin"),
]]

def msvc_find_vswhere():
    """ Find the location of vswhere """
    # For bug 3333: support default location of vswhere for both
    # 64 and 32 bit windows installs.
    # For bug 3542: also accommodate not being on C: drive.
    # NB: this gets called from testsuite on non-Windows platforms.
    # Whether that makes sense or not, don't break it for those.
    vswhere_path = None
    for pf in VSWHERE_PATHS:
        if os.path.exists(pf):
            vswhere_path = pf
            break

    return vswhere_path

def find_vc_pdir_vswhere(msvc_version, env=None):
    """ Find the MSVC product directory using the vswhere program.

    Args:
        msvc_version: MSVC version to search for
        env: optional to look up VSWHERE variable

    Returns:
        MSVC install dir or None

    Raises:
        UnsupportedVersion: if the version is not known by this file

    """
    try:
        vswhere_version = _VCVER_TO_VSWHERE_VER[msvc_version]
    except KeyError:
        debug("Unknown version of MSVC: %s", msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version) from None

    if env is None or not env.get('VSWHERE'):
        vswhere_path = msvc_find_vswhere()
    else:
        vswhere_path = env.subst('$VSWHERE')

    if vswhere_path is None:
        return None

    debug('VSWHERE: %s', vswhere_path)
    for vswhere_version_args in vswhere_version:

        vswhere_cmd = [vswhere_path] + vswhere_version_args + ["-property", "installationPath"]

        debug("running: %s", vswhere_cmd)

        #cp = subprocess.run(vswhere_cmd, capture_output=True, check=True)  # 3.7+ only
        cp = subprocess.run(vswhere_cmd, stdout=PIPE, stderr=PIPE, check=True)

        if cp.stdout:
            # vswhere could return multiple lines, e.g. if Build Tools
            # and {Community,Professional,Enterprise} are both installed.
            # We could define a way to pick the one we prefer, but since
            # this data is currently only used to make a check for existence,
            # returning the first hit should be good enough.
            lines = cp.stdout.decode("mbcs").splitlines()
            return os.path.join(lines[0], 'VC')
        else:
            # We found vswhere, but no install info available for this version
            pass

    return None


def find_vc_pdir(env, msvc_version):
    """Find the MSVC product directory for the given version.

    Tries to look up the path using a registry key from the table
    _VCVER_TO_PRODUCT_DIR; if there is no key, calls find_vc_pdir_wshere
    for help instead.

    Args:
        msvc_version: str
            msvc version (major.minor, e.g. 10.0)

    Returns:
        str: Path found in registry, or None

    Raises:
        UnsupportedVersion: if the version is not known by this file.
        MissingConfiguration: found version but the directory is missing.

        Both exceptions inherit from VisualCException.

    """
    root = 'Software\\'
    try:
        hkeys = _VCVER_TO_PRODUCT_DIR[msvc_version]
    except KeyError:
        debug("Unknown version of MSVC: %s", msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version) from None

    for hkroot, key in hkeys:
        try:
            comps = None
            if not key:
                comps = find_vc_pdir_vswhere(msvc_version, env)
                if not comps:
                    debug('no VC found for version %s', repr(msvc_version))
                    raise OSError
                debug('VC found: %s', repr(msvc_version))
                return comps
            else:
                if common.is_win64():
                    try:
                        # ordinarily at win64, try Wow6432Node first.
                        comps = common.read_reg(root + 'Wow6432Node\\' + key, hkroot)
                    except OSError:
                        # at Microsoft Visual Studio for Python 2.7, value is not in Wow6432Node
                        pass
                if not comps:
                    # not Win64, or Microsoft Visual Studio for Python 2.7
                    comps = common.read_reg(root + key, hkroot)
        except OSError:
            debug('no VC registry key %s', repr(key))
        else:
            debug('found VC in registry: %s', comps)
            if os.path.exists(comps):
                return comps
            else:
                debug('reg says dir is %s, but it does not exist. (ignoring)', comps)
                raise MissingConfiguration("registry dir {} not found on the filesystem".format(comps))
    return None

def find_batch_file(env, msvc_version, host_arch, target_arch):
    """
    Find the location of the batch script which should set up the compiler
    for any TARGET_ARCH whose compilers were installed by Visual Studio/VCExpress

    In newer (2017+) compilers, make use of the fact there are vcvars
    scripts named with a host_target pair that calls vcvarsall.bat properly,
    so use that and return an empty argument.
    """
    pdir = find_vc_pdir(env, msvc_version)
    if pdir is None:
        raise NoVersionFound("No version of Visual Studio found")
    debug('looking in %s', pdir)

    # filter out e.g. "Exp" from the version name
    msvc_ver_numeric = get_msvc_version_numeric(msvc_version)
    vernum = float(msvc_ver_numeric)

    arg = ''
    if vernum > 14:
        # 14.1 (VS2017) and later
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        batfile, _ = _GE2017_HOST_TARGET_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, batfile)
    elif 14 >= vernum >= 8:
        # 14.0 (VS2015) to 8.0 (VS2005)
        arg, _ = _LE2015_HOST_TARGET_BATCHARG_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(pdir, "vcvarsall.bat")
    else:
        # 7.1 (VS2003) and earlier
        pdir = os.path.join(pdir, "Bin")
        batfilename = os.path.join(pdir, "vcvars32.bat")

    if not os.path.exists(batfilename):
        debug("Not found: %s", batfilename)
        batfilename = None

    installed_sdks = get_installed_sdks()
    for _sdk in installed_sdks:
        sdk_bat_file = _sdk.get_sdk_vc_script(host_arch, target_arch)
        if not sdk_bat_file:
            debug("batch file not found:%s", _sdk)
        else:
            sdk_bat_file_path = os.path.join(pdir, sdk_bat_file)
            if os.path.exists(sdk_bat_file_path):
                debug('sdk_bat_file_path:%s', sdk_bat_file_path)
                return (batfilename, arg, sdk_bat_file_path)

    return (batfilename, arg, None)

__INSTALLED_VCS_RUN = None
_VC_TOOLS_VERSION_FILE_PATH = ['Auxiliary', 'Build', 'Microsoft.VCToolsVersion.default.txt']
_VC_TOOLS_VERSION_FILE = os.sep.join(_VC_TOOLS_VERSION_FILE_PATH)

def _check_cl_exists_in_vc_dir(env, vc_dir, msvc_version):
    """Return status of finding a cl.exe to use.

    Locates cl in the vc_dir depending on TARGET_ARCH, HOST_ARCH and the
    msvc version. TARGET_ARCH and HOST_ARCH can be extracted from the
    passed env, unless the env is None, in which case the native platform is
    assumed for the host and all associated targets.

    Args:
        env: Environment
            a construction environment, usually if this is passed its
            because there is a desired TARGET_ARCH to be used when searching
            for a cl.exe
        vc_dir: str
            the path to the VC dir in the MSVC installation
        msvc_version: str
            msvc version (major.minor, e.g. 10.0)

    Returns:
        bool:

    """

    # Find the host, target, and all candidate (host, target) platform combinations:
    platforms = get_host_target(env, msvc_version, all_host_targets=True)
    debug("host_platform %s, target_platform %s host_target_list %s", *platforms)
    host_platform, target_platform, host_target_list = platforms

    vernum = float(get_msvc_version_numeric(msvc_version))

    # make sure the cl.exe exists meaning the tool is installed
    if vernum > 14:
        # 14.1 (VS2017) and later
        # 2017 and newer allowed multiple versions of the VC toolset to be
        # installed at the same time. This changes the layout.
        # Just get the default tool version for now
        #TODO: support setting a specific minor VC version
        default_toolset_file = os.path.join(vc_dir, _VC_TOOLS_VERSION_FILE)
        try:
            with open(default_toolset_file) as f:
                vc_specific_version = f.readlines()[0].strip()
        except IOError:
            debug('failed to read %s', default_toolset_file)
            return False
        except IndexError:
            debug('failed to find MSVC version in %s', default_toolset_file)
            return False

        for host_platform, target_platform in host_target_list:

            debug('host platform %s, target platform %s for version %s', host_platform, target_platform, msvc_version)

            batchfile_clpathcomps = _GE2017_HOST_TARGET_BATCHFILE_CLPATHCOMPS.get((host_platform, target_platform), None)
            if batchfile_clpathcomps is None:
                debug('unsupported host/target platform combo: (%s,%s)', host_platform, target_platform)
                continue

            _, cl_path_comps = batchfile_clpathcomps
            cl_path = os.path.join(vc_dir, 'Tools', 'MSVC', vc_specific_version, *cl_path_comps, _CL_EXE_NAME)
            debug('checking for %s at %s', _CL_EXE_NAME, cl_path)

            if os.path.exists(cl_path):
                debug('found %s!', _CL_EXE_NAME)
                return True

    elif 14 >= vernum >= 8:
        # 14.0 (VS2015) to 8.0 (VS2005)

        cl_path_prefixes = [None]
        if msvc_version == '9.0':
            # Visual C++ for Python registry key is installdir (root) not productdir (vc)
            cl_path_prefixes.append(('VC',))

        for host_platform, target_platform in host_target_list:

            debug('host platform %s, target platform %s for version %s', host_platform, target_platform, msvc_version)

            batcharg_clpathcomps = _LE2015_HOST_TARGET_BATCHARG_CLPATHCOMPS.get((host_platform, target_platform), None)
            if batcharg_clpathcomps is None:
                debug('unsupported host/target platform combo: (%s,%s)', host_platform, target_platform)
                continue

            _, cl_path_comps = batcharg_clpathcomps
            for cl_path_prefix in cl_path_prefixes:

                cl_path_comps_adj = cl_path_prefix + cl_path_comps if cl_path_prefix else cl_path_comps
                cl_path = os.path.join(vc_dir, *cl_path_comps_adj, _CL_EXE_NAME)
                debug('checking for %s at %s', _CL_EXE_NAME, cl_path)

                if os.path.exists(cl_path):
                    debug('found %s', _CL_EXE_NAME)
                    return True

    elif 8 > vernum >= 6:
        # 7.1 (VS2003) to 6.0 (VS6)

        # quick check for vc_dir/bin and vc_dir/ before walk
        # need to check root as the walk only considers subdirectories
        for cl_dir in ('bin', ''):
            cl_path = os.path.join(vc_dir, cl_dir, _CL_EXE_NAME)
            if os.path.exists(cl_path):
                debug('%s found %s', _CL_EXE_NAME, cl_path)
                return True
        # not in bin or root: must be in a subdirectory
        for cl_root, cl_dirs, _ in os.walk(vc_dir):
            for cl_dir in cl_dirs:
                cl_path = os.path.join(cl_root, cl_dir, _CL_EXE_NAME)
                if os.path.exists(cl_path):
                    debug('%s found %s', _CL_EXE_NAME, cl_path)
                    return True
        return False

    else:
        # version not support return false
        debug('unsupported MSVC version: %s', str(vernum))

    return False

def get_installed_vcs(env=None):
    global __INSTALLED_VCS_RUN

    if __INSTALLED_VCS_RUN is not None:
        return __INSTALLED_VCS_RUN

    installed_versions = []

    for ver in _VCVER:
        debug('trying to find VC %s', ver)
        try:
            VC_DIR = find_vc_pdir(env, ver)
            if VC_DIR:
                debug('found VC %s', ver)
                if _check_cl_exists_in_vc_dir(env, VC_DIR, ver):
                    installed_versions.append(ver)
                else:
                    debug('no compiler found %s', ver)
            else:
                debug('return None for ver %s', ver)
        except (MSVCUnsupportedTargetArch, MSVCUnsupportedHostArch):
            # Allow this exception to propagate further as it should cause
            # SCons to exit with an error code
            raise
        except VisualCException as e:
            debug('did not find VC %s: caught exception %s', ver, str(e))

    __INSTALLED_VCS_RUN = installed_versions
    return __INSTALLED_VCS_RUN

def reset_installed_vcs():
    """Make it try again to find VC.  This is just for the tests."""
    global __INSTALLED_VCS_RUN
    __INSTALLED_VCS_RUN = None
    _MSVCSetupEnvDefault.reset()

# Running these batch files isn't cheap: most of the time spent in
# msvs.generate() is due to vcvars*.bat.  In a build that uses "tools='msvs'"
# in multiple environments, for example:
#    env1 = Environment(tools='msvs')
#    env2 = Environment(tools='msvs')
# we can greatly improve the speed of the second and subsequent Environment
# (or Clone) calls by memoizing the environment variables set by vcvars*.bat.
#
# Updated: by 2018, vcvarsall.bat had gotten so expensive (vs2017 era)
# it was breaking CI builds because the test suite starts scons so many
# times and the existing memo logic only helped with repeated calls
# within the same scons run. Windows builds on the CI system were split
# into chunks to get around single-build time limits.
# With VS2019 it got even slower and an optional persistent cache file
# was introduced. The cache now also stores only the parsed vars,
# not the entire output of running the batch file - saves a bit
# of time not parsing every time.

script_env_cache = None

def script_env(script, args=None):
    global script_env_cache

    if script_env_cache is None:
        script_env_cache = common.read_script_env_cache()
    cache_key = (script, args if args else None)
    cache_data = script_env_cache.get(cache_key, None)

    # Brief sanity check: if we got a value for the key,
    # see if it has a VCToolsInstallDir entry that is not empty.
    # If so, and that path does not exist, invalidate the entry.
    # If empty, this is an old compiler, just leave it alone.
    if cache_data is not None:
        try:
            toolsdir = cache_data["VCToolsInstallDir"]
        except KeyError:
            # we write this value, so should not happen
            pass
        else:
            if toolsdir:
                toolpath = Path(toolsdir[0])
                if not toolpath.exists():
                    cache_data = None

    if cache_data is None:
        stdout = common.get_output(script, args)

        # Stupid batch files do not set return code: we take a look at the
        # beginning of the output for an error message instead
        olines = stdout.splitlines()
        if re_script_output_error.match(olines[0]):
            raise BatchFileExecutionError("\n".join(olines[:2]))

        cache_data = common.parse_output(stdout)
        script_env_cache[cache_key] = cache_data
        # once we updated cache, give a chance to write out if user wanted
        common.write_script_env_cache(script_env_cache)

    return cache_data

def _msvc_notfound_policy_lookup(symbol):

    try:
        notfound_policy = _MSVC_NOTFOUND_POLICY_SYMBOLS_DICT[symbol]
    except KeyError:
        err_msg = "Value specified for MSVC_NOTFOUND_POLICY is not supported: {}.\n" \
                  "  Valid values are: {}".format(
                     repr(symbol),
                     ', '.join([repr(s) for s in _MSVC_NOTFOUND_POLICY_SYMBOLS_PUBLIC])
                  )
        raise ValueError(err_msg)

    return notfound_policy

def set_msvc_notfound_policy(MSVC_NOTFOUND_POLICY=None):
    global _MSVC_NOTFOUND_POLICY

    prev_policy = _MSVC_NOTFOUND_POLICY_INTERNAL_SYMBOL[_MSVC_NOTFOUND_POLICY]

    policy = MSVC_NOTFOUND_POLICY
    if policy is not None:
        _MSVC_NOTFOUND_POLICY = _msvc_notfound_policy_lookup(policy)

    debug('prev_policy=%s, policy=%s, internal_policy=%s', repr(prev_policy), repr(policy), _MSVC_NOTFOUND_POLICY)
    return prev_policy

def get_msvc_notfound_policy():
    policy = _MSVC_NOTFOUND_POLICY_INTERNAL_SYMBOL[_MSVC_NOTFOUND_POLICY]
    debug('policy=%s, internal_policy=%s', repr(policy), _MSVC_NOTFOUND_POLICY)
    return policy

def _msvc_notfound_policy_handler(env, msg):

    if env and 'MSVC_NOTFOUND_POLICY' in env:
        # use environment setting
        notfound_policy = _msvc_notfound_policy_lookup(env['MSVC_NOTFOUND_POLICY'])
    else:
        # use active global setting
        notfound_policy = _MSVC_NOTFOUND_POLICY

    debug('policy=%s, internal_policy=%s', _MSVC_NOTFOUND_POLICY_INTERNAL_SYMBOL[notfound_policy], repr(notfound_policy))

    if notfound_policy is None:
        # ignore
        pass
    elif notfound_policy:
        raise MSVCVersionNotFound(msg)
    else:
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)

class _MSVCSetupEnvDefault:

    # Determine if and/or when an error/warning should be issued when there
    # are no versions of msvc installed.  If there is at least one version of
    # msvc installed, these routines do (almost) nothing.

    # Notes:
    #     * When msvc is the default compiler because there are no compilers
    #       installed, a build may fail due to the cl.exe command not being
    #       recognized.  Currently, there is no easy way to detect during
    #       msvc initialization if the default environment will be used later
    #       to build a program and/or library. There is no error/warning
    #       as there are legitimate SCons uses that do not require a c compiler.
    #     * As implemented, the default is that a warning is issued.  This can
    #       be changed globally via the function set_msvc_notfound_policy and/or
    #       through the environment via the MSVC_NOTFOUND_POLICY variable.

    separator = r';'

    need_init = True

    @classmethod
    def reset(cls):
        debug('msvc default:init')
        cls.n_setup = 0                 # number of calls to msvc_setup_env_once
        cls.default_ismsvc = False      # is msvc the default compiler
        cls.default_tools_re_list = []  # list of default tools regular expressions
        cls.msvc_tools_init = set()     # tools registered via msvc_exists
        cls.msvc_tools = None           # tools registered via msvc_setup_env_once
        cls.msvc_installed = False      # is msvc installed (vcs_installed > 0)
        cls.msvc_nodefault = False      # is there a default version of msvc
        cls.need_init = True            # reset initialization indicator

    @classmethod
    def _initialize(cls, env):
        if cls.need_init:
            cls.reset()
            cls.need_init = False
            vcs = get_installed_vcs(env)
            cls.msvc_installed = len(vcs) > 0
            debug('msvc default:msvc_installed=%s', cls.msvc_installed)

    @classmethod
    def register_tool(cls, env, tool):
        debug('msvc default:tool=%s', tool)
        if cls.need_init:
            cls._initialize(env)
        if cls.msvc_installed:
            return None
        if not tool:
            return None
        if cls.n_setup == 0:
            if tool not in cls.msvc_tools_init:
                cls.msvc_tools_init.add(tool)
                debug('msvc default:tool=%s, msvc_tools_init=%s', tool, cls.msvc_tools_init)
            return None
        if tool not in cls.msvc_tools:
            cls.msvc_tools.add(tool)
            debug('msvc default:tool=%s, msvc_tools=%s', tool, cls.msvc_tools)

    @classmethod
    def register_setup(cls, env):
        debug('msvc default')
        if cls.need_init:
            cls._initialize(env)
        cls.n_setup += 1
        if not cls.msvc_installed:
            cls.msvc_tools = set(cls.msvc_tools_init)
            if cls.n_setup == 1:
                tool_list = env.get('TOOLS', None)
                if tool_list and tool_list[0] == 'default':
                    if len(tool_list) > 1 and tool_list[1] in cls.msvc_tools:
                        # msvc tools are the default compiler
                        cls.default_ismsvc = True
            cls.msvc_nodefault = False
            debug(
                'msvc default:n_setup=%d, msvc_installed=%s, default_ismsvc=%s',
                cls.n_setup, cls.msvc_installed, cls.default_ismsvc
            )

    @classmethod
    def set_nodefault(cls):
        # default msvc version, msvc not installed
        cls.msvc_nodefault = True
        debug('msvc default:msvc_nodefault=%s', cls.msvc_nodefault)

    @classmethod
    def register_iserror(cls, env, tool):

        cls.register_tool(env, tool)

        if cls.msvc_installed:
            # msvc installed
            return None

        if not cls.msvc_nodefault:
            # msvc version specified
            return None

        tool_list = env.get('TOOLS', None)
        if not tool_list:
            # tool list is empty
            return None

        debug(
            'msvc default:n_setup=%s, default_ismsvc=%s, msvc_tools=%s, tool_list=%s',
            cls.n_setup, cls.default_ismsvc, cls.msvc_tools, tool_list
        )

        if not cls.default_ismsvc:

            # Summary:
            #    * msvc is not installed
            #    * msvc version not specified (default)
            #    * msvc is not the default compiler

            # construct tools set
            tools_set = set(tool_list)

        else:

            if cls.n_setup == 1:
                # first setup and msvc is default compiler:
                #     build default tools regex for current tool state
                tools = cls.separator.join(tool_list)
                tools_nchar = len(tools)
                debug('msvc default:add regex:nchar=%d, tools=%s', tools_nchar, tools)
                re_default_tools = re.compile(re.escape(tools))
                cls.default_tools_re_list.insert(0, (tools_nchar, re_default_tools))
                # early exit: no error for default environment when msvc is not installed
                return None

            # Summary:
            #    * msvc is not installed
            #    * msvc version not specified (default)
            #    * environment tools list is not empty
            #    * default tools regex list constructed
            #    * msvc tools set constructed
            #
            # Algorithm using tools string and sets:
            #    * convert environment tools list to a string
            #    * iteratively remove default tools sequences via regex
            #      substition list built from longest sequence (first)
            #      to shortest sequence (last)
            #    * build environment tools set with remaining tools
            #    * compute intersection of environment tools and msvc tools sets
            #    * if the intersection is:
            #          empty - no error: default tools and/or no additional msvc tools
            #          not empty - error: user specified one or more msvc tool(s)
            #
            # This will not produce an error or warning when there are no
            # msvc installed instances nor any other recognized compilers
            # and the default environment is needed for a build.  The msvc
            # compiler is forcibly added to the environment tools list when
            # there are no compilers installed on win32. In this case, cl.exe
            # will not be found on the path resulting in a failed build.

            # construct tools string
            tools = cls.separator.join(tool_list)
            tools_nchar = len(tools)

            debug('msvc default:check tools:nchar=%d, tools=%s', tools_nchar, tools)

            # iteratively remove default tool sequences (longest to shortest)
            re_nchar_min, re_tools_min = cls.default_tools_re_list[-1]
            if tools_nchar >= re_nchar_min and re_tools_min.search(tools):
                # minimum characters satisfied and minimum pattern exists
                for re_nchar, re_default_tool in cls.default_tools_re_list:
                    if tools_nchar < re_nchar:
                        # not enough characters for pattern
                        continue
                    tools = re_default_tool.sub('', tools).strip(cls.separator)
                    tools_nchar = len(tools)
                    debug('msvc default:check tools:nchar=%d, tools=%s', tools_nchar, tools)
                    if tools_nchar < re_nchar_min or not re_tools_min.search(tools):
                        # less than minimum characters or minimum pattern does not exist
                        break

            # construct non-default list(s) tools set
            tools_set = {msvc_tool for msvc_tool in tools.split(cls.separator) if msvc_tool}

        debug('msvc default:tools=%s', tools_set)
        if not tools_set:
            return None

        # compute intersection of remaining tools set and msvc tools set
        tools_found = cls.msvc_tools.intersection(tools_set)
        debug('msvc default:tools_exist=%s', tools_found)
        if not tools_found:
            return None

        # construct in same order as tools list
        tools_found_list = []
        seen_tool = set()
        for tool in tool_list:
            if tool not in seen_tool:
                seen_tool.add(tool)
                if tool in tools_found:
                    tools_found_list.append(tool)

        # return tool list in order presented
        return tools_found_list

def get_default_version(env):
    msvc_version = env.get('MSVC_VERSION')
    msvs_version = env.get('MSVS_VERSION')
    debug('msvc_version:%s msvs_version:%s', msvc_version, msvs_version)

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
        installed_vcs = get_installed_vcs(env)
        debug('installed_vcs:%s', installed_vcs)
        if not installed_vcs:
            #SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
            debug('No installed VCs')
            return None
        msvc_version = installed_vcs[0]
        debug('using default installed MSVC version %s', repr(msvc_version))
    else:
        debug('using specified MSVC version %s', repr(msvc_version))

    return msvc_version

def msvc_setup_env_once(env, tool=None):
    try:
        has_run  = env["MSVC_SETUP_RUN"]
    except KeyError:
        has_run = False

    if not has_run:
        debug('tool=%s', repr(tool))
        _MSVCSetupEnvDefault.register_setup(env)
        msvc_setup_env(env)
        env["MSVC_SETUP_RUN"] = True

    req_tools = _MSVCSetupEnvDefault.register_iserror(env, tool)
    if req_tools:
        msg = "No versions of the MSVC compiler were found.\n" \
              "  Visual Studio C/C++ compilers may not be set correctly.\n" \
              "  Requested tool(s) are: {}".format(req_tools)
        _msvc_notfound_policy_handler(env, msg)

def msvc_find_valid_batch_script(env, version):
    """Find and execute appropriate batch script to set up build env.

    The MSVC build environment depends heavily on having the shell
    environment set.  SCons does not inherit that, and does not count
    on that being set up correctly anyway, so it tries to find the right
    MSVC batch script, or the right arguments to the generic batch script
    vcvarsall.bat, and run that, so we have a valid environment to build in.
    There are dragons here: the batch scripts don't fail (see comments
    elsewhere), they just leave you with a bad setup, so try hard to
    get it right.
    """

    # Find the host, target, and all candidate (host, target) platform combinations:
    platforms = get_host_target(env, version)
    debug("host_platform %s, target_platform %s host_target_list %s", *platforms)
    host_platform, target_platform, host_target_list = platforms

    d = None
    version_installed = False
    for host_arch, target_arch, in host_target_list:
        # Set to current arch.
        env['TARGET_ARCH'] = target_arch

        # Try to locate a batch file for this host/target platform combo
        try:
            (vc_script, arg, sdk_script) = find_batch_file(env, version, host_arch, target_arch)
            debug('vc_script:%s vc_script_arg:%s sdk_script:%s', vc_script, arg, sdk_script)
            version_installed = True
        except VisualCException as e:
            msg = str(e)
            debug('Caught exception while looking for batch file (%s)', msg)
            version_installed = False
            continue

        # Try to use the located batch file for this host/target platform combo
        debug('use_script 2 %s, args:%s', repr(vc_script), arg)
        found = None
        if vc_script:
            # Get just version numbers
            maj, min = msvc_version_to_maj_min(version)
            # VS2015+
            if maj >= 14:
                if env.get('MSVC_UWP_APP') == '1':
                    # Initialize environment variables with store/UWP paths
                    arg = (arg + ' store').lstrip()

            try:
                d = script_env(vc_script, args=arg)
                found = vc_script
            except BatchFileExecutionError as e:
                debug('use_script 3: failed running VC script %s: %s: Error:%s', repr(vc_script), arg, e)
                vc_script=None
                continue
        if not vc_script and sdk_script:
            debug('use_script 4: trying sdk script: %s', sdk_script)
            try:
                d = script_env(sdk_script)
                found = sdk_script
            except BatchFileExecutionError as e:
                debug('use_script 5: failed running SDK script %s: Error:%s', repr(sdk_script), e)
                continue
        elif not vc_script and not sdk_script:
            debug('use_script 6: Neither VC script nor SDK script found')
            continue

        debug("Found a working script/target: %s/%s", repr(found), arg)
        break # We've found a working target_platform, so stop looking

    # If we cannot find a viable installed compiler, reset the TARGET_ARCH
    # To it's initial value
    if not d:
        env['TARGET_ARCH'] = target_platform

        if version_installed:
            msg = "MSVC version '{}' working host/target script was not found.\n" \
                  "  Host = '{}', Target = '{}'\n" \
                  "  Visual Studio C/C++ compilers may not be set correctly".format(
                     version, host_platform, target_platform
                  )
        else:
            installed_vcs = get_installed_vcs(env)
            if installed_vcs:
                msg = "MSVC version '{}' was not found.\n" \
                      "  Visual Studio C/C++ compilers may not be set correctly.\n" \
                      "  Installed versions are: {}".format(version, installed_vcs)
            else:
                msg = "MSVC version '{}' was not found.\n" \
                      "  No versions of the MSVC compiler were found.\n" \
                      "  Visual Studio C/C++ compilers may not be set correctly".format(version)

        _msvc_notfound_policy_handler(env, msg)

    return d

_undefined = None

def get_use_script_use_settings(env):
    global _undefined

    if _undefined is None:
        _undefined = object()

    #   use_script  use_settings   return values   action
    #     value       ignored      (value, None)   use script or bypass detection
    #   undefined  value not None  (False, value)  use dictionary
    #   undefined  undefined/None  (True,  None)   msvc detection

    # None (documentation) or evaluates False (code): bypass detection
    # need to distinguish between undefined and None
    use_script = env.get('MSVC_USE_SCRIPT', _undefined)

    if use_script != _undefined:
        # use_script defined, use_settings ignored (not type checked)
        return (use_script, None)

    # undefined or None: use_settings ignored
    use_settings = env.get('MSVC_USE_SETTINGS', None)

    if use_settings is not None:
        # use script undefined, use_settings defined and not None (type checked)
        return (False, use_settings)

    # use script undefined, use_settings undefined or None
    return (True, None)

def msvc_setup_env(env):
    debug('called')
    version = get_default_version(env)
    if version is None:
        _MSVCSetupEnvDefault.set_nodefault()
        return None

    # XXX: we set-up both MSVS version for backward
    # compatibility with the msvs tool
    env['MSVC_VERSION'] = version
    env['MSVS_VERSION'] = version
    env['MSVS'] = {}


    use_script, use_settings = get_use_script_use_settings(env)
    if SCons.Util.is_String(use_script):
        use_script = use_script.strip()
        if not os.path.exists(use_script):
            raise MSVCScriptNotFound('Script specified by MSVC_USE_SCRIPT not found: "{}"'.format(use_script))
        args = env.subst('$MSVC_USE_SCRIPT_ARGS')
        debug('use_script 1 %s %s', repr(use_script), repr(args))
        d = script_env(use_script, args)
    elif use_script:
        d = msvc_find_valid_batch_script(env,version)
        debug('use_script 2 %s', d)
        if not d:
            return d
    elif use_settings is not None:
        if not SCons.Util.is_Dict(use_settings):
            error_msg = 'MSVC_USE_SETTINGS type error: expected a dictionary, found {}'.format(type(use_settings).__name__)
            raise MSVCUseSettingsError(error_msg)
        d = use_settings
        debug('use_settings %s', d)
    else:
        debug('MSVC_USE_SCRIPT set to False')
        warn_msg = "MSVC_USE_SCRIPT set to False, assuming environment " \
                   "set correctly."
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None

    for k, v in d.items():
        env.PrependENVPath(k, v, delete_existing=True)
        debug("env['ENV']['%s'] = %s", k, env['ENV'][k])

    # final check to issue a warning if the compiler is not present
    if not find_program_path(env, 'cl'):
        debug("did not find %s", _CL_EXE_NAME)
        if CONFIG_CACHE:
            propose = "SCONS_CACHE_MSVC_CONFIG caching enabled, remove cache file {} if out of date.".format(CONFIG_CACHE)
        else:
            propose = "It may need to be installed separately with Visual Studio."
        warn_msg = "Could not find MSVC compiler 'cl'. {}".format(propose)
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)

def msvc_exists(env=None, version=None):
    debug('version=%s', repr(version))
    vcs = get_installed_vcs(env)
    if version is None:
        rval = len(vcs) > 0
    else:
        rval = version in vcs
    debug('version=%s, return=%s', repr(version), rval)
    return rval

def msvc_setup_env_user(env=None):
    rval = False
    if env:
        for key in ('MSVC_VERSION', 'MSVS_VERSION', 'MSVC_USE_SCRIPT'):
            if key in env:
                rval = True
                debug('key=%s, return=%s', repr(key), rval)
                return rval
    debug('return=%s', rval)
    return rval

def msvc_setup_env_tool(env=None, version=None, tool=None):
    debug('tool=%s, version=%s', repr(tool), repr(version))
    _MSVCSetupEnvDefault.register_tool(env, tool)
    rval = False
    if not rval and msvc_exists(env, version):
        rval = True
    if not rval and msvc_setup_env_user(env):
        rval = True
    debug('tool=%s, version=%s, return=%s', repr(tool), repr(version), rval)
    return rval

