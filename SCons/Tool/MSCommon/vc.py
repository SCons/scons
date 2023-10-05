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
#   * supported arch for versions: for old versions of batch file without
#     argument, giving bogus argument cannot be detected, so we have to hardcode
#     this here
#   * print warning when msvc version specified but not found
#   * find out why warning do not print
#   * test on 64 bits XP +  VS 2005 (and VS 6 if possible)
#   * SDK
#   * Assembly
"""

import subprocess
import os
import platform
import sysconfig
from pathlib import Path
from string import digits as string_digits
import re
from collections import (
    namedtuple,
    OrderedDict,
)
import json
from functools import cmp_to_key

import SCons.Util
import SCons.Warnings
from SCons.Tool import find_program_path

import SCons.Script

from . import common
from .common import (
    CONFIG_CACHE,
    debug,
    debug_extra,
    AutoInitialize,
)

from . import MSVC

from .MSVC.Exceptions import (
    VisualCException,
    MSVCInternalError,
    MSVCUserError,
    MSVCArgumentError,
    MSVCToolsetVersionNotFound,
)

# external exceptions

class MSVCUnsupportedHostArch(VisualCException):
    pass

class MSVCUnsupportedTargetArch(VisualCException):
    pass

class MSVCScriptNotFound(MSVCUserError):
    pass

class MSVCUseSettingsError(MSVCUserError):
    pass

# internal exceptions

class BatchFileExecutionError(VisualCException):
    pass

# undefined object for dict.get() in case key exists and value is None
UNDEFINED = object()

# powershell error sending telemetry for arm32 process on arm64 host (VS2019+):
#    True:  force VSCMD_SKIP_SENDTELEMETRY=1 (if necessary)
#    False: do nothing
_ARM32_ON_ARM64_SKIP_SENDTELEMETRY = True

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

# 14.3 (VS2022) and later

_GE2022_HOST_TARGET_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('amd64', 'x86')   : ('vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('amd64', 'arm')   : ('vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('amd64', 'arm64') : ('vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

    ('x86',   'amd64') : ('vcvarsx86_amd64.bat',   ('bin', 'Hostx86', 'x64')),
    ('x86',   'x86')   : ('vcvars32.bat',          ('bin', 'Hostx86', 'x86')),
    ('x86',   'arm')   : ('vcvarsx86_arm.bat',     ('bin', 'Hostx86', 'arm')),
    ('x86',   'arm64') : ('vcvarsx86_arm64.bat',   ('bin', 'Hostx86', 'arm64')),

    ('arm64', 'amd64') : ('vcvarsarm64_amd64.bat', ('bin', 'Hostarm64', 'arm64_amd64')),
    ('arm64', 'x86')   : ('vcvarsarm64_x86.bat',   ('bin', 'Hostarm64', 'arm64_x86')),
    ('arm64', 'arm')   : ('vcvarsarm64_arm.bat',   ('bin', 'Hostarm64', 'arm64_arm')),
    ('arm64', 'arm64') : ('vcvarsarm64.bat',       ('bin', 'Hostarm64', 'arm64')),

}

_GE2022_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'GE2022',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm64', ['arm64', 'amd64', 'x86']),
        ('arm',   ['x86']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86', 'arm64', 'arm'],
        'x86':   ['x86', 'amd64', 'arm', 'arm64'],
        'arm64': ['arm64', 'amd64', 'arm', 'x86'],
        'arm':   [],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm64': ['arm64', 'amd64', 'arm', 'x86'],
        'arm':   ['arm'],
    },

)

# debug("_GE2022_HOST_TARGET_CFG: %s", _GE2022_HOST_TARGET_CFG)

# 14.2 (VS2019) to 14.1 (VS2017)

_LE2019_HOST_TARGET_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('amd64', 'x86')   : ('vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('amd64', 'arm')   : ('vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('amd64', 'arm64') : ('vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

    ('x86',   'amd64') : ('vcvarsx86_amd64.bat',   ('bin', 'Hostx86', 'x64')),
    ('x86',   'x86')   : ('vcvars32.bat',          ('bin', 'Hostx86', 'x86')),
    ('x86',   'arm')   : ('vcvarsx86_arm.bat',     ('bin', 'Hostx86', 'arm')),
    ('x86',   'arm64') : ('vcvarsx86_arm64.bat',   ('bin', 'Hostx86', 'arm64')),

    ('arm64', 'amd64') : ('vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('arm64', 'x86')   : ('vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('arm64', 'arm')   : ('vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('arm64', 'arm64') : ('vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

}

_LE2019_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2019',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm64', ['amd64', 'x86']),
        ('arm',   ['x86']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86', 'arm64', 'arm'],
        'x86':   ['x86', 'amd64', 'arm', 'arm64'],
        'arm64': ['arm64', 'amd64', 'arm', 'x86'],
        'arm':   [],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm64': ['arm64', 'amd64', 'arm', 'x86'],
        'arm':   ['arm'],
    },

)

# debug("_LE2019_HOST_TARGET_CFG: %s", _LE2019_HOST_TARGET_CFG)

# 14.0 (VS2015) to 10.0 (VS2010)

# Given a (host, target) tuple, return a tuple containing the argument for
# the batch file and a tuple of the path components to find cl.exe.
#
# In 14.0 (VS2015) and earlier, the original x86 tools are in the tools
# bin directory (i.e., <VSROOT>/VC/bin).  Any other tools are in subdirectory
# named for the the host/target pair or a single name if the host==target.

_LE2015_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('amd64',     'vcvars64.bat',         ('bin', 'amd64')),
    ('amd64', 'x86')   : ('amd64_x86', 'vcvarsamd64_x86.bat',  ('bin', 'amd64_x86')),
    ('amd64', 'arm')   : ('amd64_arm', 'vcvarsamd64_arm.bat',  ('bin', 'amd64_arm')),

    ('x86',   'amd64') : ('x86_amd64', 'vcvarsx86_amd64.bat',  ('bin', 'x86_amd64')),
    ('x86',   'x86')   : ('x86',       'vcvars32.bat',         ('bin', )),
    ('x86',   'arm')   : ('x86_arm',   'vcvarsx86_arm.bat',    ('bin', 'x86_arm')),
    ('x86',   'ia64')  : ('x86_ia64',  'vcvarsx86_ia64.bat',   ('bin', 'x86_ia64')),

    ('arm64', 'amd64') : ('amd64',     'vcvars64.bat',         ('bin', 'amd64')),
    ('arm64', 'x86')   : ('amd64_x86', 'vcvarsamd64_x86.bat',  ('bin', 'amd64_x86')),
    ('arm64', 'arm')   : ('amd64_arm', 'vcvarsamd64_arm.bat',  ('bin', 'amd64_arm')),

    ('arm',   'arm')   : ('arm',       'vcvarsarm.bat',        ('bin', 'arm')),
    ('ia64',  'ia64')  : ('ia64',      'vcvars64.bat',         ('bin', 'ia64')),

}

_LE2015_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2015',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm64', ['amd64', 'x86']),
        ('arm',   ['arm']),
        ('ia64',  ['ia64']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86', 'arm'],
        'x86':   ['x86', 'amd64', 'arm', 'ia64'],
        'arm64': ['amd64', 'x86', 'arm'],
        'arm':   ['arm'],
        'ia64':  ['ia64'],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm64': ['amd64', 'arm', 'x86'],
        'arm':   ['arm'],
        'ia64':  ['ia64'],
    },

)

# debug("_LE2015_HOST_TARGET_CFG: %s", _LE2015_HOST_TARGET_CFG)

# 9.0 (VS2008) to 8.0 (VS2005)

_LE2008_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('amd64',     'vcvarsamd64.bat',      ('bin', 'amd64')),
    ('amd64', 'x86') :   ('x86',       'vcvars32.bat',         ('bin', )),

    ('x86',   'amd64') : ('x86_amd64', 'vcvarsx86_amd64.bat',  ('bin', 'x86_amd64')),
    ('x86',   'x86')   : ('x86',       'vcvars32.bat',         ('bin', )),
    ('x86',   'ia64')  : ('x86_ia64',  'vcvarsx86_ia64.bat',   ('bin', 'x86_ia64')),

    ('arm64', 'amd64') : ('amd64',     'vcvarsamd64.bat',      ('bin', 'amd64')),
    ('arm64', 'x86') :   ('x86',       'vcvars32.bat',         ('bin', )),

    ('ia64',  'ia64')  : ('ia64',      'vcvarsia64.bat',       ('bin', 'ia64')),

}

_LE2008_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2008',

    host_all_hosts = OrderedDict([
        ('amd64', ['amd64', 'x86']),
        ('x86',   ['x86']),
        ('arm64', ['amd64', 'x86']),
        ('ia64',  ['ia64']),
    ]),

    host_all_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86', 'amd64', 'ia64'],
        'arm64': ['amd64', 'x86'],
        'ia64':  ['ia64'],
    },

    host_def_targets = {
        'amd64': ['amd64', 'x86'],
        'x86':   ['x86'],
        'arm64': ['amd64', 'x86'],
        'ia64':  ['ia64'],
    },

)

# debug("_LE2008_HOST_TARGET_CFG: %s", _LE2008_HOST_TARGET_CFG)

# 7.1 (VS2003) and earlier

# For 7.1 (VS2003) and earlier, there are only x86 targets and the batch files
# take no arguments.

_LE2003_HOST_TARGET_CFG = _host_target_config_factory(

    label = 'LE2003',

    host_all_hosts = OrderedDict([
        ('amd64', ['x86']),
        ('x86',   ['x86']),
        ('arm64', ['x86']),
    ]),

    host_all_targets = {
        'amd64': ['x86'],
        'x86':   ['x86'],
        'arm64': ['x86'],
    },

    host_def_targets = {
        'amd64': ['x86'],
        'x86':   ['x86'],
        'arm64': ['x86'],
    },

)

# debug("_LE2003_HOST_TARGET_CFG: %s", _LE2003_HOST_TARGET_CFG)

_CL_EXE_NAME = 'cl.exe'

_VSWHERE_EXE = 'vswhere.exe'

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
    return ''.join([x for x in msvc_version if x in string_digits + '.'])

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

_native_host_architecture = None

def get_native_host_architecture():
    """Return the native host architecture."""
    global _native_host_architecture

    if _native_host_architecture is None:

        try:
            arch = common.read_reg(
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment\PROCESSOR_ARCHITECTURE'
            )
        except OSError:
            arch = None

        if not arch:
            arch = platform.machine()

        _native_host_architecture = arch

    return _native_host_architecture

_native_host_platform = None

def get_native_host_platform():
    global _native_host_platform

    if _native_host_platform is None:
        arch = get_native_host_architecture()
        _native_host_platform = get_host_platform(arch)

    return _native_host_platform

def get_host_target(env, msvc_version, all_host_targets: bool=False):

    vernum = float(get_msvc_version_numeric(msvc_version))
    vernum_int = int(vernum * 10)

    if vernum_int >= 143:
        # 14.3 (VS2022) and later
        host_target_cfg = _GE2022_HOST_TARGET_CFG
    elif 143 > vernum_int >= 141:
        # 14.2 (VS2019) to 14.1 (VS2017)
        host_target_cfg = _LE2019_HOST_TARGET_CFG
    elif 141 > vernum_int >= 100:
        # 14.0 (VS2015) to 10.0 (VS2010)
        host_target_cfg = _LE2015_HOST_TARGET_CFG
    elif 100 > vernum_int >= 80:
        # 9.0 (VS2008) to 8.0 (VS2005)
        host_target_cfg = _LE2008_HOST_TARGET_CFG
    else: # 80 > vernum_int
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

    return host_platform, target_platform, host_target_list

_arm32_process_arm64_host = None

def is_arm32_process_arm64_host():
    global _arm32_process_arm64_host

    if _arm32_process_arm64_host is None:

        host = get_native_host_architecture()
        host = _ARCH_TO_CANONICAL.get(host.lower(),'')
        host_isarm64 = host == 'arm64'

        process = sysconfig.get_platform()
        process_isarm32 = process == 'win-arm32'

        _arm32_process_arm64_host = host_isarm64 and process_isarm32

    return _arm32_process_arm64_host

_check_skip_sendtelemetry = None

def _skip_sendtelemetry(env):
    global _check_skip_sendtelemetry

    if _check_skip_sendtelemetry is None:

        if _ARM32_ON_ARM64_SKIP_SENDTELEMETRY and is_arm32_process_arm64_host():
            _check_skip_sendtelemetry = True
        else:
            _check_skip_sendtelemetry = False

    if not _check_skip_sendtelemetry:
        return False

    msvc_version = env.get('MSVC_VERSION') if env else None
    if not msvc_version:
        msvc_version = msvc_default_version(env)

    if not msvc_version:
        return False

    vernum = float(get_msvc_version_numeric(msvc_version))
    if vernum < 14.2:  # VS2019
        return False

    # arm32 process, arm64 host, VS2019+
    return True

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

# VS2017 and later: use a single vswhere json query to find all installations
# VS2015 and earlier: configure registry queries to probe for installed VC editions
_VSPRODUCT_REGISTRY_VCDIR = {
    # vs_product: [(is_vsroot, is_vcforpython, hkroot, key), ...]
    '2015': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\14.0\Setup\VC\ProductDir'),
        (True,  False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\WDExpress\14.0\Setup\VS\ProductDir'),  # vs root
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\14.0\Setup\VC\ProductDir'),  # not populated?
    ],
    '2013': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\12.0\Setup\VC\ProductDir'),
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\12.0\Setup\VC\ProductDir'),
    ],
    '2012': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\11.0\Setup\VC\ProductDir'),
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\11.0\Setup\VC\ProductDir'),
    ],
    '2010': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'),
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\10.0\Setup\VC\ProductDir'),
    ],
    '2008': [
        (True,  True,  SCons.Util.HKEY_CURRENT_USER,  r'Microsoft\DevDiv\VCForPython\9.0\InstallDir',),  # vs root
        (True,  True,  SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\DevDiv\VCForPython\9.0\InstallDir',),  # vs root
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir',),
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\9.0\Setup\VC\ProductDir'),
    ],
    '2005': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\8.0\Setup\VC\ProductDir'),
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\8.0\Setup\VC\ProductDir'),
    ],
    '2003': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\7.1\Setup\VC\ProductDir'),
    ],
    '2002': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\7.0\Setup\VC\ProductDir'),
    ],
    '1998': [
        (False, False, SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\6.0\Setup\Microsoft Visual C++\ProductDir'),
    ]
}

# detect ide binaries

VS2022_VS2002_DEV = (
    MSVC.Kind.IDE_PROGRAM_DEVENV_COM,  # devenv.com
)

VS1998_DEV = (
    MSVC.Kind.IDE_PROGRAM_MSDEV_COM,  # MSDEV.COM
)

VS2017_EXP = (
    MSVC.Kind.IDE_PROGRAM_WDEXPRESS_EXE,  # WDExpress.exe
)

VS2015_VS2012_EXP = (
    MSVC.Kind.IDE_PROGRAM_WDEXPRESS_EXE,     # WDExpress.exe [Desktop]
    MSVC.Kind.IDE_PROGRAM_VSWINEXPRESS_EXE,  # VSWinExpress.exe [Windows]
    MSVC.Kind.IDE_PROGRAM_VWDEXPRESS_EXE,    # VWDExpress.exe [Web]
)

VS2010_VS2005_EXP = (
    MSVC.Kind.IDE_PROGRAM_VCEXPRESS_EXE,
)

# detect productdir kind

_VCDetectConfig = MSVC.Kind.VCDetectConfig

_VSPRODUCT_KIND_DETECT = {

    # 'product': (relpath from vcroot to vsroot, path from vsroot to ide binaries, ide binaries)

    '2022': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV),  # 14.3
    '2019': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV),  # 14.2

    '2017': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2017_EXP),  # 14.1

    '2015': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2015_VS2012_EXP),  # 14.0
    '2013': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2015_VS2012_EXP),  # 12.0
    '2012': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2015_VS2012_EXP),  # 11.0

    '2010': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2010_VS2005_EXP),  # 10.0
    '2008': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2010_VS2005_EXP),  # 9.0
    '2005': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV + VS2010_VS2005_EXP),  # 8.0

    '2003': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV),  # 7.1
    '2002': _VCDetectConfig(root=os.pardir, path=r'Common7\IDE', programs=VS2022_VS2002_DEV),  # 7.0

    '1998': _VCDetectConfig(root=os.pardir, path=r'Common\MSDev98\Bin', programs=VS1998_DEV),  # 6.0
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
    except ValueError:
        raise ValueError("Unrecognized version %s (%s)" % (msvc_version,msvc_version_numeric)) from None

# normalized paths

_normalize_path = {}

def normalize_path(pval):
    global _normalize_path
    rval = _normalize_path.get(pval, UNDEFINED)
    if rval == UNDEFINED:
        rval = MSVC.Util.normalize_path(pval)
        _normalize_path[pval] = rval
        # debug('pval=%s, orig=%s', repr(rval), repr(pval))
    return rval

# path existence

_path_exists = {}

def path_exists(pval):
    global _path_exists
    rval = _path_exists.get(pval, UNDEFINED)
    if rval == UNDEFINED:
        rval = os.path.exists(pval)
        _path_exists[pval] = rval
        # debug('exists=%s, pval=%s', rval, repr(pval))
    return rval

# initialize vswhere paths

VSWhereExecutable = namedtuple('VSWhereExecutable', [
    'path',
    'norm',
])

# For bug 3333: support default location of vswhere for both
# 64 and 32 bit windows installs.
# For bug 3542: also accommodate not being on C: drive.

VSWHERE_PATHS = [
    os.path.join(p,'vswhere.exe')
    for p in [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft Visual Studio\Installer"),
        os.path.expandvars(r"%ChocolateyInstall%\bin"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
        os.path.expanduser(r"~\scoop\shims"),
        os.path.expandvars(r"%SCOOP%\shims"),
    ]
    if not p.startswith('%')
]

VSWHERE_EXECS_EXIST = [
    VSWhereExecutable(path=p, norm=normalize_path(p))
    for p in VSWHERE_PATHS
    if path_exists(p)
]

debug('VSWHERE_EXECS_EXIST=%s', VSWHERE_EXECS_EXIST)

# user-specified vswhere executables

_cache_user_vswhere_paths = {}

def _vswhere_user_path(pval, source):
    global _cache_user_vswhere_paths

    rval = _cache_user_vswhere_paths.get(pval, UNDEFINED)
    if rval != UNDEFINED:
        debug('vswhere_exec=%s', repr(rval))
        return rval

    vswhere_exec = None
    if pval:

        if not path_exists(pval):

            warn_msg = f'vswhere executable path not found: {source}={pval!r}'
            SCons.Warnings.warn(MSVC.Warnings.VSWherePathWarning, warn_msg)
            debug(warn_msg)

        else:

            norm = normalize_path(pval)
            tail = os.path.split(norm)[-1]
            if tail != _VSWHERE_EXE:

                warn_msg = f'unsupported vswhere executable (expected {_VSWHERE_EXE!r}, found {tail!r}): {source}={pval!r}'
                SCons.Warnings.warn(MSVC.Warnings.VSWherePathWarning, warn_msg)
                debug(warn_msg)

            else:

                vswhere_exec = VSWhereExecutable(path=pval, norm=norm)
                debug('vswhere_exec=%s', repr(vswhere_exec))

    _cache_user_vswhere_paths[pval] = vswhere_exec

    return vswhere_exec

# register user vswhere executable location(s)

def vswhere_push_location(string_or_list, front=False) -> None:
    global VSWHERE_EXECS_EXIST

    path_list = SCons.Util.flatten(string_or_list)
    if path_list:

        user_execs = []
        for pval in path_list:
            vswhere_exec = _vswhere_user_path(pval, 'vswhere_push_location')
            if vswhere_exec:
                user_execs.append(vswhere_exec)

        if user_execs:

            if front:
                all_execs = user_execs + VSWHERE_EXECS_EXIST
            else:
                all_execs = VSWHERE_EXECS_EXIST + user_execs

            seen = set()
            unique_execs = []
            for vswhere_exec in all_execs:
                if vswhere_exec.norm in seen:
                    continue
                seen.add(vswhere_exec.norm)
                unique_execs.append(vswhere_exec)

            VSWHERE_EXECS_EXIST = unique_execs
            debug('VSWHERE_EXECS_EXIST=%s', VSWHERE_EXECS_EXIST)

# all vswhere executables

# TODO(JCB): command-line argument: --vswhere=EXEPATH

def _find_vswhere_executables(vswhere_env=None):

    vswhere_execs = []

    # env['VSWHERE'] path
    if vswhere_env:
        vswhere_exec = _vswhere_user_path(vswhere_env, "env['VSWHERE']")
        if vswhere_exec:
            vswhere_execs.append(vswhere_exec)

    # default paths and user paths (vswhere_push_location)
    if VSWHERE_EXECS_EXIST:
        vswhere_execs.extend(VSWHERE_EXECS_EXIST)

    return vswhere_execs

def find_vswhere_executables(env=None):
    vswhere_env = env.subst('$VSWHERE') if env and 'VSWHERE' in env else None
    vswhere_execs = _find_vswhere_executables(vswhere_env)
    return vswhere_execs

def msvc_find_vswhere(env=None):
    """ Find the location of vswhere """
    # NB: this gets called from testsuite on non-Windows platforms.
    # Whether that makes sense or not, don't break it for those.
    vswhere_execs = find_vswhere_executables(env)
    if vswhere_execs:
        vswhere_path = vswhere_execs[0].path
    else:
        vswhere_path = None
    debug('vswhere_path=%s', vswhere_path)
    return vswhere_path

# TODO(JCB): command-line argument: --msvs-channel=Release|Preview|Any
_default_msvs_channel_def = MSVC.Config.MSVS_CHANNEL_RELEASE
debug('default msvs_channel=%s', _default_msvs_channel_def.vs_channel_id)

_default_msvs_channel_retrieved = False

def _msvs_channel_default():
    global _default_msvs_channel_def
    global _default_msvs_channel_retrieved
    _default_msvs_channel_retrieved = True
    return _default_msvs_channel_def

def msvs_set_channel_default(msvs_channel):
    """Set the default msvs channel.

    Args:
        msvs_channel: str
            string representing the msvs channel

            Case-insensitive values are:
                Release, Rel, Preview, Pre, Any, *

    Returns:
        bool: True if the default msvs channel was accepted.
              False if the default msvs channel was not accepted.

    """
    global _default_msvs_channel_retrieved
    global _default_msvs_channel_def
    rval = False
    if _default_msvs_channel_retrieved:
        # TODO(JCB): warn msvs_channel ignored (must be set earlier)
        pass
    else:
        vs_channel_def = MSVC.Validate.validate_msvs_channel(
            msvs_channel, 'msvs_channel_set_default'
        )
        if vs_channel_def:
            _default_msvs_channel_def = vs_channel_def
            debug('default msvs_channel=%s', _default_msvs_channel_def.vs_channel_id)
            rval = True
    return rval

def msvs_get_channel_default():
    """Get the default msvs channel.

    Returns:
        str: default msvs channel

    """
    global _default_msvs_channel_def
    return _default_msvs_channel_def.vs_channel_id

class _VSKeys:

    # edition key: (product, channel, component/None, seqnbr/None)

    _MSVSEditionKey = namedtuple('_MSVSEditionKey', [
        'vs_product_def',
        'vs_channel_def',
        'vs_componentid_def',
        'vs_sequence_nbr',
    ])

    class MSVSEditionKey(_MSVSEditionKey):

        def serialize(self):
            values = [
                self.vs_product_def.vs_product,
                self.vs_channel_def.vs_channel_suffix,
            ]
            if self.vs_componentid_def:
                values.append(self.vs_componentid_def.vs_component_suffix)
            if self.vs_sequence_nbr:
                values.append(str(self.vs_sequence_nbr))
            rval = '-'.join(values)
            return rval

        @classmethod
        def factory(
            cls, *,
            vs_product_def,
            vs_channel_def,
            vs_componentid_def,
            vs_sequence_nbr,
        ):

            vs_edition_key = cls(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            return vs_edition_key

    @classmethod
    def msvs_edition_key(
        cls, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        if not vs_product_def:
            errmsg = 'vs_product_def is undefined'
            debug('MSVCInternalError: %s', errmsg)
            raise MSVCInternalError(errmsg)

        if not vs_channel_def:
            errmsg = 'vs_channel_def is undefined'
            debug('MSVCInternalError: %s', errmsg)
            raise MSVCInternalError(errmsg)

        vs_edition_key = cls.MSVSEditionKey.factory(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
            vs_sequence_nbr=vs_sequence_nbr
        )

        return vs_edition_key

    # channel key: (channel, component/None)

    _MSVSChannelKey = namedtuple('_MSVSChannelKey', [
        'vs_channel_def',
        'vs_componentid_def',
    ])

    class MSVSChannelKey(_MSVSChannelKey):

        def serialize(self):
            values = [
                self.vs_channel_def.vs_channel_suffix,
            ]
            if self.vs_componentid_def:
                values.append(self.vs_componentid_def.vs_component_suffix)
            rval = '-'.join(values)
            return rval

        @classmethod
        def factory(
            cls, *,
            vs_channel_def,
            vs_componentid_def,
        ):

            vs_channel_key = cls(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            return vs_channel_key

    @classmethod
    def msvs_channel_key(
        cls, *,
        vs_channel_def=None,
        vs_componentid_def=None,
    ):

        if not vs_channel_def:
            errmsg = 'vs_channel_def is undefined'
            debug('MSVCInternalError: %s', errmsg)
            raise MSVCInternalError(errmsg)

        vs_channel_key = cls.MSVSChannelKey.factory(
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        return vs_channel_key

_MSVSBase = namedtuple('_MSVSBase', [
    'id_str',
    'id_comps',
    'vs_product_def',
    'vs_channel_def',
    'vs_component_def',
    'vs_sequence_nbr',
    'vs_dir',
    'vs_dir_norm',
    'vs_version',
    'is_express',
    'is_buildtools',
    'is_vcforpython',
    'vs_edition_channel_component_seqnbr_key',
    'vs_edition_channel_component_key',
    'vs_edition_channel_key',
    'vs_channel_component_key',
    'vs_channel_key',
    'instance_map',
])

class MSVSBase(_MSVSBase):

    def _is_express(vs_component_def):
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_express = bool(vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_EXPRESS)
        return is_express

    @staticmethod
    def _is_buildtools(vs_component_def):
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_buildtools = bool(vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_BUILDTOOLS)
        return is_buildtools

    @staticmethod
    def _is_vcforpython(vs_component_def):
        vs_componentid_def = vs_component_def.vs_componentid_def
        is_vcforpython = bool(vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_PYTHON)
        return is_vcforpython

    @classmethod
    def factory(
        cls, *,
        vs_product_def,
        vs_channel_def,
        vs_component_def,
        vs_sequence_nbr,
        vs_dir,
        vs_version,
    ):

        vs_componentid_def = vs_component_def.vs_componentid_def

        vs_edition_channel_component_seqnbr_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
            vs_sequence_nbr=vs_sequence_nbr,
        )

        vs_edition_channel_component_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        vs_edition_channel_key = _VSKeys.msvs_edition_key(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
        )

        vs_channel_component_key = _VSKeys.msvs_channel_key(
            vs_channel_def=vs_channel_def,
            vs_componentid_def=vs_componentid_def,
        )

        vs_channel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=vs_channel_def,
        )

        instance_map = {
            'msvs_instance': None,
            'msvc_instance': None,
        }

        id_comps = (
            vs_product_def.vs_product,
            vs_channel_def.vs_channel_suffix,
            vs_component_def.vs_componentid_def.vs_component_suffix,
            str(vs_sequence_nbr),
        )

        id_str = '{}({})'.format(cls.__name__, ', '.join(id_comps))

        msvs_base = cls(
            id_str=id_str,
            id_comps=id_comps,
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_component_def=vs_component_def,
            vs_sequence_nbr=vs_sequence_nbr,
            vs_dir=vs_dir,
            vs_dir_norm=normalize_path(vs_dir),
            vs_version=vs_version,
            is_express=cls._is_express(vs_component_def),
            is_buildtools=cls._is_buildtools(vs_component_def),
            is_vcforpython=cls._is_vcforpython(vs_component_def),
            vs_edition_channel_component_seqnbr_key=vs_edition_channel_component_seqnbr_key,
            vs_edition_channel_component_key=vs_edition_channel_component_key,
            vs_edition_channel_key=vs_edition_channel_key,
            vs_channel_component_key=vs_channel_component_key,
            vs_channel_key=vs_channel_key,
            instance_map=instance_map,
        )

        return msvs_base

    @staticmethod
    def default_order(a, b):
        # vs product numeric: descending order
        if a.vs_product_def.vs_product_numeric != b.vs_product_def.vs_product_numeric:
            return 1 if a.vs_product_def.vs_product_numeric < b.vs_product_def.vs_product_numeric else -1
        # vs channel: ascending order (release, preview)
        if a.vs_channel_def.vs_channel_rank != b.vs_channel_def.vs_channel_rank:
            return 1 if a.vs_channel_def.vs_channel_rank > b.vs_channel_def.vs_channel_rank else -1
        # component rank: descending order
        if a.vs_component_def.vs_component_rank != b.vs_component_def.vs_component_rank:
            return 1 if a.vs_component_def.vs_component_rank < b.vs_component_def.vs_component_rank else -1
        # sequence number: ascending order
        if a.vs_sequence_nbr != b.vs_sequence_nbr:
            return 1 if a.vs_sequence_nbr > b.vs_sequence_nbr else -1
        return 0

    def register_msvs_instance(self, msvs_instance):
        self.instance_map['msvs_instance'] = msvs_instance

    def register_msvc_instance(self, msvc_instance):
        self.instance_map['msvc_instance'] = msvc_instance

    @property
    def msvs_instance(self):
        return self.instance_map.get('msvs_instance')

    @property
    def msvc_instance(self):
        return self.instance_map.get('msvc_instance')

    @property
    def vs_component_suffix(self):
        return self.vs_component_def.vs_componentid_def.vs_component_suffix

_MSVSInstance = namedtuple('_MSVSInstance', [
    'id_str',
    'msvs_base',
    'vs_executable',
    'vs_executable_norm',
    'vc_version_def',
])

class MSVSInstance(_MSVSInstance):

    @classmethod
    def factory(
        cls, *,
        msvs_base,
        vs_executable,
        vc_version_def,
    ):

        id_str = '{}({})'.format(cls.__name__, ', '.join(msvs_base.id_comps))

        msvs_instance = cls(
            id_str=id_str,
            msvs_base=msvs_base,
            vs_executable=vs_executable,
            vs_executable_norm=normalize_path(vs_executable),
            vc_version_def=vc_version_def,
        )

        return msvs_instance

    @staticmethod
    def default_order(a, b):
        return MSVSBase.default_order(a.msvs_base, b.msvs_base)

    @property
    def id_comps(self):
        return self.msvs_base.id_comps

    @property
    def msvc_instance(self):
        return self.msvs_base.msvc_instance

    @property
    def vs_dir(self):
        return self.msvs_base.vs_dir

    @property
    def vs_version(self):
        return self.msvs_base.vs_version

    @property
    def vs_edition_channel_component_seqnbr_key(self):
        return self.msvs_base.vs_edition_channel_component_seqnbr_key

    @property
    def vs_edition_channel_component_key(self):
        return self.msvs_base.vs_edition_channel_component_key

    @property
    def vs_edition_channel_key(self):
        return self.msvs_base.vs_edition_channel_key

    @property
    def vs_channel_component_key(self):
        return self.msvs_base.vs_channel_component_key

    @property
    def vs_channel_key(self):
        return self.msvs_base.vs_channel_key

    @property
    def msvc_version(self):
        return self.vc_version_def.msvc_version

    @property
    def msvc_verstr(self):
        return self.vc_version_def.msvc_verstr

    @property
    def vs_product_def(self):
        return self.msvs_base.vs_product_def

    @property
    def vs_channel_def(self):
        return self.msvs_base.vs_channel_def

    @property
    def vs_componentid_def(self):
        return self.msvs_base.vs_component_def.vs_componentid_def

    @property
    def vs_product(self):
        return self.msvs_base.vs_product_def.vs_product

    @property
    def vs_channel_id(self):
        return self.msvs_base.vs_channel_def.vs_channel_id

    @property
    def vs_component_id(self):
        return self.msvs_base.vs_component_def.vs_componentid_def.vs_component_id

    @property
    def vs_sequence_nbr(self):
        return self.msvs_base.vs_sequence_nbr

_MSVSInstalled = namedtuple('_MSVSInstalled', [
    'msvs_instances',
    'msvs_edition_instances_map',
    'msvs_channel_instances_map',
    'msvs_channel_map', # TODO(JCB): remove?
])

class MSVSInstalled(_MSVSInstalled, AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls):
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvs_instances,
    ):

        msvs_instances = sorted(
            msvs_instances, key=cmp_to_key(MSVSInstance.default_order)
        )

        msvs_channel_map = {
            vs_channel_def: {}
            for vs_channel_def in MSVC.Config.MSVS_CHANNEL_DEFINITION_LIST
        }

        vs_edition_instances = {}
        vs_channel_instances = {}

        # channel key: (ANY, None)
        vs_anychannel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
        )

        for msvs_instance in msvs_instances:

            debug(
                'msvs instance: id_str=%s, msvc_version=%s, vs_dir=%s, vs_exec=%s',
                repr(msvs_instance.id_str),
                repr(msvs_instance.msvc_version),
                repr(msvs_instance.vs_dir),
                repr(msvs_instance.vs_executable_norm),
                extra=cls.debug_extra,
            )

            # edition key: (product, ANY, None, None)
            vs_edition_any_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvs_instance.vs_product_def,
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
            )

            # edition key: (product, ANY, component, None)
            vs_edition_anychannel_component_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvs_instance.vs_product_def,
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvs_instance.vs_componentid_def,
            )

            # all editions keys
            vs_edition_keys = (
                vs_edition_any_key,
                msvs_instance.vs_edition_channel_key,
                vs_edition_anychannel_component_key,
                msvs_instance.vs_edition_channel_component_key,
                msvs_instance.vs_edition_channel_component_seqnbr_key,
            )

            # channel key: (ANY, component)
            vs_anychannel_component_key = _VSKeys.msvs_channel_key(
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvs_instance.vs_componentid_def,
            )

            # all channel keys
            vs_channel_keys = (
                vs_anychannel_key,
                msvs_instance.vs_channel_key,
                vs_anychannel_component_key,
                msvs_instance.vs_channel_component_key,
            )

            for vs_edition_key in vs_edition_keys:
                vs_edition_instances.setdefault(vs_edition_key, []).append(msvs_instance)

            for vs_channel_key in vs_channel_keys:
                vs_channel_instances.setdefault(vs_channel_key, []).append(msvs_instance)

            # msvc_version support

            if msvs_instance.msvc_version != msvs_instance.msvc_verstr:
                versions = [msvs_instance.msvc_verstr, msvs_instance.msvc_version]
            else:
                versions = [msvs_instance.msvc_verstr]

            vs_channel_defs = MSVC.Config.MSVS_CHANNEL_MEMBERLISTS[msvs_instance.vs_channel_def]

            for vcver in versions:
                for vs_channel_def in vs_channel_defs:

                    msvs_version_map = msvs_channel_map[vs_channel_def]

                    msvs_instance_list = msvs_version_map.setdefault(vcver, [])
                    slot = len(msvs_instance_list)
                    msvs_instance_list.append(msvs_instance)
                    debug(
                        'msvs_version_map[%s][%s][%d]=%s',
                        repr(vs_channel_def.vs_channel_suffix),
                        repr(vcver),
                        slot,
                        repr(msvs_instance.id_str),
                        extra=cls.debug_extra,
                    )

        msvs_installed = cls(
            msvs_instances=msvs_instances,
            msvs_edition_instances_map=vs_edition_instances,
            msvs_channel_instances_map=vs_channel_instances,
            msvs_channel_map=msvs_channel_map,
        )

        return msvs_installed

    def query_msvs_instances(
        self, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        # TODO(JCB): error checking combinations (ignored, etc)

        if not vs_channel_def:
            vs_channel_def = _msvs_channel_default()

        if vs_product_def:

            query_key = _VSKeys.msvs_edition_key(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            msvs_instances = self.msvs_edition_instances_map.get(query_key, [])

        else:

            query_key = _VSKeys.msvs_channel_key(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            msvs_instances = self.msvs_channel_instances_map.get(query_key, [])

        debug(
            'query_key=%s, n_msvs_instances=%s',
            repr(query_key.serialize()),
            repr(len(msvs_instances)),
            extra=self.debug_extra,
        )

        return query_key, msvs_instances

_MSVCInstance = namedtuple('_MSVCInstance', [
    'id_str',
    'msvs_base',
    'vc_version_def',
    'vc_feature_map',
    'vc_dir',
    'vc_dir_norm',
    'is_sdkversion_supported',
])

class MSVCInstance(_MSVCInstance, AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls):
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvs_base,
        vc_version_def,
        vc_feature_map,
        vc_dir,
    ):

        id_str = '{}({})'.format(cls.__name__, ', '.join(msvs_base.id_comps))

        if vc_feature_map is None:
            vc_feature_map = {}

        msvc_instance = cls(
            id_str=id_str,
            msvs_base=msvs_base,
            vc_version_def=vc_version_def,
            vc_feature_map=vc_feature_map,
            vc_dir=vc_dir,
            vc_dir_norm=normalize_path(vc_dir),
            is_sdkversion_supported=cls._is_sdkversion_supported(msvs_base),
        )

        return msvc_instance

    @staticmethod
    def default_order(a, b):
        return MSVSBase.default_order(a.msvs_base, b.msvs_base)

    @property
    def id_comps(self):
        return self.msvs_base.id_comps

    @property
    def msvs_instance(self):
        return self.msvs_base.msvs_instance

    @staticmethod
    def _is_sdkversion_supported(msvs_base):

        vs_componentid_def = msvs_base.vs_component_def.vs_componentid_def
        vs_product_numeric = msvs_base.vs_product_def.vs_product_numeric

        if vs_product_numeric >= 2017:
            # VS2017 and later
            is_supported = True
        elif vs_product_numeric == 2015:
            # VS2015:
            #   False: Express, BuildTools
            #   True:  Develop, CmdLine
            if vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_EXPRESS:
                is_supported = False
            elif vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_BUILDTOOLS:
                is_supported = False
            else:
                is_supported = True
        else:
            # VS2013 and earlier
            is_supported = False

        return is_supported

    def skip_uwp_target(self, env):
        skip = False
        if self.vc_feature_map:
            target_arch = env.get('TARGET_ARCH')
            uwp_target_is_supported = self.vc_feature_map.get('uwp_target_is_supported', {})
            is_supported = uwp_target_is_supported.get(target_arch, True)
            skip = bool(not is_supported)
        debug(
            'skip=%s, msvc_version=%s',
            repr(skip), repr(self.vc_version_def.msvc_version), extra=self.debug_extra
        )
        return skip

    def is_uwp_target_supported(self, target_arch=None):

        vs_componentid_def = self.msvs_base.vs_component_def.vs_componentid_def
        vs_product_numeric = self.msvs_base.vs_product_def.vs_product_numeric

        is_target = False
        if vs_product_numeric >= 2017:
            # VS2017 and later
            is_supported = True
        elif vs_product_numeric == 2015:
            # VS2015:
            #   Maybe: Express
            #   False: BuildTools
            #   True:  Develop, CmdLine
            if vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_EXPRESS:
                uwp_target_is_supported = self.vc_feature_map.get('uwp_target_is_supported', {})
                is_supported = uwp_target_is_supported.get(target_arch, True)
                is_target = True
            elif vs_componentid_def == MSVC.Config.MSVS_COMPONENTID_BUILDTOOLS:
                is_supported = False
            else:
                is_supported = True
        else:
            # VS2013 and earlier
            is_supported = False

        debug(
            'is_supported=%s, is_target=%s, msvc_version=%s, msvs_component=%s, target_arch=%s',
            is_supported, is_target,
            repr(self.vc_version_def.msvc_version),
            repr(vs_componentid_def.vs_component_id),
            repr(target_arch),
            extra=self.debug_extra,
        )

        return is_supported, is_target

    # convenience properties: reduce member lookup chain for readability

    @property
    def is_express(self):
        return self.msvs_base.is_express

    @property
    def is_buildtools(self):
        return self.msvs_base.is_buildtools

    @property
    def is_vcforpython(self):
        return self.msvs_base.is_vcforpython

    @property
    def vs_edition_channel_component_seqnbr_key(self):
        return self.msvs_base.vs_edition_channel_component_seqnbr_key

    @property
    def vs_edition_channel_component_key(self):
        return self.msvs_base.vs_edition_channel_component_key

    @property
    def vs_edition_channel_key(self):
        return self.msvs_base.vs_edition_channel_key

    @property
    def vs_channel_component_key(self):
        return self.msvs_base.vs_channel_component_key

    @property
    def vs_channel_key(self):
        return self.msvs_base.vs_channel_key

    @property
    def msvc_version(self):
        return self.vc_version_def.msvc_version

    @property
    def msvc_vernum(self):
        return self.vc_version_def.msvc_vernum

    @property
    def msvc_verstr(self):
        return self.vc_version_def.msvc_verstr

    @property
    def vs_product_def(self):
        return self.msvs_base.vs_product_def

    @property
    def vs_channel_def(self):
        return self.msvs_base.vs_channel_def

    @property
    def vs_componentid_def(self):
        return self.msvs_base.vs_component_def.vs_componentid_def

    @property
    def vs_product(self):
        return self.msvs_base.vs_product_def.vs_product

    @property
    def vs_product_numeric(self):
        return self.msvs_base.vs_product_def.vs_product_numeric

    @property
    def vs_channel_id(self):
        return self.msvs_base.vs_channel_def.vs_channel_id

    @property
    def vs_component_id(self):
        return self.msvs_base.vs_component_def.vs_componentid_def.vs_component_id

    @property
    def vs_sequence_nbr(self):
        return self.msvs_base.vs_sequence_nbr

_MSVCInstalled = namedtuple('_MSVCInstalled', [
    'msvc_instances',
    'msvs_edition_instances_map',
    'msvs_channel_instances_map',
    'msvs_channel_map', # TODO(JCB): remove?
])

class MSVCInstalled(_MSVCInstalled, AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls):
        cls.debug_extra = debug_extra(cls)

    @classmethod
    def factory(
        cls, *,
        msvc_instances,
    ):

        msvc_instances = sorted(
            msvc_instances, key=cmp_to_key(MSVCInstance.default_order)
        )

        msvs_channel_map = {
            vs_channel_def: {}
            for vs_channel_def in MSVC.Config.MSVS_CHANNEL_DEFINITION_LIST
        }

        vs_edition_instances = {}
        vs_channel_instances = {}

        # channel key: (ANY, None)
        vs_anychannel_key = _VSKeys.msvs_channel_key(
            vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
        )

        for msvc_instance in msvc_instances:

            debug(
                'msvc_instance: id_str=%s, msvc_version=%s, vc_dir=%s',
                repr(msvc_instance.id_str),
                repr(msvc_instance.msvc_version),
                repr(msvc_instance.vc_dir),
                extra=cls.debug_extra,
            )

            # edition key: (product, ANY, None, None)
            vs_edition_any_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvc_instance.vs_product_def,
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
            )

            # edition key: (product, ANY, component, None)
            vs_edition_anychannel_component_key = _VSKeys.msvs_edition_key(
                vs_product_def=msvc_instance.vs_product_def,
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvc_instance.vs_componentid_def,
            )

            # all editions keys
            vs_edition_keys = (
                vs_edition_any_key,
                msvc_instance.vs_edition_channel_key,
                vs_edition_anychannel_component_key,
                msvc_instance.vs_edition_channel_component_key,
                msvc_instance.vs_edition_channel_component_seqnbr_key,
            )

            # channel key: (ANY, component)
            vs_anychannel_component_key = _VSKeys.msvs_channel_key(
                vs_channel_def=MSVC.Config.MSVS_CHANNEL_ANY,
                vs_componentid_def=msvc_instance.vs_componentid_def,
            )

            # all channel keys
            vs_channel_keys = (
                vs_anychannel_key,
                msvc_instance.vs_channel_key,
                vs_anychannel_component_key,
                msvc_instance.vs_channel_component_key,
            )

            for vs_edition_key in vs_edition_keys:
                vs_edition_instances.setdefault(vs_edition_key, []).append(msvc_instance)

            for vs_channel_key in vs_channel_keys:
                vs_channel_instances.setdefault(vs_channel_key, []).append(msvc_instance)

            # msvc_version support

            if msvc_instance.msvc_version != msvc_instance.msvc_verstr:
                versions = [msvc_instance.msvc_verstr, msvc_instance.msvc_version]
            else:
                versions = [msvc_instance.msvc_verstr]

            vs_channel_defs = MSVC.Config.MSVS_CHANNEL_MEMBERLISTS[msvc_instance.vs_channel_def]

            for vcver in versions:

                for vs_channel_def in vs_channel_defs:

                    msvc_version_map = msvs_channel_map[vs_channel_def]

                    msvc_instance_list = msvc_version_map.setdefault(vcver, [])
                    slot = len(msvc_instance_list)
                    msvc_instance_list.append(msvc_instance)
                    debug(
                        'msvc_version_map[%s][%s][%d]=%s',
                        repr(vs_channel_def.vs_channel_suffix),
                        repr(vcver),
                        slot,
                        repr(msvc_instance.id_str),
                        extra=cls.debug_extra,
                    )

        msvc_installed = cls(
            msvc_instances=msvc_instances,
            msvs_edition_instances_map=vs_edition_instances,
            msvs_channel_instances_map=vs_channel_instances,
            msvs_channel_map=msvs_channel_map,
        )

        return msvc_installed

    def query_msvc_instances(
        self, *,
        vs_product_def=None,
        vs_channel_def=None,
        vs_componentid_def=None,
        vs_sequence_nbr=None,
    ):

        # TODO(JCB): error checking combinations (ignored, etc)

        if not vs_channel_def:
            vs_channel_def = _msvs_channel_default()

        if vs_product_def:

            query_key = _VSKeys.msvs_edition_key(
                vs_product_def=vs_product_def,
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
                vs_sequence_nbr=vs_sequence_nbr
            )

            msvc_instances = self.msvs_edition_instances_map.get(query_key, [])

        else:

            query_key = _VSKeys.msvs_channel_key(
                vs_channel_def=vs_channel_def,
                vs_componentid_def=vs_componentid_def,
            )

            msvc_instances = self.msvs_channel_instances_map.get(query_key, [])

        debug(
            'query_key=%s, n_msvc_instances=%s',
            repr(query_key.serialize()),
            repr(len(msvc_instances)),
            extra=self.debug_extra,
        )

        return query_key, msvc_instances

_MSVSManager = namedtuple('_MSVSManager', [
    'msvc_installed',
    'msvs_installed',
])

class MSVSManager(_MSVSManager):

    @classmethod
    def factory(cls, msvc_installed, msvs_installed):

        msvs_manager = cls(
            msvc_installed=msvc_installed,
            msvs_installed=msvs_installed,
        )

        return msvs_manager

class _VSDetect(AutoInitialize):

    debug_extra = None

    @classmethod
    def _initialize(cls):
        cls.debug_extra = debug_extra(cls)
        cls.reset()

    @classmethod
    def reset(cls):

        cls.vswhere_executable_seen = set()
        cls.vswhere_executables = []

        cls.registry_once = False

        cls.vs_dir_seen = set()  # vswhere
        cls.vc_dir_seen = set()  # registry

        cls.msvs_sequence_nbr = {}

        cls.msvs_instances = []
        cls.msvc_instances = []

        # volatile: reconstructed when new instances detected
        cls.msvs_manager = None

    reset_funcs = []

    @classmethod
    def register_reset_func(cls, func):
        cls.reset_funcs.append(func)

    @classmethod
    def call_reset_funcs(cls):
        for func in cls.reset_funcs:
            func()

    @classmethod
    def _msvc_dir_evaluate(
        cls, *,
        vs_product_def,
        vs_component_def,
        vs_channel_def,
        vs_dir,
        vs_version,
        vs_exec,
        vc_version,
        vc_dir,
        vc_feature_map=None,
    ):

        vs_sequence_key = (vs_product_def, vs_channel_def, vs_component_def)

        cls.msvs_sequence_nbr.setdefault(vs_sequence_key, 0)
        cls.msvs_sequence_nbr[vs_sequence_key] += 1

        vs_sequence_nbr = cls.msvs_sequence_nbr[vs_sequence_key]

        msvs_base = MSVSBase.factory(
            vs_product_def=vs_product_def,
            vs_channel_def=vs_channel_def,
            vs_component_def=vs_component_def,
            vs_sequence_nbr=vs_sequence_nbr,
            vs_dir=vs_dir,
            vs_version=vs_version,
        )

        if msvs_base.is_express:
            vc_version += msvs_base.vs_component_suffix

        vc_version_def = MSVC.Util.msvc_version_components(vc_version)

        msvc_instance = MSVCInstance.factory(
            msvs_base=msvs_base,
            vc_version_def=vc_version_def,
            vc_feature_map=vc_feature_map,
            vc_dir=vc_dir,
        )

        # TODO(JCB): load toolsets/tools
        if not _msvc_instance_check_files_exist(msvc_instance):
            # no compilers detected don't register msvc_instance
            return None

        msvs_base.register_msvc_instance(msvc_instance)
        cls.msvc_instances.append(msvc_instance)

        if vs_exec:

            msvs_instance = MSVSInstance.factory(
                msvs_base=msvs_base,
                vs_executable=vs_exec,
                vc_version_def=vc_version_def,
            )

            msvs_base.register_msvs_instance(msvs_instance)
            cls.msvs_instances.append(msvs_instance)

        return msvc_instance

    @classmethod
    def _filter_vswhere_paths(cls, vswhere_env=None):
        vswhere_paths = [
            vswhere_exec.norm
            for vswhere_exec in _find_vswhere_executables(vswhere_env)
            if vswhere_exec.norm not in cls.vswhere_executable_seen
        ]
        debug('vswhere_paths=%s', vswhere_paths, extra=cls.debug_extra)
        return vswhere_paths

    @classmethod
    def _vswhere_query_json_output(cls, vswhere_exe, vswhere_args):

        vswhere_json = None

        once = True
        while once:
            once = False
            # using break for single exit (unless exception)

            vswhere_cmd = [vswhere_exe] + vswhere_args + ['-format', 'json', '-utf8']
            debug("running: %s", vswhere_cmd, extra=cls.debug_extra)

            try:
                cp = subprocess.run(
                    vswhere_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
                )
            except OSError as e:
                errmsg = str(e)
                debug("%s: %s", type(e).__name__, errmsg, extra=cls.debug_extra)
                break
            except Exception as e:
                errmsg = str(e)
                debug("%s: %s", type(e).__name__, errmsg, extra=cls.debug_extra)
                raise

            if not cp.stdout:
                debug("no vswhere information returned", extra=cls.debug_extra)
                break

            vswhere_output = cp.stdout.decode('utf8', errors='replace')
            if not vswhere_output:
                debug("no vswhere information output", extra=cls.debug_extra)
                break

            try:
                vswhere_output_json = json.loads(vswhere_output)
            except json.decoder.JSONDecodeError:
                debug("json decode exception loading vswhere output", extra=cls.debug_extra)
                break

            vswhere_json = vswhere_output_json
            break

        debug(
            'vswhere_json=%s, vswhere_exe=%s',
            bool(vswhere_json), repr(vswhere_exe), extra=cls.debug_extra
        )

        return vswhere_json

    @classmethod
    def _msvc_instances_vswhere(cls, vswhere_env=None):

        num_instances = len(cls.msvc_instances)
        num_new_instances = 0

        vswhere_paths = cls._filter_vswhere_paths(vswhere_env)
        if vswhere_paths:

            num_beg_instances = num_instances

            for vswhere_exe in vswhere_paths:

                if vswhere_exe in cls.vswhere_executable_seen:
                    continue

                cls.vswhere_executable_seen.add(vswhere_exe)
                cls.vswhere_executables.append(vswhere_exe)

                debug('vswhere_exe=%s', repr(vswhere_exe), extra=cls.debug_extra)

                vswhere_json = cls._vswhere_query_json_output(
                    vswhere_exe,
                    ['-all', '-products', '*', '-prerelease']
                )

                if not vswhere_json:
                    continue

                for instance in vswhere_json:

                    #print(json.dumps(instance, indent=4, sort_keys=True))

                    vs_dir = instance.get('installationPath')
                    if not vs_dir or not path_exists(vs_dir):
                        continue

                    vs_norm = normalize_path(vs_dir)
                    if vs_norm in cls.vs_dir_seen:
                        continue

                    vs_version = instance.get('installationVersion')
                    if not vs_version:
                        continue

                    product_id = instance.get('productId')
                    if not product_id:
                        continue

                    # consider msvs root evaluated at this point
                    cls.vs_dir_seen.add(vs_norm)

                    vc_dir = os.path.join(vs_dir, 'VC')
                    if not path_exists(vc_dir):
                        continue

                    vs_major = vs_version.split('.')[0]
                    if vs_major not in MSVC.Config.MSVS_VERSION_MAJOR_MAP:
                        debug('ignore vs_major: %s', vs_major, extra=cls.debug_extra)
                        continue

                    vs_product_def = MSVC.Config.MSVS_VERSION_MAJOR_MAP[vs_major]

                    component_id = product_id.split('.')[-1]
                    vs_component_def = MSVC.Config.VSWHERE_COMPONENT_INTERNAL.get(component_id)
                    if not vs_component_def:
                        debug('ignore component_id: %s', component_id, extra=cls.debug_extra)
                        continue

                    is_prerelease = True if instance.get('isPrerelease', False) else False
                    if is_prerelease:
                        vs_channel_def = MSVC.Config.MSVS_CHANNEL_PREVIEW
                    else:
                        vs_channel_def = MSVC.Config.MSVS_CHANNEL_RELEASE

                    vc_version = MSVC.Config.VSWHERE_VSMAJOR_TO_VCVERSION[vs_major]

                    vs_exec = MSVC.Kind.msvc_dir_vswhere(
                        vc_dir,
                        _VSPRODUCT_KIND_DETECT[vs_product_def.vs_product],
                    )

                    cls._msvc_dir_evaluate(
                        vs_product_def=vs_product_def,
                        vs_component_def=vs_component_def,
                        vs_channel_def=vs_channel_def,
                        vs_dir=vs_dir,
                        vs_version=vs_version,
                        vs_exec=vs_exec,
                        vc_version=vc_version,
                        vc_dir=vc_dir,
                    )

            num_instances = len(cls.msvc_instances)
            num_new_instances = num_instances - num_beg_instances

            if num_new_instances > 0:
                cls.call_reset_funcs()
                debug('num_new_instances=%s, num_instances=%s', num_new_instances, num_instances, extra=cls.debug_extra)

        return num_new_instances

    @classmethod
    def _msvc_instances_registry(cls):

        num_instances = len(cls.msvc_instances)
        num_new_instances = 0

        if not cls.registry_once:
            cls.registry_once = True

            num_beg_instances = num_instances

            is_win64 = common.is_win64()

            for vs_product, regkeys in _VSPRODUCT_REGISTRY_VCDIR.items():

                key_prefix = 'Software\\'
                for is_vsroot, is_vcforpython, hkroot, key in regkeys:

                    if not hkroot or not key:
                        continue

                    if is_win64:
                        msregkeys = [key_prefix + 'Wow6432Node\\' + key, key_prefix + key]
                    else:
                        msregkeys = [key_prefix + key]

                    vc_dir = None
                    for msregkey in msregkeys:
                        debug('trying VC registry key %s', repr(msregkey), extra=cls.debug_extra)
                        try:
                            vc_dir = common.read_reg(msregkey, hkroot)
                        except OSError:
                            continue
                        if vc_dir:
                            break

                    if not vc_dir:
                        debug('no VC registry key %s', repr(key), extra=cls.debug_extra)
                        continue

                    if vc_dir in cls.vc_dir_seen:
                        continue
                    cls.vc_dir_seen.add(vc_dir)

                    if not os.path.exists(vc_dir):
                        debug(
                            'reg says vc dir is %s, but it does not exist. (ignoring)',
                            repr(vc_dir), extra=cls.debug_extra
                        )
                        continue

                    if is_vsroot:

                        vc_dir = os.path.join(vc_dir, 'VC')
                        debug('convert vs dir to vc dir: %s', repr(vc_dir), extra=cls.debug_extra)

                        if vc_dir in cls.vc_dir_seen:
                            continue
                        cls.vc_dir_seen.add(vc_dir)

                        if not os.path.exists(vc_dir):
                            debug('vc dir does not exist. (ignoring)', repr(vc_dir), extra=cls.debug_extra)
                            continue

                    vc_norm = normalize_path(vc_dir)
                    if vc_norm in cls.vc_dir_seen:
                        continue
                    cls.vc_dir_seen.add(vc_norm)

                    vs_product_def = MSVC.Config.MSVS_VERSION_INTERNAL[vs_product]
                    vc_version =  vs_product_def.vc_buildtools_def.vc_version

                    vs_component_def, vs_dir, vs_exec, vc_feature_map = MSVC.Kind.msvc_dir_registry(
                        vc_norm,
                        _VSPRODUCT_KIND_DETECT[vs_product_def.vs_product],
                        vc_version,
                        is_vcforpython,
                        vs_product_def.vs_version
                    )

                    if not vs_component_def:
                        continue

                    vs_channel_def = MSVC.Config.MSVS_CHANNEL_RELEASE

                    cls._msvc_dir_evaluate(
                        vs_product_def=vs_product_def,
                        vs_component_def=vs_component_def,
                        vs_channel_def=vs_channel_def,
                        vs_dir=vs_dir,
                        vs_version=vs_product_def.vs_version,
                        vs_exec=vs_exec,
                        vc_version=vc_version,
                        vc_dir=vc_dir,
                        vc_feature_map=vc_feature_map,
                    )

            num_instances = len(cls.msvc_instances)
            num_new_instances = num_instances - num_beg_instances

        return num_new_instances

    @classmethod
    def detect(cls, vswhere_env=None):

        num_new_instances = 0
        num_new_instances += cls._msvc_instances_vswhere(vswhere_env)
        num_new_instances += cls._msvc_instances_registry()

        if num_new_instances > 0 or cls.msvs_manager is None:

            msvc_installed = MSVCInstalled.factory(
                msvc_instances=cls.msvc_instances,
            )

            msvs_installed = MSVSInstalled.factory(
                msvs_instances=cls.msvs_instances,
            )

            cls.msvs_manager = MSVSManager.factory(
                msvc_installed=msvc_installed,
                msvs_installed=msvs_installed,
            )

        return cls.msvs_manager

def vs_detect(env=None):
    vswhere_env = env.subst('$VSWHERE') if env and 'VSWHERE' in env else None
    msvs_manager = _VSDetect.detect(vswhere_env)
    return msvs_manager

def _query_key_components(msvc_version, env=None):

    # TODO(JCB): temporary placeholder

    prefix, suffix = MSVC.Util.get_msvc_version_prefix_suffix(msvc_version)

    vs_product_def = MSVC.Config.MSVC_VERSION_INTERNAL[prefix]

    vs_channel_def = None

    if suffix == 'Exp':
        vs_componentid_def = MSVC.Config.MSVS_COMPONENTID_EXPRESS
    else:
        vs_componentid_def = None

    return vs_product_def, vs_componentid_def, vs_channel_def

def _find_msvc_instance(msvc_version, env=None):

    msvc_instance = None
    query_key = None

    if msvc_version not in _VCVER:
        # TODO(JCB): issue warning (add policy?)
        debug("Unknown version of MSVC: %s", repr(msvc_version))
        return msvc_instance, query_key

    vs_manager = vs_detect(env)

    vs_product_def, vs_componentid_def, vs_channel_def = _query_key_components(msvc_version, env)

    query_key, msvc_instances = vs_manager.msvc_installed.query_msvc_instances(
        vs_product_def=vs_product_def,
        vs_componentid_def=vs_componentid_def,
        vs_channel_def=vs_channel_def,
    )

    msvc_instance = msvc_instances[0] if msvc_instances else None

    debug(
        'msvc_version=%s, vc_dir=%s',
        repr(msvc_version),
        repr(msvc_instance.vc_dir if msvc_instance else None)
    )

    return msvc_instance, query_key

def find_msvc_instance(msvc_version, env=None):
    """Select an MSVC installation record.

    Args:
        msvc_version: str
            msvc version (major.minor, e.g. 10.0)
        env: optional
            env to look up construction variables

    Returns:
        str: MSVC installation record or None
    """
    msvc_instance, _ = _find_msvc_instance(msvc_version, env)
    return msvc_instance

def _reset_installed_queries():
    debug('reset')
    global _cache_user_vswhere_path
    _cache_user_vswhere_paths = {}

def find_batch_file(msvc_instance, host_arch, target_arch):
    """
    Find the location of the batch script which should set up the compiler
    for any TARGET_ARCH whose compilers were installed by Visual Studio/VCExpress

    In newer (2017+) compilers, make use of the fact there are vcvars
    scripts named with a host_target pair that calls vcvarsall.bat properly,
    so use that and return an empty argument.
    """

    arg = ''
    batfilename = None
    clexe = None
    depbat = None

    pdir = msvc_instance.vc_dir

    if msvc_instance.vs_product_numeric >= 2022:
        # 14.3 (VS2022) and later
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        batfile, _ = _GE2022_HOST_TARGET_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, batfile)
    elif 2022 > msvc_instance.vs_product_numeric >= 2017:
        # 14.2 (VS2019) to 14.1 (VS2017)
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        batfile, _ = _LE2019_HOST_TARGET_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, batfile)
    elif 2017 > msvc_instance.vs_product_numeric >= 2010:
        # 14.0 (VS2015) to 10.0 (VS2010)
        arg, batfile, cl_path_comps = _LE2015_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(pdir, "vcvarsall.bat")
        depbat = os.path.join(pdir, *cl_path_comps, batfile)
        clexe = os.path.join(pdir, *cl_path_comps, _CL_EXE_NAME)
    elif 2010 > msvc_instance.vs_product_numeric >= 2005:
        # 9.0 (VS2008) to 8.0 (VS2005)
        arg, batfile, cl_path_comps = _LE2008_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        if msvc_instance.is_vcforpython:
            # 9.0 (VS2008) Visual C++ for Python:
            #     sdk batch files do not point to the VCForPython installation
            #     vcvarsall batch file is in installdir not productdir (e.g., vc\..\vcvarsall.bat)
            #     dependency batch files are not called from vcvarsall.bat
            batfilename = os.path.join(pdir, os.pardir, "vcvarsall.bat")
            depbat = None
        else:
            batfilename = os.path.join(pdir, "vcvarsall.bat")
            depbat = os.path.join(pdir, *cl_path_comps, batfile)
        clexe = os.path.join(pdir, *cl_path_comps, _CL_EXE_NAME)
    else:  # 2005 > vc_product_numeric >= 6.0
        # 7.1 (VS2003) and earlier
        pdir = os.path.join(pdir, "Bin")
        batfilename = os.path.join(pdir, "vcvars32.bat")
        clexe = os.path.join(pdir, _CL_EXE_NAME)

    if not os.path.exists(batfilename):
        debug("batch file not found: %s", batfilename)
        batfilename = None

    if clexe and not os.path.exists(clexe):
        debug("%s not found: %s", _CL_EXE_NAME, clexe)
        batfilename = None

    if depbat and not os.path.exists(depbat):
        debug("dependency batch file not found: %s", depbat)
        batfilename = None

    return batfilename, arg

# TODO(JCB): test and remove (orphaned)
def find_batch_file_sdk(host_arch, target_arch, sdk_pdir):
    """
    Find the location of the sdk batch script which should set up the compiler
    for any TARGET_ARCH whose compilers were installed by Visual Studio/VCExpress
    """
    from .sdk import get_installed_sdks

    installed_sdks = get_installed_sdks()
    for _sdk in installed_sdks:
        sdk_bat_file = _sdk.get_sdk_vc_script(host_arch, target_arch)
        if not sdk_bat_file:
            debug("sdk batch file not found:%s", _sdk)
        else:
            sdk_bat_file_path = os.path.join(sdk_pdir, sdk_bat_file)
            if os.path.exists(sdk_bat_file_path):
                debug('sdk_bat_file_path:%s', sdk_bat_file_path)
                return sdk_bat_file_path

    return None

_cache_installed_msvc_versions = None
_cache_installed_msvc_instances = None

def _reset_installed_vcs():
    global _cache_installed_msvc_versions
    global _cache_installed_msvc_instances
    _cache_installed_msvc_versions = None
    _cache_installed_msvc_instances = None
    debug('reset')

# register vcs cache reset function with vsdetect state manager
_VSDetect.register_reset_func(_reset_installed_vcs)

_VC_TOOLS_VERSION_FILE_PATH = ['Auxiliary', 'Build', 'Microsoft.VCToolsVersion.default.txt']
_VC_TOOLS_VERSION_FILE = os.sep.join(_VC_TOOLS_VERSION_FILE_PATH)

def _msvc_instance_check_files_exist(msvc_instance) -> bool:
    """Return status of finding at least one batch file and cl.exe.

    Locates at least one required vcvars batch file and cl.ex in the vc_dir.
    The native platform is assumed for the host and all associated targets.

    Args:
        msvc_instance:
            MSVC installation record

    Returns:
        bool:

    """

    # Find the host, target, and all candidate (host, target) platform combinations:
    platforms = get_host_target(None, msvc_instance.msvc_version, all_host_targets=True)
    debug("host_platform=%s, target_platform=%s, host_target_list=%s", *platforms)
    host_platform, target_platform, host_target_list = platforms

    # make sure the cl.exe exists meaning the tool is installed
    if msvc_instance.vs_product_numeric >= 2017:
        # 14.1 (VS2017) and later
        # 2017 and newer allowed multiple versions of the VC toolset to be
        # installed at the same time. This changes the layout.
        # Just get the default tool version for now
        # TODO: support setting a specific minor VC version
        default_toolset_file = os.path.join(msvc_instance.vc_dir, _VC_TOOLS_VERSION_FILE)
        try:
            with open(default_toolset_file) as f:
                vc_specific_version = f.readlines()[0].strip()
        except OSError:
            debug('failed to read %s', default_toolset_file)
            return False
        except IndexError:
            debug('failed to find MSVC version in %s', default_toolset_file)
            return False

        if msvc_instance.vs_product_numeric >= 2022:
            # 14.3 (VS2022) and later
            host_target_batchfile_clpathcomps = _GE2022_HOST_TARGET_BATCHFILE_CLPATHCOMPS
        else:
            # 14.2 (VS2019) to 14.1 (VS2017)
            host_target_batchfile_clpathcomps = _LE2019_HOST_TARGET_BATCHFILE_CLPATHCOMPS

        for host_platform, target_platform in host_target_list:

            debug(
                'host_platform=%s, target_platform=%s, msvc_version=%s',
                host_platform, target_platform, msvc_instance.msvc_version
            )

            batchfile_clpathcomps = host_target_batchfile_clpathcomps.get((host_platform, target_platform), None)
            if batchfile_clpathcomps is None:
                debug('unsupported host/target platform combo: (%s,%s)', host_platform, target_platform)
                continue

            batfile, cl_path_comps = batchfile_clpathcomps

            batfile_path = os.path.join(msvc_instance.vc_dir, "Auxiliary", "Build", batfile)
            if not os.path.exists(batfile_path):
                debug("batch file not found: %s", batfile_path)
                continue

            cl_path = os.path.join(
                msvc_instance.vc_dir, 'Tools', 'MSVC', vc_specific_version, *cl_path_comps, _CL_EXE_NAME
            )
            if not os.path.exists(cl_path):
                debug("%s not found: %s", _CL_EXE_NAME, cl_path)
                continue

            debug('%s found: %s', _CL_EXE_NAME, cl_path)
            return True

    elif 2017 > msvc_instance.vs_product_numeric >= 2005:
        # 14.0 (VS2015) to 8.0 (VS2005)

        if msvc_instance.vs_product_numeric >= 2010:
            # 14.0 (VS2015) to 10.0 (VS2010)
            host_target_batcharg_batchfile_clpathcomps = _LE2015_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS
        else:
            # 9.0 (VS2008) to 8.0 (VS2005)
            host_target_batcharg_batchfile_clpathcomps = _LE2008_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS

        if msvc_instance.is_vcforpython:
            # 9.0 (VS2008) Visual C++ for Python:
            #     vcvarsall batch file is in installdir not productdir (e.g., vc\..\vcvarsall.bat)
            #     dependency batch files are not called from vcvarsall.bat
            batfile_path = os.path.join(msvc_instance.vc_dir, os.pardir, "vcvarsall.bat")
            check_depbat = False
        else:
            batfile_path = os.path.join(msvc_instance.vc_dir, "vcvarsall.bat")
            check_depbat = True

        if not os.path.exists(batfile_path):
            debug("batch file not found: %s", batfile_path)
            return False

        for host_platform, target_platform in host_target_list:

            debug(
                'host_platform=%s, target_platform=%s, msvc_version=%s',
                host_platform, target_platform, msvc_instance.msvc_version
            )

            batcharg_batchfile_clpathcomps = host_target_batcharg_batchfile_clpathcomps.get(
                (host_platform, target_platform), None
            )

            if batcharg_batchfile_clpathcomps is None:
                debug('unsupported host/target platform combo: (%s,%s)', host_platform, target_platform)
                continue

            _, batfile, cl_path_comps = batcharg_batchfile_clpathcomps

            if check_depbat:
                batfile_path = os.path.join(msvc_instance.vc_dir, *cl_path_comps, batfile)
                if not os.path.exists(batfile_path):
                    debug("batch file not found: %s", batfile_path)
                    continue

            cl_path = os.path.join(msvc_instance.vc_dir, *cl_path_comps, _CL_EXE_NAME)
            if not os.path.exists(cl_path):
                debug("%s not found: %s", _CL_EXE_NAME, cl_path)
                continue

            debug('%s found: %s', _CL_EXE_NAME, cl_path)
            return True

    elif 2005 > msvc_instance.vs_product_numeric >= 1998:
        # 7.1 (VS2003) to 6.0 (VS6)

        bin_dir = os.path.join(msvc_instance.vc_dir, "bin")

        batfile_path = os.path.join(bin_dir, "vcvars32.bat")
        if not os.path.exists(batfile_path):
            debug("batch file not found: %s", batfile_path)
            return False

        cl_path = os.path.join(bin_dir, _CL_EXE_NAME)
        if not os.path.exists(cl_path):
            debug("%s not found: %s", _CL_EXE_NAME, cl_path)
            return False

        debug('%s found: %s', _CL_EXE_NAME, cl_path)
        return True

    else:
        # version not supported return false
        debug('unsupported MSVC version: %s', str(msvc_instance.msvc_version))

    return False

def get_installed_msvc_instances(env=None):
    global _cache_installed_msvc_instances

    # the installed instance cache is cleared if new instances are discovered
    vs_manager = vs_detect(env)

    if _cache_installed_msvc_instances is not None:
        return _cache_installed_msvc_instances

    msvc_installed = vs_manager.msvc_installed

    # TODO(JCB): first-use default channel
    vs_channel_def = _msvs_channel_default()

    msvs_channel_map = msvc_installed.msvs_channel_map
    msvc_version_map = msvs_channel_map.get(vs_channel_def)

    installed_msvc_instances = [
        msvc_version_map[vc_version][0]
        for vc_version in msvc_version_map.keys()
    ]

    _cache_installed_msvc_instances = installed_msvc_instances
    # debug("installed_msvc_instances=%s", _cache_installed_msvc_versions)
    return _cache_installed_msvc_instances

def get_installed_vcs(env=None):
    global _cache_installed_msvc_versions

    # the installed version cache is cleared if new instances are discovered
    vs_manager = vs_detect(env)

    if _cache_installed_msvc_versions is not None:
        return _cache_installed_msvc_versions

    msvc_installed = vs_manager.msvc_installed

    # TODO(JCB): first-use default channel
    vs_channel_def = _msvs_channel_default()

    msvs_channel_map = msvc_installed.msvs_channel_map
    msvc_version_map = msvs_channel_map.get(vs_channel_def)

    installed_msvc_versions = [
        vc_version
        for vc_version in msvc_version_map.keys()
    ]

    _cache_installed_msvc_versions = installed_msvc_versions
    debug("installed_msvc_versions=%s", _cache_installed_msvc_versions)
    return _cache_installed_msvc_versions

def reset_installed_vcs() -> None:
    """Make it try again to find VC.  This is just for the tests."""
    _reset_installed_vcs()
    _reset_installed_queries()
    _VSDetect.reset()
    MSVC._reset()

def msvc_default_version(env=None):
    """Get default msvc version."""
    vcs = get_installed_vcs(env)
    msvc_version = vcs[0] if vcs else None
    debug('msvc_version=%s', repr(msvc_version))
    return msvc_version

def get_installed_vcs_components(env=None):
    """Test suite convenience function: return list of installed msvc version component tuples"""
    vcs = get_installed_vcs(env)
    msvc_version_component_defs = [MSVC.Util.msvc_version_components(vcver) for vcver in vcs]
    return msvc_version_component_defs

def _check_cl_exists_in_script_env(data):
    """Find cl.exe in the script environment path."""
    cl_path = None
    if data and 'PATH' in data:
        for p in data['PATH']:
            cl_exe = os.path.join(p, _CL_EXE_NAME)
            if os.path.exists(cl_exe):
                cl_path = cl_exe
                break
    have_cl = True if cl_path else False
    debug('have_cl: %s, cl_path: %s', have_cl, cl_path)
    return have_cl, cl_path

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

def script_env(env, script, args=None):
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
        skip_sendtelemetry = _skip_sendtelemetry(env)
        stdout = common.get_output(script, args, skip_sendtelemetry=skip_sendtelemetry)
        cache_data = common.parse_output(stdout)

        # debug(stdout)
        olines = stdout.splitlines()

        # process stdout: batch file errors (not necessarily first line)
        script_errlog = []
        for line in olines:
            if re_script_output_error.match(line):
                if not script_errlog:
                    script_errlog.append('vc script errors detected:')
                script_errlog.append(line)

        if script_errlog:
            script_errmsg = '\n'.join(script_errlog)

            have_cl, _ = _check_cl_exists_in_script_env(cache_data)

            debug(
                'script=%s args=%s have_cl=%s, errors=%s',
                repr(script), repr(args), repr(have_cl), script_errmsg
            )
            MSVC.Policy.msvc_scripterror_handler(env, script_errmsg)

            if not have_cl:
                # detected errors, cl.exe not on path
                raise BatchFileExecutionError(script_errmsg)

        # once we updated cache, give a chance to write out if user wanted
        script_env_cache[cache_key] = cache_data
        common.write_script_env_cache(script_env_cache)

    return cache_data

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
                    "Requested msvc version (%s) and msvs version (%s) do "
                    "not match: please use MSVC_VERSION only to request a "
                    "visual studio version, MSVS_VERSION is deprecated"
                    % (msvc_version, msvs_version))
        return msvs_version

    if not msvc_version:
        msvc_version = msvc_default_version(env)
        if not msvc_version:
            #SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
            debug('No installed VCs')
            return None
        debug('using default installed MSVC version %s', repr(msvc_version))
    else:
        debug('using specified MSVC version %s', repr(msvc_version))

    return msvc_version

def msvc_setup_env_once(env, tool=None) -> None:
    try:
        has_run = env["MSVC_SETUP_RUN"]
    except KeyError:
        has_run = False

    if not has_run:
        MSVC.SetupEnvDefault.register_setup(env, msvc_exists)
        msvc_setup_env(env)
        env["MSVC_SETUP_RUN"] = True

    req_tools = MSVC.SetupEnvDefault.register_iserror(env, tool, msvc_exists)
    if req_tools:
        msg = "No versions of the MSVC compiler were found.\n" \
              "  Visual Studio C/C++ compilers may not be set correctly.\n" \
              "  Requested tool(s) are: {}".format(req_tools)
        MSVC.Policy.msvc_notfound_handler(env, msg)

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

    msvc_instance, msvc_query_key = _find_msvc_instance(version, env)

    debug(
        'version=%s, query_key=%s, vc_dir=%s',
        version,
        repr(msvc_query_key.serialize()) if msvc_query_key else None,
        msvc_instance.vc_dir if msvc_instance else None
    )

    d = None
    version_installed = False

    if msvc_instance:

        # Find the host, target, and all candidate (host, target) platform combinations:
        platforms = get_host_target(env, msvc_instance.msvc_version)
        debug("host_platform %s, target_platform %s host_target_list %s", *platforms)
        host_platform, target_platform, host_target_list = platforms

        for host_arch, target_arch, in host_target_list:
            # Set to current arch.
            env['TARGET_ARCH'] = target_arch
            arg = ''

            # Try to locate a batch file for this host/target platform combo
            try:
                vc_script, arg = find_batch_file(msvc_instance, host_arch, target_arch)
                debug('vc_script:%s vc_script_arg:%s', vc_script, arg)
                version_installed = True
            except VisualCException as e:
                msg = str(e)
                debug('Caught exception while looking for batch file (%s)', msg)
                version_installed = False
                continue

            if not vc_script:
                continue

            if not target_platform and MSVC.ScriptArguments.msvc_script_arguments_has_uwp(env):
                # no target arch specified and is a store/uwp build
                if msvc_instance.skip_uwp_target(env):
                    # store/uwp may not be supported for all express targets (prevent constraint error)
                    debug('skip uwp target arch: version=%s, target=%s', repr(version), repr(target_arch))
                    continue

            # Try to use the located batch file for this host/target platform combo
            arg = MSVC.ScriptArguments.msvc_script_arguments(env, msvc_instance, arg)
            debug('trying vc_script:%s, vc_script_args:%s', repr(vc_script), arg)
            try:
                d = script_env(env, vc_script, args=arg)
            except BatchFileExecutionError as e:
                debug('failed vc_script:%s, vc_script_args:%s, error:%s', repr(vc_script), arg, e)
                vc_script = None
                continue

            have_cl, _ = _check_cl_exists_in_script_env(d)
            if not have_cl:
                debug('skip cl.exe not found vc_script:%s, vc_script_args:%s', repr(vc_script), arg)
                continue

            debug("Found a working script/target: %s/%s", repr(vc_script), arg)
            break # We've found a working target_platform, so stop looking

        # If we cannot find a viable installed compiler, reset the TARGET_ARCH
        # To it's initial value
        if not d:
            env['TARGET_ARCH'] = target_platform

    if not d:

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

        MSVC.Policy.msvc_notfound_handler(env, msg)

    return d

MSVCAction = namedtuple("MSVCAction", [
    'action',
])

MSVC_ACTION_SCRIPT = MSVCAction(action='SCRIPT')
MSVC_ACTION_SELECT = MSVCAction(action='SELECT')
MSVC_ACTION_SETTINGS = MSVCAction(action='SETTINGS')
MSVC_ACTION_BYPASS = MSVCAction(action='BYPASS')

def _msvc_action(env):

    #   use_script  use_settings   return    description
    #   ---------- --------------  --------  ----------------
    #     string      ignored      SCRIPT    use script
    #   eval false    ignored      BYPASS    bypass detection
    #   eval true     ignored      SELECT    msvc selection
    #   undefined  value not None  SETTINGS  use dictionary
    #   undefined  undefined/None  SELECT    msvc selection

    msvc_action = None

    use_script = env.get('MSVC_USE_SCRIPT', UNDEFINED)
    use_settings = env.get('MSVC_USE_SETTINGS', None)

    if use_script != UNDEFINED:
        # use script defined
        if SCons.Util.is_String(use_script):
            # use_script is string, use_settings ignored
            msvc_action = MSVC_ACTION_SCRIPT
        elif not use_script:
            # use_script eval false, use_settings ignored
            msvc_action = MSVC_ACTION_BYPASS
        else:
            # use script eval true, use_settings ignored
            msvc_action = MSVC_ACTION_SELECT
    elif use_settings is not None:
        # use script undefined, use_settings defined and not None (type checked)
        msvc_action = MSVC_ACTION_SETTINGS
    else:
        # use script undefined, use_settings undefined or None
        msvc_action = MSVC_ACTION_SELECT

    if not msvc_action:
        errmsg = 'msvc_action is undefined'
        debug('MSVCInternalError: %s', errmsg)
        raise MSVCInternalError(errmsg)

    return msvc_action, use_script, use_settings

def msvc_setup_env(env):
    debug('called')
    version = get_default_version(env)
    if version is None:
        if not msvc_setup_env_user(env):
            MSVC.SetupEnvDefault.set_nodefault()
        return None

    # XXX: we set-up both MSVS version for backward
    # compatibility with the msvs tool
    env['MSVC_VERSION'] = version
    env['MSVS_VERSION'] = version
    env['MSVS'] = {}

    msvc_action, use_script, use_settings = _msvc_action(env)
    if msvc_action == MSVC_ACTION_SCRIPT:
        use_script = use_script.strip()
        if not os.path.exists(use_script):
            error_msg = f'Script specified by MSVC_USE_SCRIPT not found: {use_script!r}'
            debug(error_msg)
            raise MSVCScriptNotFound(error_msg)
        args = env.subst('$MSVC_USE_SCRIPT_ARGS')
        debug('use_script 1 %s %s', repr(use_script), repr(args))
        d = script_env(env, use_script, args)
    elif msvc_action == MSVC_ACTION_SELECT:
        d = msvc_find_valid_batch_script(env, version)
        debug('use_script 2 %s', d)
        if not d:
            return d
    elif msvc_action == MSVC_ACTION_SETTINGS:
        if not SCons.Util.is_Dict(use_settings):
            error_msg = f'MSVC_USE_SETTINGS type error: expected a dictionary, found {type(use_settings).__name__}'
            debug(error_msg)
            raise MSVCUseSettingsError(error_msg)
        d = use_settings
        debug('use_settings %s', d)
    elif msvc_action == MSVC_ACTION_BYPASS:
        debug('MSVC_USE_SCRIPT set to False')
        warn_msg = "MSVC_USE_SCRIPT set to False, assuming environment set correctly."
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None
    else:
        action = msvc_action.action if msvc_action else None
        errmsg = f'unhandled msvc_action ({action!r})'
        debug('MSVCInternalError: %s', errmsg)
        raise MSVCInternalError(errmsg)

    found_cl_path = None
    found_cl_envpath = None

    seen_path = False
    for k, v in d.items():
        if not seen_path and k.upper() == 'PATH':
            seen_path = True
            found_cl_path = SCons.Util.WhereIs('cl', v)
            found_cl_envpath = SCons.Util.WhereIs('cl', env['ENV'].get(k, []))
        env.PrependENVPath(k, v, delete_existing=True)
        debug("env['ENV']['%s'] = %s", k, env['ENV'][k])

    debug("cl paths: d['PATH']=%s, ENV['PATH']=%s", repr(found_cl_path), repr(found_cl_envpath))

    # final check to issue a warning if the requested compiler is not present
    if not found_cl_path:
        if CONFIG_CACHE:
            propose = f"SCONS_CACHE_MSVC_CONFIG caching enabled, remove cache file {CONFIG_CACHE} if out of date."
        else:
            propose = "It may need to be installed separately with Visual Studio."
        warn_msg = "Could not find requested MSVC compiler 'cl'."
        if found_cl_envpath:
            warn_msg += " A 'cl' was found on the scons ENV path which may be erroneous."
        warn_msg += " %s"
        debug(warn_msg, propose)
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg % propose)

def msvc_exists(env=None, version=None):
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

        # Intent is to use msvc tools:
        #     MSVC_VERSION:         defined and evaluates True
        #     MSVS_VERSION:         defined and evaluates True
        #     MSVC_USE_SCRIPT:      defined and (is string or evaluates False)
        #     MSVC_USE_SETTINGS:    defined and is not None

        # defined and is True
        for key in ['MSVC_VERSION', 'MSVS_VERSION']:
            if key in env and env[key]:
                rval = True
                debug('key=%s, return=%s', repr(key), rval)
                return rval

        # defined and (is string or is False)
        for key in ['MSVC_USE_SCRIPT']:
            if key in env and (SCons.Util.is_String(env[key]) or not env[key]):
                rval = True
                debug('key=%s, return=%s', repr(key), rval)
                return rval

        # defined and is not None
        for key in ['MSVC_USE_SETTINGS']:
            if key in env and env[key] is not None:
                rval = True
                debug('key=%s, return=%s', repr(key), rval)
                return rval

    debug('return=%s', rval)
    return rval

def msvc_setup_env_tool(env=None, version=None, tool=None):
    MSVC.SetupEnvDefault.register_tool(env, tool, msvc_exists)
    rval = False
    if not rval and msvc_exists(env, version):
        rval = True
    if not rval and msvc_setup_env_user(env):
        rval = True
    return rval

def msvc_sdk_versions(version=None, msvc_uwp_app: bool=False):
    debug('version=%s, msvc_uwp_app=%s', repr(version), repr(msvc_uwp_app))

    rval = []

    if not version:
        version = msvc_default_version()

    if not version:
        debug('no msvc versions detected')
        return rval

    version_def = MSVC.Util.msvc_extended_version_components(version)
    if not version_def:
        msg = f'Unsupported version {version!r}'
        raise MSVCArgumentError(msg)

    rval = MSVC.WinSDK.get_msvc_sdk_version_list(version, msvc_uwp_app)
    return rval

def msvc_toolset_versions(msvc_version=None, full: bool=True, sxs: bool=False):
    debug('msvc_version=%s, full=%s, sxs=%s', repr(msvc_version), repr(full), repr(sxs))

    rval = []

    if not msvc_version:
        msvc_version = msvc_default_version()

    if not msvc_version:
        debug('no msvc versions detected')
        return rval

    if msvc_version not in _VCVER:
        msg = f'Unsupported msvc version {msvc_version!r}'
        raise MSVCArgumentError(msg)

    msvc_instance = find_msvc_instance(msvc_version)
    if not msvc_instance:
        debug('MSVC instance not found for version %s', repr(msvc_version))
        return rval

    rval = MSVC.ScriptArguments._msvc_toolset_versions_internal(msvc_instance, full=full, sxs=sxs)
    return rval

def msvc_toolset_versions_spectre(msvc_version=None):
    debug('msvc_version=%s', repr(msvc_version))

    rval = []

    if not msvc_version:
        msvc_version = msvc_default_version()

    if not msvc_version:
        debug('no msvc versions detected')
        return rval

    if msvc_version not in _VCVER:
        msg = f'Unsupported msvc version {msvc_version!r}'
        raise MSVCArgumentError(msg)

    msvc_instance = find_msvc_instance(msvc_version)
    if not msvc_instance:
        debug('MSVC instance not found for version %s', repr(msvc_version))
        return rval

    rval = MSVC.ScriptArguments._msvc_toolset_versions_spectre_internal(msvc_instance)
    return rval

def msvc_query_version_toolset(version=None, prefer_newest: bool=True):
    """
    Returns an msvc version and a toolset version given a version
    specification.

    This is an EXPERIMENTAL proxy for using a toolset version to perform
    msvc instance selection.  This function will be removed when
    toolset version is taken into account during msvc instance selection.

    Search for an installed Visual Studio instance that supports the
    specified version.

    When the specified version contains a component suffix (e.g., Exp),
    the msvc version is returned and the toolset version is None. No
    search if performed.

    When the specified version does not contain a component suffix, the
    version is treated as a toolset version specification. A search is
    performed for the first msvc instance that contains the toolset
    version.

    Only Visual Studio 2017 and later support toolset arguments.  For
    Visual Studio 2015 and earlier, the msvc version is returned and
    the toolset version is None.

    Args:

        version: str
            The version specification may be an msvc version or a toolset
            version.

        prefer_newest: bool
            True:  prefer newer Visual Studio instances.
            False: prefer the "native" Visual Studio instance first. If
                   the native Visual Studio instance is not detected, prefer
                   newer Visual Studio instances.

    Returns:
        tuple: A tuple containing the msvc version and the msvc toolset version.
               The msvc toolset version may be None.

    Raises:
        MSVCToolsetVersionNotFound: when the specified version is not found.
        MSVCArgumentError: when argument validation fails.
    """
    debug('version=%s, prefer_newest=%s', repr(version), repr(prefer_newest))

    msvc_version = None
    msvc_toolset_version = None

    if not version:
        version = msvc_default_version()

    if not version:
        debug('no msvc versions detected')
        return msvc_version, msvc_toolset_version

    version_def = MSVC.Util.msvc_extended_version_components(version)

    if not version_def:
        msg = f'Unsupported msvc version {version!r}'
        raise MSVCArgumentError(msg)

    if version_def.msvc_suffix:
        if version_def.msvc_verstr != version_def.msvc_toolset_version:
            # toolset version with component suffix
            msg = f'Unsupported toolset version {version!r}'
            raise MSVCArgumentError(msg)

    if version_def.msvc_vernum > 14.0:
        # VS2017 and later
        force_toolset_msvc_version = False
    else:
        # VS2015 and earlier
        force_toolset_msvc_version = True
        extended_version = version_def.msvc_verstr + '0.00000'
        if not extended_version.startswith(version_def.msvc_toolset_version):
            # toolset not equivalent to msvc version
            msg = 'Unsupported toolset version {} (expected {})'.format(
                repr(version), repr(extended_version)
            )
            raise MSVCArgumentError(msg)

    msvc_version = version_def.msvc_version

    if msvc_version not in MSVC.Config.MSVC_VERSION_TOOLSET_SEARCH_MAP:
        # VS2013 and earlier
        debug(
            'ignore: msvc_version=%s, msvc_toolset_version=%s',
            repr(msvc_version), repr(msvc_toolset_version)
        )
        return msvc_version, msvc_toolset_version

    if force_toolset_msvc_version:
        query_msvc_toolset_version = version_def.msvc_verstr
    else:
        query_msvc_toolset_version = version_def.msvc_toolset_version

    if prefer_newest:
        query_version_list = MSVC.Config.MSVC_VERSION_TOOLSET_SEARCH_MAP[msvc_version]
    else:
        query_version_list = MSVC.Config.MSVC_VERSION_TOOLSET_DEFAULTS_MAP[msvc_version] + \
                             MSVC.Config.MSVC_VERSION_TOOLSET_SEARCH_MAP[msvc_version]

    seen_msvc_version = set()
    for query_msvc_version in query_version_list:

        if query_msvc_version in seen_msvc_version:
            continue
        seen_msvc_version.add(query_msvc_version)

        query_msvc_instance = find_msvc_instance(query_msvc_version)
        if not query_msvc_instance:
            continue

        if query_msvc_version.startswith('14.0'):
            # VS2015 does not support toolset version argument
            msvc_toolset_version = None
            debug(
                'found: msvc_version=%s, msvc_toolset_version=%s',
                repr(query_msvc_version), repr(msvc_toolset_version)
            )
            return query_msvc_version, msvc_toolset_version

        try:
            toolset_vcvars = MSVC.ScriptArguments._msvc_toolset_internal(query_msvc_instance, query_msvc_toolset_version)
            if toolset_vcvars:
                msvc_toolset_version = toolset_vcvars
                debug(
                    'found: msvc_version=%s, msvc_toolset_version=%s',
                    repr(query_msvc_version), repr(msvc_toolset_version)
                )
                return query_msvc_version, msvc_toolset_version

        except MSVCToolsetVersionNotFound:
            pass

    msvc_toolset_version = query_msvc_toolset_version

    debug(
        'not found: msvc_version=%s, msvc_toolset_version=%s',
        repr(msvc_version), repr(msvc_toolset_version)
    )

    if version_def.msvc_verstr == msvc_toolset_version:
        msg = f'MSVC version {version!r} was not found'
        MSVC.Policy.msvc_notfound_handler(None, msg)
        return msvc_version, msvc_toolset_version

    msg = f'MSVC toolset version {version!r} not found'
    raise MSVCToolsetVersionNotFound(msg)


# internal consistency check (should be last)
MSVC._verify()

