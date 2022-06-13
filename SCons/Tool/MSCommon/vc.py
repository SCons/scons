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

class MSVCArgumentError(VisualCException):
    pass

class BatchFileExecutionWarning(SCons.Warnings.WarningOnByDefault):
    pass


class _Const:

    MSVC_RUNTIME_DEFINITION = namedtuple('MSVCRuntime', [
        'vc_runtime',
        'vc_runtime_numeric',
        'vc_runtime_alias_list',
        'vc_runtime_vsdef_list',
    ])

    MSVC_RUNTIME_DEFINITION_LIST = []

    MSVC_RUNTIME_INTERNAL = {}
    MSVC_RUNTIME_EXTERNAL = {}

    for vc_runtime, vc_runtime_numeric, vc_runtime_alias_list in [
        ('140', 140, ['ucrt']),
        ('120', 120, ['msvcr120']),
        ('110', 110, ['msvcr110']),
        ('100', 100, ['msvcr100']),
        ( '90',  90, ['msvcr90']),
        ( '80',  80, ['msvcr80']),
        ( '71',  71, ['msvcr71']),
        ( '70',  70, ['msvcr70']),
        ( '60',  60, ['msvcrt']),
    ]:
        vc_runtime_def = MSVC_RUNTIME_DEFINITION(
            vc_runtime = vc_runtime,
            vc_runtime_numeric = vc_runtime_numeric,
            vc_runtime_alias_list = vc_runtime_alias_list,
            vc_runtime_vsdef_list = [],
        )

        MSVC_RUNTIME_DEFINITION_LIST.append(vc_runtime_def)

        MSVC_RUNTIME_INTERNAL[vc_runtime] = vc_runtime_def
        MSVC_RUNTIME_EXTERNAL[vc_runtime] = vc_runtime_def

        for vc_runtime_alias in vc_runtime_alias_list:
            MSVC_RUNTIME_EXTERNAL[vc_runtime_alias] = vc_runtime_def

    MSVC_BUILDTOOLS_DEFINITION = namedtuple('MSVCBuildtools', [
        'vc_buildtools',
        'vc_buildtools_numeric',
        'vc_version',
        'vc_version_numeric',
        'cl_version',
        'cl_version_numeric',
        'vc_runtime_def',
    ])

    MSVC_BUILDTOOLS_DEFINITION_LIST = []

    MSVC_BUILDTOOLS_INTERNAL = {}
    MSVC_BUILDTOOLS_EXTERNAL = {}

    VC_VERSION_MAP = {}

    for vc_buildtools, vc_version, cl_version, vc_runtime in [
        ('v143', '14.3', '19.3', '140'),
        ('v142', '14.2', '19.2', '140'),
        ('v141', '14.1', '19.1', '140'),
        ('v140', '14.0', '19.0', '140'),
        ('v120', '12.0', '18.0', '120'),
        ('v110', '11.0', '17.0', '110'),
        ('v100', '10.0', '16.0', '100'),
        ( 'v90',  '9.0', '15.0',  '90'),
        ( 'v80',  '8.0', '14.0',  '80'),
        ( 'v71',  '7.1', '13.1',  '71'),
        ( 'v70',  '7.0', '13.0',  '70'),
        ( 'v60',  '6.0', '12.0',  '60'),
    ]:

        vc_runtime_def = MSVC_RUNTIME_INTERNAL[vc_runtime]

        vc_buildtools_def = MSVC_BUILDTOOLS_DEFINITION(
            vc_buildtools = vc_buildtools,
            vc_buildtools_numeric = int(vc_buildtools[1:]),
            vc_version = vc_version,
            vc_version_numeric = float(vc_version),
            cl_version = cl_version,
            cl_version_numeric = float(cl_version),
            vc_runtime_def = vc_runtime_def,
        )

        MSVC_BUILDTOOLS_DEFINITION_LIST.append(vc_buildtools_def)

        MSVC_BUILDTOOLS_INTERNAL[vc_buildtools] = vc_buildtools_def
        MSVC_BUILDTOOLS_EXTERNAL[vc_buildtools] = vc_buildtools_def
        MSVC_BUILDTOOLS_EXTERNAL[vc_version] = vc_buildtools_def

        VC_VERSION_MAP[vc_version] = vc_buildtools_def

    MSVS_VERSION_INTERNAL = {}
    MSVS_VERSION_EXTERNAL = {}

    MSVC_VERSION_INTERNAL = {}
    MSVC_VERSION_EXTERNAL = {}

    MSVS_VERSION_MAJOR_MAP = {}

    CL_VERSION_MAP = {}

    VISUALSTUDIO_DEFINITION = namedtuple('VisualStudioDefinition', [
        'vs_product',
        'vs_product_alias_list',
        'vs_version',
        'vs_version_major',
        'vs_envvar',
        'vs_express',
        'vs_lookup',
        'vc_sdk_versions',
        'vc_ucrt_versions',
        'vc_uwp',
        'vc_buildtools_def',
        'vc_buildtools_all',
    ])

    VISUALSTUDIO_DEFINITION_LIST = []

    VS_PRODUCT_ALIAS = {
        '1998': ['6']
    }

    # vs_envvar: VisualStudioVersion defined in environment for MSVS 2012 and later
    #            MSVS 2010 and earlier cl_version -> vs_def is a 1:1 mapping
    # SDK attached to product or buildtools?
    for vs_product, vs_version, vs_envvar, vs_express, vs_lookup, vc_sdk, vc_ucrt, vc_uwp, vc_buildtools_all in [
        ('2022', '17.0', True,  False, 'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v143', 'v142', 'v141', 'v140']),
        ('2019', '16.0', True,  False, 'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v142', 'v141', 'v140']),
        ('2017', '15.0', True,  True,  'vswhere' , ['10.0', '8.1'], ['10'],   'uwp', ['v141', 'v140']),
        ('2015', '14.0', True,  True,  'registry', ['10.0', '8.1'], ['10'], 'store', ['v140']),
        ('2013', '12.0', True,  True,  'registry',            None,   None,    None, ['v120']),
        ('2012', '11.0', True,  True,  'registry',            None,   None,    None, ['v110']),
        ('2010', '10.0', False, True,  'registry',            None,   None,    None, ['v100']),
        ('2008',  '9.0', False, True,  'registry',            None,   None,    None, [ 'v90']),
        ('2005',  '8.0', False, True,  'registry',            None,   None,    None, [ 'v80']),
        ('2003',  '7.1', False, False, 'registry',            None,   None,    None, [ 'v71']),
        ('2002',  '7.0', False, False, 'registry',            None,   None,    None, [ 'v70']),
        ('1998',  '6.0', False, False, 'registry',            None,   None,    None, [ 'v60']),
    ]:

        vs_version_major = vs_version.split('.')[0]

        vc_buildtools_def = MSVC_BUILDTOOLS_INTERNAL[vc_buildtools_all[0]]

        vs_def = VISUALSTUDIO_DEFINITION(
            vs_product = vs_product,
            vs_product_alias_list = [],
            vs_version = vs_version,
            vs_version_major = vs_version_major,
            vs_envvar = vs_envvar,
            vs_express = vs_express,
            vs_lookup = vs_lookup,
            vc_sdk_versions = vc_sdk,
            vc_ucrt_versions = vc_ucrt,
            vc_uwp = vc_uwp,
            vc_buildtools_def = vc_buildtools_def,
            vc_buildtools_all = vc_buildtools_all,
        )

        VISUALSTUDIO_DEFINITION_LIST.append(vs_def)

        vc_buildtools_def.vc_runtime_def.vc_runtime_vsdef_list.append(vs_def)

        MSVS_VERSION_INTERNAL[vs_product] = vs_def
        MSVS_VERSION_EXTERNAL[vs_product] = vs_def
        MSVS_VERSION_EXTERNAL[vs_version] = vs_def

        MSVC_VERSION_INTERNAL[vc_buildtools_def.vc_version] = vs_def
        MSVC_VERSION_EXTERNAL[vs_product] = vs_def
        MSVC_VERSION_EXTERNAL[vc_buildtools_def.vc_version] = vs_def
        MSVC_VERSION_EXTERNAL[vc_buildtools_def.vc_buildtools] = vs_def

        if vs_product in VS_PRODUCT_ALIAS:
            for vs_product_alias in VS_PRODUCT_ALIAS[vs_product]:
                vs_def.vs_product_alias_list.append(vs_product_alias)
                MSVS_VERSION_EXTERNAL[vs_product_alias] = vs_def
                MSVC_VERSION_EXTERNAL[vs_product_alias] = vs_def

        MSVS_VERSION_MAJOR_MAP[vs_version_major] = vs_def

        CL_VERSION_MAP[vc_buildtools_def.cl_version] = vs_def

    MSVS_VERSION_LEGACY = {}
    MSVC_VERSION_LEGACY = {}

    for vdict in (MSVS_VERSION_EXTERNAL, MSVC_VERSION_INTERNAL):
        for key, vs_def in vdict.items():
            if key not in MSVS_VERSION_LEGACY:
                MSVS_VERSION_LEGACY[key] = vs_def
                MSVC_VERSION_LEGACY[key] = vs_def

