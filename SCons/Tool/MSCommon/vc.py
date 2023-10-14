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

import SCons.Util
import SCons.Warnings

from . import common
from .common import (
    CONFIG_CACHE,
    debug,
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
UNDEFINED = MSVC.Config.UNDEFINED

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

_GE2022_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('amd64',       'vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('amd64', 'x86')   : ('amd64_x86',   'vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('amd64', 'arm')   : ('amd64_arm',   'vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('amd64', 'arm64') : ('amd64_arm64', 'vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

    ('x86',   'amd64') : ('x86_amd64',   'vcvarsx86_amd64.bat',   ('bin', 'Hostx86', 'x64')),
    ('x86',   'x86')   : ('x86',         'vcvars32.bat',          ('bin', 'Hostx86', 'x86')),
    ('x86',   'arm')   : ('x86_arm',     'vcvarsx86_arm.bat',     ('bin', 'Hostx86', 'arm')),
    ('x86',   'arm64') : ('x86_arm64',   'vcvarsx86_arm64.bat',   ('bin', 'Hostx86', 'arm64')),

    ('arm64', 'amd64') : ('arm64_amd64', 'vcvarsarm64_amd64.bat', ('bin', 'Hostarm64', 'arm64_amd64')),
    ('arm64', 'x86')   : ('arm64_x86',   'vcvarsarm64_x86.bat',   ('bin', 'Hostarm64', 'arm64_x86')),
    ('arm64', 'arm')   : ('arm64_arm',   'vcvarsarm64_arm.bat',   ('bin', 'Hostarm64', 'arm64_arm')),
    ('arm64', 'arm64') : ('arm64',       'vcvarsarm64.bat',       ('bin', 'Hostarm64', 'arm64')),

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

_LE2019_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'amd64') : ('amd64',       'vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('amd64', 'x86')   : ('amd64_x86',   'vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('amd64', 'arm')   : ('amd64_arm',   'vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('amd64', 'arm64') : ('amd64_arm64', 'vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

    ('x86',   'amd64') : ('x86_amd64',   'vcvarsx86_amd64.bat',   ('bin', 'Hostx86', 'x64')),
    ('x86',   'x86')   : ('x86',         'vcvars32.bat',          ('bin', 'Hostx86', 'x86')),
    ('x86',   'arm')   : ('x86_arm',     'vcvarsx86_arm.bat',     ('bin', 'Hostx86', 'arm')),
    ('x86',   'arm64') : ('x86_arm64',   'vcvarsx86_arm64.bat',   ('bin', 'Hostx86', 'arm64')),

    ('arm64', 'amd64') : ('amd64',       'vcvars64.bat',          ('bin', 'Hostx64', 'x64')),
    ('arm64', 'x86')   : ('amd64_x86',   'vcvarsamd64_x86.bat',   ('bin', 'Hostx64', 'x86')),
    ('arm64', 'arm')   : ('amd64_arm',   'vcvarsamd64_arm.bat',   ('bin', 'Hostx64', 'arm')),
    ('arm64', 'arm64') : ('amd64_arm64', 'vcvarsamd64_arm64.bat', ('bin', 'Hostx64', 'arm64')),

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

_LE2003_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS = {

    ('amd64', 'x86') : ('x86', 'vcvars32.bat', ('bin', )),
    ('x86',   'x86') : ('x86', 'vcvars32.bat', ('bin', )),
    ('arm64', 'x86') : ('x86', 'vcvars32.bat', ('bin', )),

}

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
            debug(warn_msg)
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)

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

def msvc_find_vswhere(env=None):
    """ Find the location of vswhere """
    # NB: this gets called from testsuite on non-Windows platforms.
    # Whether that makes sense or not, don't break it for those.
    vswhere_env = env.subst('$VSWHERE') if env and 'VSWHERE' in env else None
    vswhere_executables = MSVC.VSWhere.vswhere_get_executables(vswhere_env)
    if vswhere_executables:
        vswhere_path = vswhere_executables[0].path
    else:
        vswhere_path = None
    debug('vswhere_path=%s', vswhere_path)
    return vswhere_path

def msvs_manager(env=None):
    vswhere_env = env.subst('$VSWHERE') if env and 'VSWHERE' in env else None
    vs_manager = MSVC.VSDetect.msvs_manager(vswhere_env)
    return vs_manager

def _find_msvc_instance(msvc_version, env=None):

    msvc_instance = None
    query_key = None

    if msvc_version not in _VCVER:
        # TODO(JCB): issue warning (add policy?)
        debug("Unknown version of MSVC: %s", repr(msvc_version))
        return msvc_instance, query_key

    vs_manager = msvs_manager(env)

    msvc_instances, query_key = vs_manager.query_msvc_instances(msvc_version=msvc_version)

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
        _, batfile, _ = _GE2022_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, batfile)
    elif 2022 > msvc_instance.vs_product_numeric >= 2017:
        # 14.2 (VS2019) to 14.1 (VS2017)
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        _, batfile, _ = _LE2019_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
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
        _, batfile, cl_path_comps = _LE2003_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(pdir, *cl_path_comps, batfile)
        clexe = os.path.join(pdir, *cl_path_comps, _CL_EXE_NAME)

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

def _reset_installed_vcs() -> None:
    global _cache_installed_msvc_versions
    global _cache_installed_msvc_instances
    _cache_installed_msvc_versions = None
    _cache_installed_msvc_instances = None
    debug('reset')

# register vcs cache reset function with vs detection
MSVC.VSDetect.register_reset_func(_reset_installed_vcs)

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
            host_target_batcharg_batchfile_clpathcomps = _GE2022_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS
        else:
            # 14.2 (VS2019) to 14.1 (VS2017)
            host_target_batcharg_batchfile_clpathcomps = _LE2019_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS

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

        host_target_batcharg_batchfile_clpathcomps = _LE2003_HOST_TARGET_BATCHARG_BATCHFILE_CLPATHCOMPS

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

    else:
        # version not supported return false
        debug('unsupported MSVC version: %s', str(msvc_instance.msvc_version))

    return False

# TODO(JCB): register callback (temporary until toolset detection is added)
MSVC.VSDetect.register_msvc_instance_check_files_exist(_msvc_instance_check_files_exist)

def get_installed_msvc_instances(env=None):
    global _cache_installed_msvc_instances

    # the installed instance cache is cleared if new instances are discovered
    vs_manager = msvs_manager(env)

    if _cache_installed_msvc_instances is not None:
        return _cache_installed_msvc_instances

    installed_msvc_instances = vs_manager.get_installed_msvc_instances()

    _cache_installed_msvc_instances = installed_msvc_instances
    # debug("installed_msvc_instances=%s", _cache_installed_msvc_versions)
    return _cache_installed_msvc_instances

def get_installed_vcs(env=None):
    global _cache_installed_msvc_versions

    # the installed version cache is cleared if new instances are discovered
    vs_manager = msvs_manager(env)

    if _cache_installed_msvc_versions is not None:
        return _cache_installed_msvc_versions

    installed_msvc_versions = vs_manager.get_installed_msvc_versions()

    _cache_installed_msvc_versions = installed_msvc_versions
    debug("installed_msvc_versions=%s", _cache_installed_msvc_versions)
    return _cache_installed_msvc_versions

def reset_installed_vcs() -> None:
    """Make it try again to find VC.  This is just for the tests."""
    _reset_installed_vcs()
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

class _MSVCAction:

    MSVCAction = namedtuple("MSVCAction", [
        'label',
    ])

    SCRIPT = MSVCAction(label='script')
    SELECT = MSVCAction(label='select')
    SETTINGS = MSVCAction(label='settings')
    BYPASS = MSVCAction(label='bypass')

def _msvc_action(env):

    #   use_script     use_settings  action    description
    #   -------------  ------------  --------  ----------------
    #  defined/None    not None      SETTINGS  use dictionary
    #  defined/None    None          BYPASS    bypass detection
    #  defined/string  ignored       SCRIPT    use script
    #  defined/false   ignored       BYPASS    bypass detection
    #  defined/true    ignored       SELECT    msvc selection
    #  undefined       not None      SETTINGS  use dictionary
    #  undefined       None          SELECT    msvc selection

    msvc_action = None

    use_script = env.get('MSVC_USE_SCRIPT', UNDEFINED)
    use_settings = env.get('MSVC_USE_SETTINGS', None)

    if use_script != UNDEFINED:
        # use script defined
        if use_script is None:
            # use script is None
            if use_settings is not None:
                # use script is None, use_settings is not None
                msvc_action = _MSVCAction.SETTINGS
            else:
                # use script is None, use_settings is None
                msvc_action = _MSVCAction.BYPASS
        else:
            # use script is not None
            if SCons.Util.is_String(use_script):
                # use_script is string, use_settings ignored
                msvc_action = _MSVCAction.SCRIPT
            elif not use_script:
                # use_script eval false, use_settings ignored
                msvc_action = _MSVCAction.BYPASS
            else:
                # use script eval true, use_settings ignored
                msvc_action = _MSVCAction.SELECT
    elif use_settings is not None:
        # use script undefined, use_settings is defined and not None
        msvc_action = _MSVCAction.SETTINGS
    else:
        # use script undefined, use_settings undefined or None
        msvc_action = _MSVCAction.SELECT

    if not msvc_action:
        errmsg = 'msvc_action is undefined'
        debug('MSVCInternalError: %s', errmsg)
        raise MSVCInternalError(errmsg)

    debug('msvc_action=%s', repr(msvc_action.label))

    return msvc_action, use_script, use_settings

def msvc_setup_env(env) -> None:
    debug('called')
    version = get_default_version(env)
    if version is None:
        if not msvc_setup_env_user(env):
            MSVC.SetupEnvDefault.set_nodefault()
        return

    # XXX: we set-up both MSVS version for backward
    # compatibility with the msvs tool
    env['MSVC_VERSION'] = version
    env['MSVS_VERSION'] = version
    env['MSVS'] = {}

    msvc_action, use_script, use_settings = _msvc_action(env)
    if msvc_action == _MSVCAction.SCRIPT:
        use_script = use_script.strip()
        if not os.path.exists(use_script):
            error_msg = f'Script specified by MSVC_USE_SCRIPT not found: {use_script!r}'
            debug(error_msg)
            raise MSVCScriptNotFound(error_msg)
        args = env.subst('$MSVC_USE_SCRIPT_ARGS')
        debug('msvc_action=%s, script=%s, args=%s', repr(msvc_action.label), repr(use_script), repr(args))
        d = script_env(env, use_script, args)
    elif msvc_action == _MSVCAction.SELECT:
        d = msvc_find_valid_batch_script(env, version)
        debug('msvc_action=%s, d=%s', repr(msvc_action.label), d)
        if not d:
            return
    elif msvc_action == _MSVCAction.SETTINGS:
        if not SCons.Util.is_Dict(use_settings):
            error_msg = f'MSVC_USE_SETTINGS type error: expected a dictionary, found {type(use_settings).__name__}'
            debug(error_msg)
            raise MSVCUseSettingsError(error_msg)
        d = use_settings
        debug('msvc_action=%s, d=%s', repr(msvc_action.label), d)
    elif msvc_action == _MSVCAction.BYPASS:
        debug('msvc_action=%s', repr(msvc_action.label))
        warn_msg = "MSVC detection bypassed, assuming environment set correctly."
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return
    else:
        label = msvc_action.label if msvc_action else None
        errmsg = f'unhandled msvc_action ({label!r})'
        debug('MSVCInternalError: %s', errmsg)
        raise MSVCInternalError(errmsg)

    found_cl_path = None
    found_cl_envpath = None

    seen_path = False
    for k, v in d.items():
        if not seen_path and k == 'PATH':
            seen_path = True
            found_cl_path = SCons.Util.WhereIs('cl', v)
            found_cl_envpath = SCons.Util.WhereIs('cl', env['ENV'].get(k, []))
        env.PrependENVPath(k, v, delete_existing=True)
        debug("env['ENV']['%s'] = %s", k, env['ENV'][k])

    debug("cl paths: d['PATH']=%s, ENV['PATH']=%s", repr(found_cl_path), repr(found_cl_envpath))

    # final check to issue a warning if the requested compiler is not present
    if not found_cl_path:
        warn_msg = "Could not find requested MSVC compiler 'cl'."
        if CONFIG_CACHE:
            warn_msg += f" SCONS_CACHE_MSVC_CONFIG caching enabled, remove cache file {CONFIG_CACHE} if out of date."
        else:
            warn_msg += " It may need to be installed separately with Visual Studio."
        if found_cl_envpath:
            warn_msg += " A 'cl' was found on the scons ENV path which may be erroneous."
        debug(warn_msg)
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)

def msvc_exists(env=None, version=None) -> bool:
    vcs = get_installed_vcs(env)
    if version is None:
        rval = len(vcs) > 0
    else:
        rval = version in vcs
    debug('version=%s, return=%s', repr(version), rval)
    return rval

def msvc_setup_env_user(env=None) -> bool:
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

def msvc_setup_env_tool(env=None, version=None, tool=None) -> bool:
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

# internal consistency checks (should be last)
MSVC._verify()