# MSVC_NOTFOUND_POLICY definition:
#     error:   raise exception
#     warning: issue warning and continue
#     ignore:  continue

_MSVC_NOTFOUND_POLICY_DEFINITION = namedtuple('MSVCNotFoundPolicyDefinition', [
    'value',
    'symbol',
])

_MSVC_NOTFOUND_POLICY_INTERNAL = {}
_MSVC_NOTFOUND_POLICY_EXTERNAL = {}

for policy_value, policy_symbol_list in [
    (True,  ['Error',   'Exception']),
    (False, ['Warning', 'Warn']),
    (None,  ['Ignore',  'Suppress']),
]:

    policy_symbol = policy_symbol_list[0].lower()
    policy_def = _MSVC_NOTFOUND_POLICY_DEFINITION(policy_value, policy_symbol)

    _MSVC_NOTFOUND_POLICY_INTERNAL[policy_symbol] = policy_def

    for policy_symbol in policy_symbol_list:
        _MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol.lower()] = policy_def
        _MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol] = policy_def
        _MSVC_NOTFOUND_POLICY_EXTERNAL[policy_symbol.upper()] = policy_def

_MSVC_NOTFOUND_POLICY_DEF = _MSVC_NOTFOUND_POLICY_INTERNAL['warning']

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
    vcdir = None

    if vernum > 14:
        # 14.1 (VS2017) and later
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        batfile, _ = _GE2017_HOST_TARGET_BATCHFILE_CLPATHCOMPS[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, batfile)
        vcdir = pdir
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
                return (batfilename, arg, vcdir, sdk_bat_file_path)

    return (batfilename, arg, vcdir, None)

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
    _MSVCScriptArguments.reset()

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
        cache_data = common.parse_output(stdout)

        olines = stdout.splitlines()
        #debug(olines)

        # process stdout: batch file errors (not necessarily first line)
        script_errlog = []
        for line in olines:
            if re_script_output_error.match(line):
                if not script_errlog:
                    script_errlog.append('vc script errors detected:')
                script_errlog.append(line)

        if script_errlog:
            script_errmsg = '\n'.join(script_errlog)
            have_cl = False
            if cache_data and 'PATH' in cache_data:
                for p in cache_data['PATH']:
                    if os.path.exists(os.path.join(p, _CL_EXE_NAME)):
                        have_cl = True
                        break
            if not have_cl:
                # detected errors, cl.exe not on path
                raise BatchFileExecutionError(script_errmsg)
            else:
                # detected errors, cl.exe on path
                debug('script=%s args=%s errors=%s', repr(script), repr(args), script_errmsg)
                # This may be a bad idea (scons environment != vs cmdline environment)
                SCons.Warnings.warn(BatchFileExecutionWarning, script_errmsg)
                # TODO: errlog/errstr should be added to cache and warning moved to call site

        # once we updated cache, give a chance to write out if user wanted
        script_env_cache[cache_key] = cache_data
        common.write_script_env_cache(script_env_cache)

    return cache_data

def _msvc_notfound_policy_lookup(symbol):

    try:
        notfound_policy_def = _MSVC_NOTFOUND_POLICY_EXTERNAL[symbol]
    except KeyError:
        err_msg = "Value specified for MSVC_NOTFOUND_POLICY is not supported: {}.\n" \
                  "  Valid values are: {}".format(
                     repr(symbol),
                     ', '.join([repr(s) for s in _MSVC_NOTFOUND_POLICY_EXTERNAL.keys()])
                  )
        raise ValueError(err_msg)

    return notfound_policy_def

def set_msvc_notfound_policy(MSVC_NOTFOUND_POLICY=None):
    """ Set the default policy when MSVC is not found.

    Args:
        MSVC_NOTFOUND_POLICY:
           string representing the policy behavior
           when MSVC is not found or None

    Returns:
        The previous policy is returned when the MSVC_NOTFOUND_POLICY argument
        is not None. The active policy is returned when the MSVC_NOTFOUND_POLICY
        argument is None.

    """
    global _MSVC_NOTFOUND_POLICY_DEF

    prev_policy = _MSVC_NOTFOUND_POLICY_DEF.symbol

    policy = MSVC_NOTFOUND_POLICY
    if policy is not None:
        _MSVC_NOTFOUND_POLICY_DEF = _msvc_notfound_policy_lookup(policy)

    debug(
        'prev_policy=%s, set_policy=%s, policy.symbol=%s, policy.value=%s',
        repr(prev_policy), repr(policy),
        repr(_MSVC_NOTFOUND_POLICY_DEF.symbol), repr(_MSVC_NOTFOUND_POLICY_DEF.value)
    )

    return prev_policy

def get_msvc_notfound_policy():
    """Return the active policy when MSVC is not found."""
    debug(
        'policy.symbol=%s, policy.value=%s',
        repr(_MSVC_NOTFOUND_POLICY_DEF.symbol), repr(_MSVC_NOTFOUND_POLICY_DEF.value)
    )
    return _MSVC_NOTFOUND_POLICY_DEF.symbol

def _msvc_notfound_policy_handler(env, msg):

    if env and 'MSVC_NOTFOUND_POLICY' in env:
        # environment setting
        notfound_policy_src = 'environment'
        policy = env['MSVC_NOTFOUND_POLICY']
        if policy is not None:
            # user policy request
            notfound_policy_def = _msvc_notfound_policy_lookup(policy)
        else:
            # active global setting
            notfound_policy_def = _MSVC_NOTFOUND_POLICY_DEF
    else:
        # active global setting
        notfound_policy_src = 'default'
        policy = None
        notfound_policy_def = _MSVC_NOTFOUND_POLICY_DEF

    debug(
        'source=%s, set_policy=%s, policy.symbol=%s, policy.value=%s',
        notfound_policy_src, repr(policy), repr(notfound_policy_def.symbol), repr(notfound_policy_def.value)
    )

    if notfound_policy_def.value is None:
        # ignore
        pass
    elif notfound_policy_def.value:
        raise MSVCVersionNotFound(msg)
    else:
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)

class _MSVCSetupEnvDefault:
    """
    Determine if and/or when an error/warning should be issued when there
    are no versions of msvc installed.  If there is at least one version of
    msvc installed, these routines do (almost) nothing.

    Notes:
        * When msvc is the default compiler because there are no compilers
          installed, a build may fail due to the cl.exe command not being
          recognized.  Currently, there is no easy way to detect during
          msvc initialization if the default environment will be used later
          to build a program and/or library. There is no error/warning
          as there are legitimate SCons uses that do not require a c compiler.
        * As implemented, the default is that a warning is issued.  This can
          be changed globally via the function set_msvc_notfound_policy and/or
          through the environment via the MSVC_NOTFOUND_POLICY variable.
    """

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

class _MSVCScriptArguments:

    # MSVC batch file arguments:
    #
    #     VS2022: UWP, SDK, TOOLSET, SPECTRE
    #     VS2019: UWP, SDK, TOOLSET, SPECTRE
    #     VS2017: UWP, SDK, TOOLSET, SPECTRE
    #     VS2015: UWP, SDK
    #
    #     MSVC_UWP_APP:         VS2015+
    #     MSVC_SDK_VERSION:     VS2015+
    #     MSVC_TOOLSET_VERSION: VS2017+
    #     MSVC_SPECTRE_LIBS:    VS2017+
    #
    #     MSVC_SCRIPT_ARGS:     VS2015+
    #

    # Force -vcvars_ver argument for default toolset
    MSVC_TOOLSET_DEFAULT_VCVARSVER = False

    VS2019 = _Const.MSVS_VERSION_INTERNAL['2019']
    VS2017 = _Const.MSVS_VERSION_INTERNAL['2017']
    VS2015 = _Const.MSVS_VERSION_INTERNAL['2015']

    MSVC_VERSION_ARGS_DEFINITION = namedtuple('MSVCVersionArgsDefinition', [
        'version',
        'vs_def',
    ])

    @classmethod
    def _msvc_version(cls, version):
        verstr = get_msvc_version_numeric(version)
        vs_def = _Const.MSVC_VERSION_INTERNAL[verstr]
        msvc_req = cls.MSVC_VERSION_ARGS_DEFINITION(
            version = version,
            vs_def = vs_def,
        )
        return msvc_req

    @classmethod
    def _msvc_script_argument_uwp(cls, env, msvc, arglist):

        uwp_app = env['MSVC_UWP_APP']
        debug('MSVC_VERSION=%s, MSVC_UWP_APP=%s', repr(msvc.version), repr(uwp_app))

        if not uwp_app:
            return False

        if uwp_app not in (True, '1'):
            return False

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2015.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: msvc version constraint: %s < %s VS2015',
                repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
                repr(cls.VS2015.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_UWP_APP ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
                repr(uwp_app), repr(msvc.version), repr(cls.VS2015.vc_buildtools_def.vc_version)
            )
            raise MSVCArgumentError(err_msg)

        # uwp may not be installed
        uwp_arg = msvc.vs_def.vc_uwp
        arglist.append(uwp_arg)
        return True

    # TODO: verify SDK 10 version folder names 10.0.XXXXX.0 {1,3} last?
    re_sdk_version_10 = re.compile(r'^10[.][0-9][.][0-9]{5}[.][0-9]{1}$')

    @classmethod
    def _msvc_script_argument_sdk_constraints(cls, msvc, sdk_version):

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2015.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: msvc_version constraint: %s < %s VS2015',
                repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
                repr(cls.VS2015.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_SDK_VERSION ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
                repr(sdk_version), repr(msvc.version), repr(cls.VS2015.vc_buildtools_def.vc_version)
            )
            return err_msg

        # TODO: check sdk against vs_def/vc_buildtools_def

        if sdk_version == '8.1':
            debug('valid: sdk_version=%s', repr(sdk_version))
            return None

        if cls.re_sdk_version_10.match(sdk_version):
            debug('valid: sdk_version=%s', repr(sdk_version))
            return None

        debug('invalid: method exit: sdk_version=%s', repr(sdk_version))
        err_msg = "MSVC_SDK_VERSION ({}) is not supported".format(repr(sdk_version))
        return err_msg

    @classmethod
    def _msvc_script_argument_sdk(cls, env, msvc, is_uwp, arglist):

        sdk_version = env['MSVC_SDK_VERSION']
        debug(
            'MSVC_VERSION=%s, MSVC_SDK_VERSION=%s, uwp=%s',
            repr(msvc.version), repr(sdk_version), repr(is_uwp)
        )

        if not sdk_version:
            return False

        err_msg = cls._msvc_script_argument_sdk_constraints(msvc, sdk_version)
        if err_msg:
            raise MSVCArgumentError(err_msg)

        # sdk folder may not exist
        arglist.append(sdk_version)
        return True

    @classmethod
    def _msvc_read_toolset_file(cls, msvc, filename):
        toolset_version = None
        try:
            with open(filename) as f:
                toolset_version = f.readlines()[0].strip()
            debug(
                'msvc_version=%s, filename=%s, toolset_version=%s',
                repr(msvc.version), repr(filename), repr(toolset_version)
            )
        except IOError:
            debug('IOError: msvc_version=%s, filename=%s', repr(msvc.version), repr(filename))
        except IndexError:
            debug('IndexError: msvc_version=%s, filename=%s', repr(msvc.version), repr(filename))
        return toolset_version

    @classmethod
    def _msvc_read_toolset_folders(cls, msvc, vc_dir):

        toolsets_sxs = {}
        toolsets_full = []

        build_dir = os.path.join(vc_dir, "Auxiliary", "Build")
        sxs_toolsets = [f.name for f in os.scandir(build_dir) if f.is_dir()]
        for sxs_toolset in sxs_toolsets:
            filename = 'Microsoft.VCToolsVersion.{}.txt'.format(sxs_toolset)
            filepath = os.path.join(build_dir, sxs_toolset, filename)
            if os.path.exists(filepath):
                toolset_version = cls._msvc_read_toolset_file(msvc, filepath)
                if not toolset_version:
                    continue
                toolsets_sxs[sxs_toolset] = toolset_version
                debug(
                    'sxs toolset: msvc_version=%s, sxs_version=%s, toolset_version=%s',
                    repr(msvc.version), repr(sxs_toolset), toolset_version
                )

        toolset_dir = os.path.join(vc_dir, "Tools", "MSVC")
        toolsets = [f.name for f in os.scandir(toolset_dir) if f.is_dir()]
        for toolset_version in toolsets:
            binpath = os.path.join(toolset_dir, toolset_version, "bin")
            if os.path.exists(binpath):
                toolsets_full.append(toolset_version)
                debug(
                    'toolset: msvc_version=%s, toolset_version=%s',
                    repr(msvc.version), repr(toolset_version)
                )

        toolsets_full.sort(reverse=True)
        debug('msvc_version=%s, toolsets=%s', repr(msvc.version), repr(toolsets_full))

        return toolsets_sxs, toolsets_full

    @classmethod
    def _msvc_read_toolset_default(cls, msvc, vc_dir):

        build_dir = os.path.join(vc_dir, "Auxiliary", "Build")

        # VS2019+
        filename = "Microsoft.VCToolsVersion.{}.default.txt".format(msvc.vs_def.vc_buildtools_def.vc_buildtools)
        filepath = os.path.join(build_dir, filename)

        toolset_buildtools = None
        if os.path.exists(filepath):
            toolset_buildtools = cls._msvc_read_toolset_file(msvc, filepath)
            if toolset_buildtools:
                return toolset_buildtools

        # VS2017+
        filename = "Microsoft.VCToolsVersion.default.txt"
        filepath = os.path.join(build_dir, filename)

        toolset_default = None
        if os.path.exists(filepath):
            toolset_default = cls._msvc_read_toolset_file(msvc, filepath)
            if toolset_default:
                return toolset_default

        return None

    @classmethod
    def _reset_toolsets(cls):
        debug('reset: toolset cache')
        cls._toolset_version_cache = {}
        cls._toolset_default_cache = {}

    _toolset_version_cache = {}
    _toolset_default_cache = {}

    @classmethod
    def _msvc_version_toolsets(cls, msvc, vc_dir):

        if msvc.version in cls._toolset_version_cache:
            toolsets_sxs, toolsets_full = cls._toolset_version_cache[msvc.version]
        else:
            toolsets_sxs, toolsets_full = cls._msvc_read_toolset_folders(msvc, vc_dir)
            cls._toolset_version_cache[msvc.version] = toolsets_sxs, toolsets_full

        return toolsets_sxs, toolsets_full

    @classmethod
    def _msvc_default_toolset(cls, msvc, vc_dir):

        if msvc.version in cls._toolset_default_cache:
            toolset_default = cls._toolset_default_cache[msvc.version]
        else:
            toolset_default = cls._msvc_read_toolset_default(msvc, vc_dir)
            cls._toolset_default_cache[msvc.version] = toolset_default

        return toolset_default

    @classmethod
    def _msvc_version_toolset_vcvars(cls, msvc, vc_dir, toolset_version):

        if toolset_version == '14.0':
            return toolset_version

        toolsets_sxs, toolsets_full = cls._msvc_version_toolsets(msvc, vc_dir)

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric == cls.VS2019.vc_buildtools_def.vc_version_numeric:
            if toolset_version == '14.28.16.8':
                new_toolset_version = '14.28'
                # VS2019\Common7\Tools\vsdevcmd\ext\vcvars.bat AzDO Bug#1293526
                #     special handling of the 16.8 SxS toolset, use VC\Auxiliary\Build\14.28 directory and SxS files
                #     if SxS version 14.28 not present/installed, fallback selection of toolset VC\Tools\MSVC\14.28.nnnnn.
                debug(
                    'rewrite toolset_version=%s => toolset_version=%s',
                    repr(toolset_version), repr(new_toolset_version)
                )
                toolset_version = new_toolset_version

        if toolset_version in toolsets_sxs:
            toolset_vcvars = toolsets_sxs[toolset_version]
            return toolset_vcvars

        for toolset_full in toolsets_full:
            if toolset_full.startswith(toolset_version):
                toolset_vcvars = toolset_full
                return toolset_vcvars

        return None

    # capture msvc version
    re_toolset_version = re.compile(r'^(?P<version>[1-9][0-9]?[.][0-9])[0-9.]*$', re.IGNORECASE)

    re_toolset_full = re.compile(r'''^(?:
        (?:[1-9][0-9][.][0-9]{1,2})|           # XX.Y    - XX.YY
        (?:[1-9][0-9][.][0-9]{2}[.][0-9]{1,5}) # XX.YY.Z - XX.YY.ZZZZZ
    )$''', re.VERBOSE)

    re_toolset_140 = re.compile(r'''^(?:
        (?:14[.]0{1,2})|       # 14.0    - 14.00
        (?:14[.]0{2}[.]0{1,5}) # 14.00.0 - 14.00.00000
    )$''', re.VERBOSE)

    # valid SxS formats will be matched with re_toolset_full: match 3 '.' format
    re_toolset_sxs = re.compile(r'^[1-9][0-9][.][0-9]{2}[.][0-9]{2}[.][0-9]{1,2}$')

    @classmethod
    def _msvc_script_argument_toolset_constraints(cls, msvc, toolset_version):

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2017.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: msvc version constraint: %s < %s VS2017',
                repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
                repr(cls.VS2017.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: MSVC_VERSION {} < {} VS2017".format(
                repr(toolset_version), repr(msvc.version), repr(cls.VS2017.vc_buildtools_def.vc_version)
            )
            return err_msg

        m = cls.re_toolset_version.match(toolset_version)
        if not m:
            debug('invalid: re_toolset_version: toolset_version=%s', repr(toolset_version))
            err_msg = 'MSVC_TOOLSET_VERSION {} format is not supported'.format(
                repr(toolset_version)
            )
            return err_msg

        toolset_ver = m.group('version')
        toolset_vernum = float(toolset_ver)

        if toolset_vernum < cls.VS2015.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: toolset version constraint: %s < %s VS2015',
                repr(toolset_vernum), repr(cls.VS2015.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} < {} VS2015".format(
                repr(toolset_version), repr(toolset_ver), repr(cls.VS2015.vc_buildtools_def.vc_version)
            )
            return err_msg

        if toolset_vernum > msvc.vs_def.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: toolset version constraint: toolset %s > %s msvc',
                repr(toolset_vernum), repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} > {} MSVC_VERSION".format(
                repr(toolset_version), repr(toolset_ver), repr(msvc.version)
            )
            return err_msg

        if toolset_vernum == cls.VS2015.vc_buildtools_def.vc_version_numeric:
            # tooset = 14.0
            if cls.re_toolset_full.match(toolset_version):
                if not cls.re_toolset_140.match(toolset_version):
                    debug(
                        'invalid: toolset version 14.0 constraint: %s != 14.0',
                        repr(toolset_version)
                    )
                    err_msg = "MSVC_TOOLSET_VERSION ({}) constraint violation: toolset version {} != '14.0'".format(
                        repr(toolset_version), repr(toolset_version)
                    )
                    return err_msg
                return None

        if cls.re_toolset_full.match(toolset_version):
            debug('valid: re_toolset_full: toolset_version=%s', repr(toolset_version))
            return None

        if cls.re_toolset_sxs.match(toolset_version):
            debug('valid: re_toolset_sxs: toolset_version=%s', repr(toolset_version))
            return None

        debug('invalid: method exit: toolset_version=%s', repr(toolset_version))
        err_msg = "MSVC_TOOLSET_VERSION ({}) format is not supported".format(repr(toolset_version))
        return err_msg

    @classmethod
    def _msvc_script_argument_toolset(cls, env, msvc, vc_dir, arglist):

        toolset_version = env['MSVC_TOOLSET_VERSION']
        debug('MSVC_VERSION=%s, MSVC_TOOLSET_VERSION=%s', repr(msvc.version), repr(toolset_version))

        if not toolset_version:
            return False

        err_msg = cls._msvc_script_argument_toolset_constraints(msvc, toolset_version)
        if err_msg:
            raise MSVCArgumentError(err_msg)

        if toolset_version.startswith('14.0') and len(toolset_version) > len('14.0'):
            new_toolset_version = '14.0'
            debug(
                'rewrite toolset_version=%s => toolset_version=%s',
                repr(toolset_version), repr(new_toolset_version)
            )
            toolset_version = new_toolset_version

        toolset_vcvars = cls._msvc_version_toolset_vcvars(msvc, vc_dir, toolset_version)
        debug(
            'toolset: toolset_version=%s, toolset_vcvars=%s',
            repr(toolset_version), repr(toolset_vcvars)
        )

        if not toolset_vcvars:
            err_msg = "MSVC_TOOLSET_VERSION {} not found for MSVC_VERSION {}".format(
                repr(toolset_version), repr(msvc.version)
            )
            raise MSVCArgumentError(err_msg)

        arglist.append('-vcvars_ver={}'.format(toolset_vcvars))
        return True

    @classmethod
    def _msvc_script_default_toolset(cls, env, msvc, vc_dir, arglist):

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2017.vc_buildtools_def.vc_version_numeric:
            return False

        toolset_default = cls._msvc_default_toolset(msvc, vc_dir)
        if not toolset_default:
            return False

        debug('MSVC_VERSION=%s, toolset_default=%s', repr(msvc.version), repr(toolset_default))
        arglist.append('-vcvars_ver={}'.format(toolset_default))
        return True

    @classmethod
    def _msvc_script_argument_spectre(cls, env, msvc, arglist):

        spectre_libs = env['MSVC_SPECTRE_LIBS']
        debug('MSVC_VERSION=%s, MSVC_SPECTRE_LIBS=%s', repr(msvc.version), repr(spectre_libs))

        if not spectre_libs:
            return False

        if spectre_libs not in (True, '1'):
            return False

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2017.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: msvc version constraint: %s < %s VS2017',
                repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
                repr(cls.VS2017.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_SPECTRE_LIBS ({}) constraint violation: MSVC_VERSION {} < {} VS2017".format(
                repr(spectre_libs), repr(msvc.version), repr(cls.VS2017.vc_buildtools_def.vc_version)
            )
            raise MSVCArgumentError(err_msg)

        # spectre libs may not be installed
        arglist.append('-vcvars_spectre_libs=spectre')
        return True

    @classmethod
    def _msvc_script_argument_user(cls, env, msvc, arglist):

        # subst None -> empty string
        script_args = env.subst('$MSVC_SCRIPT_ARGS')
        debug('MSVC_VERSION=%s, MSVC_SCRIPT_ARGS=%s', repr(msvc.version), repr(script_args))

        if not script_args:
            return False

        if msvc.vs_def.vc_buildtools_def.vc_version_numeric < cls.VS2015.vc_buildtools_def.vc_version_numeric:
            debug(
                'invalid: msvc version constraint: %s < %s VS2015',
                repr(msvc.vs_def.vc_buildtools_def.vc_version_numeric),
                repr(cls.VS2015.vc_buildtools_def.vc_version_numeric)
            )
            err_msg = "MSVC_SCRIPT_ARGS ({}) constraint violation: MSVC_VERSION {} < {} VS2015".format(
                repr(script_args), repr(msvc.version), repr(cls.VS2015.vc_buildtools_def.vc_version)
            )
            raise MSVCArgumentError(err_msg)

        # user arguments are not validated
        arglist.append(script_args)
        return True

    @classmethod
    def msvc_script_arguments(cls, env, version, vc_dir, arg):

        msvc = cls._msvc_version(version)

        arglist = [arg]

        have_uwp = False
        have_toolset = False

        if 'MSVC_UWP_APP' in env:
            have_uwp = cls._msvc_script_argument_uwp(env, msvc, arglist)

        if 'MSVC_SDK_VERSION' in env:
            cls._msvc_script_argument_sdk(env, msvc, have_uwp, arglist)

        if 'MSVC_TOOLSET_VERSION' in env:
            have_toolset = cls._msvc_script_argument_toolset(env, msvc, vc_dir, arglist)

        if cls.MSVC_TOOLSET_DEFAULT_VCVARSVER and not have_toolset:
            have_toolset = cls._msvc_script_default_toolset(env, msvc, vc_dir, arglist)

        if 'MSVC_SPECTRE_LIBS' in env:
            cls._msvc_script_argument_spectre(env, msvc, arglist)

        if 'MSVC_SCRIPT_ARGS' in env:
            cls._msvc_script_argument_user(env, msvc, arglist)

        argstr = ' '.join(arglist).strip()
        debug('arguments: %s', repr(argstr))

        return argstr

    @classmethod
    def reset(cls):
        debug('reset')
        cls._reset_toolsets()

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
        arg = ''

        # Try to locate a batch file for this host/target platform combo
        try:
            (vc_script, arg, vc_dir, sdk_script) = find_batch_file(env, version, host_arch, target_arch)
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
            arg = _MSVCScriptArguments.msvc_script_arguments(env, version, vc_dir, arg)
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
        if not msvc_setup_env_user(env):
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

        # Intent is to use msvc tools:
        #     MSVC_VERSION or MSVS_VERSION: defined and is True
        #     MSVC_USE_SCRIPT:   defined and (is string or is False)
        #     MSVC_USE_SETTINGS: defined and is not None

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
    debug('tool=%s, version=%s', repr(tool), repr(version))
    _MSVCSetupEnvDefault.register_tool(env, tool)
    rval = False
    if not rval and msvc_exists(env, version):
        rval = True
    if not rval and msvc_setup_env_user(env):
        rval = True
    debug('tool=%s, version=%s, return=%s', repr(tool), repr(version), rval)
    return rval

