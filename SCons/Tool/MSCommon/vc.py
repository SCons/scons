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
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__doc__ = """Module for Visual C/C++ detection and configuration.
"""

# Experimental version - specific version and product types:
#    True:  specific msvc toolset and product selection
#    False: _VCVER msvc version (master compatible)
#
_MSVC_EXPERIMENTAL_ACTIVE = True

import SCons.compat
import SCons.Util

import subprocess
import os
import platform
import sys
from string import digits as string_digits
from subprocess import PIPE

import json
import re
from collections import namedtuple

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

class MSVCProductInvalid(VisualCException):
    pass

class MSVCProductNotFound(VisualCException):
    pass

class MSVCTargetNotFound(VisualCException):
    pass

class MSVCToolsetNotFound(VisualCException):
    pass


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

# Starting with 14.1 (aka VS2017), the tools are organized by host directory.
# subdirs for each target. They are now in .../VC/Auxuiliary/Build.
# Note 2017 Express uses Hostx86 even if it's on 64-bit Windows,
# not reflected in this table.
_HOST_TARGET_TO_CL_DIR_GREATER_THAN_14 = {
    ("amd64","amd64")  : ("Hostx64","x64"),
    ("amd64","x86")    : ("Hostx64","x86"),
    ("amd64","arm")    : ("Hostx64","arm"),
    ("amd64","arm64")  : ("Hostx64","arm64"),
    ("x86","amd64")    : ("Hostx86","x64"),
    ("x86","x86")      : ("Hostx86","x86"),
    ("x86","arm")      : ("Hostx86","arm"),
    ("x86","arm64")    : ("Hostx86","arm64"),
}

# before 14.1 (VS2017): the original x86 tools are in the tools dir,
# any others are in a subdir named by the host/target pair,
# or just a single word if host==target
_HOST_TARGET_TO_CL_DIR = {
    ("amd64","amd64")  : "amd64",
    ("amd64","x86")    : "amd64_x86",
    ("amd64","arm")    : "amd64_arm",
    ("amd64","arm64")  : "amd64_arm64",
    ("x86","amd64")    : "x86_amd64",
    ("x86","x86")      : "",
    ("x86","arm")      : "x86_arm",
    ("x86","arm64")    : "x86_arm64",
    ("arm","arm")      : "arm",
}

# 14.1 (VS2017) and later:
# Given a (host, target) tuple, return the batch file to look for.
# We can't rely on returning an arg to use for vcvarsall.bat,
# because that script will run even if given a pair that isn't installed.
# Targets that already look like a pair are pseudo targets that
# effectively mean to skip whatever the host was specified as.
_HOST_TARGET_TO_BAT_ARCH_GT14 = {
    ("amd64", "amd64"): "vcvars64.bat",
    ("amd64", "x86"): "vcvarsamd64_x86.bat",
    ("amd64", "x86_amd64"): "vcvarsx86_amd64.bat",
    ("amd64", "x86_x86"): "vcvars32.bat",
    ("amd64", "arm"): "vcvarsamd64_arm.bat",
    ("amd64", "x86_arm"): "vcvarsx86_arm.bat",
    ("amd64", "arm64"): "vcvarsamd64_arm64.bat",
    ("amd64", "x86_arm64"): "vcvarsx86_arm64.bat",
    ("x86", "x86"): "vcvars32.bat",
    ("x86", "amd64"): "vcvarsx86_amd64.bat",
    ("x86", "x86_amd64"): "vcvarsx86_amd64.bat",
    ("x86", "arm"): "vcvarsx86_arm.bat",
    ("x86", "x86_arm"): "vcvarsx86_arm.bat",
    ("x86", "arm64"): "vcvarsx86_arm64.bat",
    ("x86", "x86_arm64"): "vcvarsx86_arm64.bat",
}

# before 14.1 (VS2017):
# Given a (host, target) tuple, return the argument for the bat file;
# Both host and target should be canoncalized.
# If the target already looks like a pair, return it - these are
# pseudo targets (mainly used by Express versions)
_HOST_TARGET_ARCH_TO_BAT_ARCH = {
    ("x86", "x86"): "x86",
    ("x86", "amd64"): "x86_amd64",
    ("x86", "x86_amd64"): "x86_amd64",
    ("amd64", "x86_amd64"): "x86_amd64", # This is present in (at least) VS2012 express
    ("amd64", "amd64"): "amd64",
    ("amd64", "x86"): "x86",
    ("amd64", "x86_x86"): "x86",
    ("x86", "ia64"): "x86_ia64",         # gone since 14.0
    ("x86", "arm"): "x86_arm",          # since 14.0
    ("x86", "arm64"): "x86_arm64",      # since 14.1
    ("amd64", "arm"): "amd64_arm",      # since 14.0
    ("amd64", "arm64"): "amd64_arm64",  # since 14.1
    ("x86", "x86_arm"): "x86_arm",      # since 14.0
    ("x86", "x86_arm64"): "x86_arm64",  # since 14.1
    ("amd64", "x86_arm"): "x86_arm",      # since 14.0
    ("amd64", "x86_arm64"): "x86_arm64",  # since 14.1
}

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

def get_host_target(env):
    host_platform = env.get('HOST_ARCH')
    debug("HOST_ARCH:" + str(host_platform))
    if not host_platform:
        host_platform = platform.machine()

    # Solaris returns i86pc for both 32 and 64 bit architectures
    if host_platform == "i86pc":
        if platform.architecture()[0] == "64bit":
            host_platform = "amd64"
        else:
            host_platform = "x86"

    # Retain user requested TARGET_ARCH
    req_target_platform = env.get('TARGET_ARCH')
    debug("HOST_ARCH:" + str(req_target_platform))
    if req_target_platform:
        # If user requested a specific platform then only try that one.
        target_platform = req_target_platform
    else:
        target_platform = host_platform

    try:
        host = _ARCH_TO_CANONICAL[host_platform.lower()]
    except KeyError:
        msg = "Unrecognized host architecture %s"
        raise MSVCUnsupportedHostArch(msg % repr(host_platform))

    try:
        target = _ARCH_TO_CANONICAL[target_platform.lower()]
    except KeyError:
        all_archs = str(list(_ARCH_TO_CANONICAL.keys()))
        raise MSVCUnsupportedTargetArch("Unrecognized target architecture %s\n\tValid architectures: %s" % (target_platform, all_archs))

    return (host, target,req_target_platform)

# If you update this, update SupportedVSList in Tool/MSCommon/vs.py, and the
# MSVC_VERSION documentation in Tool/msvc.xml.
_VCVER = ["14.2", "14.1", "14.1Exp", "14.0", "14.0Exp", "12.0", "12.0Exp", "11.0", "11.0Exp", "10.0", "10.0Exp", "9.0", "9.0Exp","8.0", "8.0Exp","7.1", "7.0", "6.0"]

# if using vswhere, configure command line arguments to probe for installed VC editions
_VCVER_TO_VSWHERE_VER = {
    '14.2': [
        ["-version", "[16.0, 17.0)", ], # default: Enterprise, Professional, Community  (order unpredictable?)
        ["-version", "[16.0, 17.0)", "-products", "Microsoft.VisualStudio.Product.BuildTools"], # BuildTools
        ],
    '14.1':    [
        ["-version", "[15.0, 16.0)", ], # default: Enterprise, Professional, Community (order unpredictable?)
        ["-version", "[15.0, 16.0)", "-products", "Microsoft.VisualStudio.Product.BuildTools"], # BuildTools
        ],
    '14.1Exp': [
        ["-version", "[15.0, 16.0)", "-products", "Microsoft.VisualStudio.Product.WDExpress"], # Express
        ],
}

# Experimental version: empty 2017+ keys not necessary.
# Remove 2017+ keys and rename everywhere to _VCVER_TO_PRODUCT_DIR_LE14
_VCVER_TO_PRODUCT_DIR = {
    '14.2': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')], # not set by this version
    '14.1': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')], # not set by this version
    '14.1Exp': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'')], # not set by this version
    '14.0' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\14.0\Setup\VC\ProductDir')],
    '14.0Exp' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\14.0\Setup\VC\ProductDir')],
    '12.0' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\12.0\Setup\VC\ProductDir'),
        ],
    '12.0Exp' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\12.0\Setup\VC\ProductDir'),
        ],
    '11.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\11.0\Setup\VC\ProductDir'),
        ],
    '11.0Exp' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\11.0\Setup\VC\ProductDir'),
        ],
    '10.0': [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\10.0\Setup\VC\ProductDir'),
        ],
    '10.0Exp' : [
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VCExpress\10.0\Setup\VC\ProductDir'),
        ],
    '9.0': [
        (SCons.Util.HKEY_CURRENT_USER, r'Microsoft\DevDiv\VCForPython\9.0\installdir',),
        (SCons.Util.HKEY_LOCAL_MACHINE, r'Microsoft\VisualStudio\9.0\Setup\VC\ProductDir',),
        ],
    '9.0Exp' : [
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

# Express component in vswhere query
_MSVC_COMPONENT_EXPRESS = 'WDExpress'

# Vswhere query elements (reverse dictionaries computed during intialization)
#     MSVS_MAJOR: MSVS installationVersion.split('.')[0] <-> to _VCVER
#     Products: expected product components returned in vswhere query
_MSVC_PRODUCTVERSION_COMPONENTIDS = {
    '14.2': {
        'MSVS_MAJOR' : '16', 
        'Products'   : ['Enterprise', 'Professional', 'Community', 'BuildTools']
        },
    '14.1': { 
        'MSVS_MAJOR' : '15',
        'Products'   : ['Enterprise', 'Professional', 'Community', 'BuildTools', _MSVC_COMPONENT_EXPRESS]
        },
}

# Legacy component for 140 instance in table
_MSVC_COMPONENT_LEGACY = '<LEGACY>'

# Unknown component in vswhere query
_MSVC_COMPONENT_UNKNOWN = '<UNKNOWN>'

# Expected product component names returned from vswhere query for all products.
# The ranking is used as a relative order for multiple instances of a specific toolset version.
# Leave gaps for future additions
_MSVC_COMPONENTID_SELECTION_RANKING = {
    'Enterprise'  : 50,
    'Professional': 40,
    'Community'   : 30,
    'BuildTools'  : 20,
    'WDExpress'   : 10,
    _MSVC_COMPONENT_LEGACY  : 1, # special case for 14.0
    _MSVC_COMPONENT_UNKNOWN : 0, # must be 0: indicates error
}

# Symbol for the express version: 14.1Exp (2017)
_MSVC_SYMBOL_EXPRESS = 'Exp'

# map component id to product version suffix
# user facing suffix for product specification
_MSVC_COMPONENTID_VERSIONSUFFIX = {
    'Enterprise'  : 'Ent',
    'Professional': 'Pro',
    'Community'   : 'Com',
    'BuildTools'  : 'BT' ,
    'WDExpress'   : _MSVC_SYMBOL_EXPRESS,
    _MSVC_COMPONENT_UNKNOWN : 'Unknown', # must be 0: indicates error
}

# Remap express host folder on win64
_MSVC_EXPRESS_HOSTNAME_ISWIN64_RENAMEHOST_GT14 = {
    ('hostx86', True)  : 'hostx64',
}

# Host folders that need processing for windows platform (lower case)
_MSVC_HOSTNAME_ISWIN64_PROCESS_TARGETS_GT14 = {
    ('hostx64', True)  : True,
    ('hostx64', False) : False,
    ('hostx86', True)  : False,
    ('hostx86', False) : True,
}

# Regular Expression to validate/parse MSVC_VERSION
#
#    named groups:
#       version:  _VCVER version or specific version
#       vcver:    _VCVER version or None
#       specific: specific version or None
#       product:  _VCVER version or None
#       suffix:   product type suffix or None

_MSVC_EXTENDED_VERSION_RE = re.compile("""
    # anchor at start of string
    ^
    # version number
    (?P<version>
        # _VCVER version: 14.2
        (?P<vcver> \d{1,2} \. \d{1} )
        |
        # toolset version: 14.16, 14.16.27023
        (?P<specific> \d{1,2} \. \d{2} (?: \. \d{1,5} )* )
    )
    # optional product: '->' 14.2
    (?:
        # optional whitespace
        \s*
        # right assignment literal '->'
        [-][>]
        # optional whitespace
        \s*
        # _VCVER version: 14.2
        (?P<product> \d{1,2} \. \d{1} )
    )*
    # optional whitespace
    \s*
    # optional product type: Ent, Pro, Com, Exp, BT, etc.
    (?P<suffix> [A-Z][A-Za-z]+)*
    # anchor at end of string
    $
""", re.VERBOSE)

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
        raise ValueError("Unrecognized version %s (%s)" % (msvc_version,msvc_version_numeric))


def is_host_target_supported(host_target, msvc_version):
    """Check if (host, target) pair is supported for a VC version.

    Only checks whether a given version *may* support the given
    (host, target) pair, not that the toolchain is actually on the machine.

    Args:
        host_target: canonalized host-target pair, e.g.
          ("x86", "amd64") for cross compilation from 32- to 64-bit Windows.
        msvc_version: Visual C++ version (major.minor), e.g. "10.0"

    Returns:
        True or False

    """
    # We assume that any Visual Studio version supports x86 as a target
    if host_target[1] != "x86":
        maj, min = msvc_version_to_maj_min(msvc_version)
        if maj < 8:
            return False
    return True


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

# Experimental version - these routines are not used:
#     find_vc_pdir_vswhere -> find_vc_pdir_vswhere_classic
#     find_vc_pdir         -> find_vc_pdir_classic

def find_vc_pdir_vswhere_classic(msvc_version, env=None):
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
        debug("Unknown version of MSVC: %s" % msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    if env is None or not env.get('VSWHERE'):
        vswhere_path = msvc_find_vswhere()
    else:
        vswhere_path = env.subst('$VSWHERE')

    if vswhere_path is None:
        return None

    debug('VSWHERE: %s' % vswhere_path)
    for vswhere_version_args in vswhere_version:

        vswhere_cmd = [vswhere_path] + vswhere_version_args + ["-property", "installationPath"]

        debug("running: %s" % vswhere_cmd)

        #cp = subprocess.run(vswhere_cmd, capture_output=True)  # 3.7+ only
        cp = subprocess.run(vswhere_cmd, stdout=PIPE, stderr=PIPE)

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


def find_vc_pdir_classic(env, msvc_version):
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
        debug("Unknown version of MSVC: %s" % msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    for hkroot, key in hkeys:
        try:
            comps = None
            if not key:
                comps = find_vc_pdir_vswhere(msvc_version, env)
                if not comps:
                    debug('no VC found for version {}'.format(repr(msvc_version)))
                    raise SCons.Util.WinError
                debug('VC found: {}'.format(repr(msvc_version)))
                return comps
            else:
                if common.is_win64():
                    try:
                        # ordinarily at win64, try Wow6432Node first.
                        comps = common.read_reg(root + 'Wow6432Node\\' + key, hkroot)
                    except SCons.Util.WinError as e:
                        # at Microsoft Visual Studio for Python 2.7, value is not in Wow6432Node
                        pass
                if not comps:
                    # not Win64, or Microsoft Visual Studio for Python 2.7
                    comps = common.read_reg(root + key, hkroot)
        except SCons.Util.WinError as e:
            debug('no VC registry key {}'.format(repr(key)))
        else:
            debug('found VC in registry: {}'.format(comps))
            if os.path.exists(comps):
                return comps
            else:
                debug('reg says dir is {}, but it does not exist. (ignoring)'.format(comps))
                raise MissingConfiguration("registry dir {} not found on the filesystem".format(comps))
    return None

# Experimental version - replacement routines:
#     
#      call_vswhere_json_output: invokes vswhere and returns json output
#     
#      find_vc_pdir_registry: queries the registry for versions <= 14.0
#     
#      find_vc_pdir_specific:
#        calls find_vc_pdir_vswhere_instance for versions >= 14.1
#        calls find_vc_pdir_registry for versions <= 14.0

def call_vswhere_json_output(vswhere_args, env=None):
    """ Find MSVC instances using the vswhere program.

    Args:
        vswhere_args: query arguments passed to vswhere
        env: optional to look up VSWHERE variable

    Returns:
        json output or None

    """

    if env is None or not env.get('VSWHERE'):
        vswhere_path = msvc_find_vswhere()
    else:
        vswhere_path = env.subst('$VSWHERE')

    if vswhere_path is None:
        debug("vswhere path not found")
        return None

    debug('VSWHERE = %s' % vswhere_path)

    vswhere_cmd = [vswhere_path] + vswhere_args + ['-format', 'json']

    debug("running: %s" % vswhere_cmd)

    #cp = subprocess.run(vswhere_cmd, capture_output=True)  # 3.7+ only
    cp = subprocess.run(vswhere_cmd, stdout=PIPE, stderr=PIPE)
    if not cp.stdout:
        debug("no vswhere information returned")
        return None

    vswhere_output = cp.stdout.decode("mbcs")
    if not vswhere_output:
        debug("no vswhere information output")
        return None

    try:
        vswhere_json = json.loads(vswhere_output)
    except json.decoder.JSONDecodeError:
        debug("json decode exception loading vswhere output")
        vswhere_json = None

    return vswhere_json

def find_vc_pdir_registry(env, msvc_version):
    """Find the MSVC product directory in the registry.

    Tries to look up the path using a registry key from the table
    _VCVER_TO_PRODUCT_DIR.

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
        debug("Unknown version of MSVC: %s" % msvc_version)
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    for hkroot, key in hkeys:
        try:
            comps = None
            if not key:
                raise SCons.Util.WinError
            if common.is_win64():
                try:
                    # ordinarily at win64, try Wow6432Node first.
                    comps = common.read_reg(root + 'Wow6432Node\\' + key, hkroot)
                except SCons.Util.WinError:
                    # at Microsoft Visual Studio for Python 2.7, value is not in Wow6432Node
                    pass
            if not comps:
                # not Win64, or Microsoft Visual Studio for Python 2.7
                comps = common.read_reg(root + key, hkroot)
        except SCons.Util.WinError:
            debug('no VC registry key {}'.format(repr(key)))
        else:
            debug('found VC in registry: {}'.format(comps))
            if os.path.exists(comps):
                return comps
            else:
                debug('reg says dir is {}, but it does not exist. (ignoring)'.format(comps))
                raise MissingConfiguration("registry dir {} not found on the filesystem".format(comps))
    return None


def find_vc_pdir_specific(env, msvc_version):

    msvc_ver_numeric = get_msvc_version_numeric(msvc_version)
    vernum = float(msvc_ver_numeric)

    if vernum >= 14.1:
        vc_dir = find_vc_pdir_vswhere(msvc_version, env)
    else:
        vc_dir = find_vc_pdir_registry(env, msvc_version)

    return vc_dir

def find_batch_file(env,msvc_version,host_arch,target_arch):
    """
    Find the location of the batch script which should set up the compiler
    for any TARGET_ARCH whose compilers were installed by Visual Studio/VCExpress

    In newer (2017+) compilers, make use of the fact there are vcvars
    scripts named with a host_target pair that calls vcvarsall.bat properly,
    so use that and return an indication we don't need the argument
    we would have computed to run vcvarsall.bat.
    """
    pdir = find_vc_pdir(env, msvc_version)
    if pdir is None:
        raise NoVersionFound("No version of Visual Studio found")
    debug('looking in {}'.format(pdir))

    # filter out e.g. "Exp" from the version name
    msvc_ver_numeric = get_msvc_version_numeric(msvc_version)
    use_arg = True
    vernum = float(msvc_ver_numeric)
    if 7 <= vernum < 8:
        pdir = os.path.join(pdir, os.pardir, "Common7", "Tools")
        batfilename = os.path.join(pdir, "vsvars32.bat")
    elif vernum < 7:
        pdir = os.path.join(pdir, "Bin")
        batfilename = os.path.join(pdir, "vcvars32.bat")
    elif 8 <= vernum <= 14:
        batfilename = os.path.join(pdir, "vcvarsall.bat")
    else:  # vernum >= 14.1  VS2017 and above
        batfiledir = os.path.join(pdir, "Auxiliary", "Build")
        targ  = _HOST_TARGET_TO_BAT_ARCH_GT14[(host_arch, target_arch)]
        batfilename = os.path.join(batfiledir, targ)
        use_arg = False

    if not os.path.exists(batfilename):
        debug("Not found: %s" % batfilename)
        batfilename = None

    installed_sdks = get_installed_sdks()
    for _sdk in installed_sdks:
        sdk_bat_file = _sdk.get_sdk_vc_script(host_arch,target_arch)
        if not sdk_bat_file:
            debug("batch file not found:%s" % _sdk)
        else:
            sdk_bat_file_path = os.path.join(pdir,sdk_bat_file)
            if os.path.exists(sdk_bat_file_path):
                debug('sdk_bat_file_path:%s' % sdk_bat_file_path)
                return (batfilename, use_arg, sdk_bat_file_path)
    return (batfilename, use_arg, None)


__INSTALLED_VCS_RUN = None
_VC_TOOLS_VERSION_FILE_PATH = ['Auxiliary', 'Build', 'Microsoft.VCToolsVersion.default.txt']
_VC_TOOLS_VERSION_FILE = os.sep.join(_VC_TOOLS_VERSION_FILE_PATH)

def _check_cl_exists_in_vc_dir(env, vc_dir, msvc_version):
    """Return status of finding a cl.exe to use.

    Locates cl in the vc_dir depending on TARGET_ARCH, HOST_ARCH and the
    msvc version. TARGET_ARCH and HOST_ARCH can be extracted from the
    passed env, unless it is None, in which case the native platform is
    assumed for both host and target.

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

    # determine if there is a specific target platform we want to build for and
    # use that to find a list of valid VCs, default is host platform == target platform
    # and same for if no env is specified to extract target platform from
    if env:
        (host_platform, target_platform, req_target_platform) = get_host_target(env)
    else:
        host_platform = platform.machine().lower()
        target_platform = host_platform

    host_platform = _ARCH_TO_CANONICAL[host_platform]
    target_platform = _ARCH_TO_CANONICAL[target_platform]

    debug('host platform %s, target platform %s for version %s' % (host_platform, target_platform, msvc_version))

    ver_num = float(get_msvc_version_numeric(msvc_version))

    # make sure the cl.exe exists meaning the tool is installed
    if ver_num > 14:
        # 2017 and newer allowed multiple versions of the VC toolset to be
        # installed at the same time. This changes the layout.
        # Just get the default tool version for now
        #TODO: support setting a specific minor VC version
        default_toolset_file = os.path.join(vc_dir, _VC_TOOLS_VERSION_FILE)
        try:
            with open(default_toolset_file) as f:
                vc_specific_version = f.readlines()[0].strip()
        except IOError:
            debug('failed to read ' + default_toolset_file)
            return False
        except IndexError:
            debug('failed to find MSVC version in ' + default_toolset_file)
            return False

        host_trgt_dir = _HOST_TARGET_TO_CL_DIR_GREATER_THAN_14.get((host_platform, target_platform), None)
        if host_trgt_dir is None:
            debug('unsupported host/target platform combo: (%s,%s)'%(host_platform, target_platform))
            return False

        cl_path = os.path.join(vc_dir, 'Tools','MSVC', vc_specific_version, 'bin',  host_trgt_dir[0], host_trgt_dir[1], _CL_EXE_NAME)
        debug('checking for ' + _CL_EXE_NAME + ' at ' + cl_path)
        if os.path.exists(cl_path):
            debug('found ' + _CL_EXE_NAME + '!')
            return True

        elif host_platform == "amd64" and host_trgt_dir[0] == "Hostx64":
            # Special case: fallback to Hostx86 if Hostx64 was tried
            # and failed.  This is because VS 2017 Express running on amd64
            # will look to our probe like the host dir should be Hostx64,
            # but Express uses Hostx86 anyway.
            # We should key this off the "x86_amd64" and related pseudo
            # targets, but we don't see those in this function.
            host_trgt_dir = ("Hostx86", host_trgt_dir[1])
            cl_path = os.path.join(vc_dir, 'Tools','MSVC', vc_specific_version, 'bin',  host_trgt_dir[0], host_trgt_dir[1], _CL_EXE_NAME)
            debug('checking for ' + _CL_EXE_NAME + ' at ' + cl_path)
            if os.path.exists(cl_path):
                debug('found ' + _CL_EXE_NAME + '!')
                return True

    elif 14 >= ver_num >= 8:
        # Set default value to be -1 as "", which is the value for x86/x86,
        # yields true when tested if not host_trgt_dir
        host_trgt_dir = _HOST_TARGET_TO_CL_DIR.get((host_platform, target_platform), None)
        if host_trgt_dir is None:
            debug('unsupported host/target platform combo')
            return False

        cl_path = os.path.join(vc_dir, 'bin',  host_trgt_dir, _CL_EXE_NAME)
        debug('checking for ' + _CL_EXE_NAME + ' at ' + cl_path)

        cl_path_exists = os.path.exists(cl_path)
        if not cl_path_exists and host_platform == 'amd64':
            # older versions of visual studio only had x86 binaries,
            # so if the host platform is amd64, we need to check cross
            # compile options (x86 binary compiles some other target on a 64 bit os)

            # Set default value to be -1 as "" which is the value for x86/x86 yields true when tested
            # if not host_trgt_dir
            host_trgt_dir = _HOST_TARGET_TO_CL_DIR.get(('x86', target_platform), None)
            if host_trgt_dir is None:
                return False

            cl_path = os.path.join(vc_dir, 'bin', host_trgt_dir, _CL_EXE_NAME)
            debug('checking for ' + _CL_EXE_NAME + ' at ' + cl_path)
            cl_path_exists = os.path.exists(cl_path)

        if cl_path_exists:
            debug('found ' + _CL_EXE_NAME + '!')
            return True

    elif 8 > ver_num >= 6:
        # quick check for vc_dir/bin and vc_dir/ before walk
        # need to check root as the walk only considers subdirectories
        for cl_dir in ('bin', ''):
            cl_path = os.path.join(vc_dir, cl_dir, _CL_EXE_NAME)
            if os.path.exists(cl_path):
                debug(_CL_EXE_NAME + ' found %s' % cl_path)
                return True
        # not in bin or root: must be in a subdirectory
        for cl_root, cl_dirs, _ in os.walk(vc_dir):
            for cl_dir in cl_dirs:
                cl_path = os.path.join(cl_root, cl_dir, _CL_EXE_NAME)
                if os.path.exists(cl_path):
                    debug(_CL_EXE_NAME + ' found %s' % cl_path)
                    return True
        return False
    else:
        # version not support return false
        debug('unsupported MSVC version: ' + str(ver_num))

    return False

def get_installed_vcs(env=None):
    global __INSTALLED_VCS_RUN

    if __INSTALLED_VCS_RUN is not None:
        return __INSTALLED_VCS_RUN

    installed_versions = []

    if _MSVC_EXPERIMENTAL_ACTIVE:
        prepare_installed_vctoolsets(env, get_installed_vcs=True)

    for ver in _VCVER:
        debug('trying to find VC %s' % ver)
        try:
            VC_DIR = find_vc_pdir(env, ver)
            if VC_DIR:
                debug('found VC %s' % ver)
                if _check_cl_exists_in_vc_dir(env, VC_DIR, ver):
                    installed_versions.append(ver)
                else:
                    debug('no compiler found %s' % ver)
            else:
                debug('return None for ver %s' % ver)
        except (MSVCUnsupportedTargetArch, MSVCUnsupportedHostArch):
            # Allow this exception to propagate further as it should cause
            # SCons to exit with an error code
            raise
        except (MSVCProductInvalid, MSVCProductNotFound) as e:
            # version >= 14.1: UnsupportedVersion, MSVCProductInvalid, MSVCProductNotFound
            raise e
        except VisualCException as e:
            debug('did not find VC %s: caught exception %s' % (ver, str(e)))

    if _MSVC_EXPERIMENTAL_ACTIVE:
        setup_installed_vctoolsets(env)

    __INSTALLED_VCS_RUN = installed_versions
    return __INSTALLED_VCS_RUN

def reset_installed_vcs():
    """Make it try again to find VC.  This is just for the tests."""
    global __INSTALLED_VCS_RUN
    if _MSVC_EXPERIMENTAL_ACTIVE:
        reset_installed_vctoolsets()
    __INSTALLED_VCS_RUN = None

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
    cache_key = "{}--{}".format(script, args)
    cache_data = script_env_cache.get(cache_key, None)
    if cache_data is None:
        stdout = common.get_output(script, args)

        # Stupid batch files do not set return code: we take a look at the
        # beginning of the output for an error message instead
        olines = stdout.splitlines()
        if olines[0].startswith("The specified configuration type is missing"):
            raise BatchFileExecutionError("\n".join(olines[:2]))

        cache_data = common.parse_output(stdout)
        script_env_cache[cache_key] = cache_data
        # once we updated cache, give a chance to write out if user wanted
        common.write_script_env_cache(script_env_cache)

    return cache_data

def get_default_version(env):
    msvc_version = env.get('MSVC_VERSION')
    msvs_version = env.get('MSVS_VERSION')
    debug('msvc_version:%s msvs_version:%s' % (msvc_version, msvs_version))

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
        debug('installed_vcs:%s' % installed_vcs)
        if not installed_vcs:
            #msg = 'No installed VCs'
            #debug('msv %s' % repr(msg))
            #SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, msg)
            debug('No installed VCs')
            return None
        msvc_version = installed_vcs[0]
        debug('using default installed MSVC version %s' % repr(msvc_version))
    else:
        debug('using specified MSVC version %s' % repr(msvc_version))

    return msvc_version

def msvc_setup_env_once(env):
    try:
        has_run  = env["MSVC_SETUP_RUN"]
    except KeyError:
        has_run = False

    if not has_run:
        msvc_setup_env(env)
        env["MSVC_SETUP_RUN"] = True

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

    # Find the host, target, and if present the requested target:
    platforms = get_host_target(env)
    debug("host_platform %s, target_platform %s req_target_platform %s" % platforms)
    host_platform, target_platform, req_target_platform = platforms

    # Most combinations of host + target are straightforward.
    # While all MSVC / Visual Studio tools are pysically 32-bit, they
    # make it look like there are 64-bit tools if the host is 64-bit,
    # so you can invoke the environment batch script to set up to build,
    # say, amd64 host -> x86 target. Express versions are an exception:
    # they always look 32-bit, so the batch scripts with 64-bit
    # host parts are absent. We try to fix that up in a couple of ways.
    # One is here: we make a table of "targets" to try, with the extra
    # targets being tags that tell us to try a different "host" instead
    # of the deduced host.
    try_target_archs = [target_platform]
    if req_target_platform in ('amd64', 'x86_64'):
        try_target_archs.append('x86_amd64')
    elif req_target_platform in ('x86',):
        try_target_archs.append('x86_x86')
    elif req_target_platform in ('arm',):
        try_target_archs.append('x86_arm')
    elif req_target_platform in ('arm64',):
        try_target_archs.append('x86_arm64')
    elif not req_target_platform:
        if target_platform in ('amd64', 'x86_64'):
            try_target_archs.append('x86_amd64')
            # If the user hasn't specifically requested a TARGET_ARCH,
            # and the TARGET_ARCH is amd64 then also try 32 bits
            # if there are no viable 64 bit tools installed
            try_target_archs.append('x86')

    debug("host_platform: %s, try_target_archs: %s"%(host_platform, try_target_archs))

    if _MSVC_EXPERIMENTAL_ACTIVE:
        vcvars_ver = None
        ver_num = float(get_msvc_version_numeric(version))
        if ver_num >= 14.1:
            try:
                # version is volatile: may change based on (host_platform, target_platform, toolset)
                # TODO|JCB: if moved back into loop below need to re-initialize the version each time (change argument name)
                version, vcvars_ver = msvc_find_specific_version(env, version, host_platform, target_platform)
            except (MSVCProductInvalid, MSVCProductNotFound) as e:
                # product/version conflict or not installed
                raise e
            except (MSVCTargetNotFound) as e:
                # (host,target) not found
                # this indicates an error with the toolset initialization
                raise e
            except (MSVCToolsetNotFound) as e:
                # (host,target) exists: toolset not found
                raise e

    d = None
    for tp in try_target_archs:
        # Set to current arch.
        env['TARGET_ARCH'] = tp

        debug("trying target_platform:%s" % tp)
        host_target = (host_platform, tp)
        if not is_host_target_supported(host_target, version):
            warn_msg = "host, target = %s not supported for MSVC version %s" % \
                (host_target, version)
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        arg = _HOST_TARGET_ARCH_TO_BAT_ARCH[host_target]

        # Try to locate a batch file for this host/target platform combo
        try:
            (vc_script, use_arg, sdk_script) = find_batch_file(env, version, host_platform, tp)
            debug('vc_script:%s sdk_script:%s'%(vc_script,sdk_script))
        except (MSVCProductInvalid, MSVCProductNotFound) as e:
            # version >= 14.1: UnsupportedVersion, MSVCProductInvalid, MSVCProductNotFound
            raise e
        except VisualCException as e:
            msg = str(e)
            debug('Caught exception while looking for batch file (%s)' % msg)
            warn_msg = "VC version %s not installed.  " + \
                       "C/C++ compilers are most likely not set correctly.\n" + \
                       " Installed versions are: %s"
            warn_msg = warn_msg % (version, get_installed_vcs(env))
            SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
            continue

        # Try to use the located batch file for this host/target platform combo
        debug('use_script 2 %s, args:%s' % (repr(vc_script), arg))
        found = None
        if vc_script:
            if not use_arg:
                arg = ''  # bat file will supply platform type
            # Get just version numbers
            maj, min = msvc_version_to_maj_min(version)
            # VS2015+
            if maj >= 14:
                if env.get('MSVC_UWP_APP') == '1':
                    # Initialize environment variables with store/UWP paths
                    arg = (arg + ' store').lstrip()
            if _MSVC_EXPERIMENTAL_ACTIVE:
                # VS2017+
                if vcvars_ver:
                    arg = (arg + vcvars_ver).lstrip()

            try:
                d = script_env(vc_script, args=arg)
                found = vc_script
            except BatchFileExecutionError as e:
                debug('use_script 3: failed running VC script %s: %s: Error:%s'%(repr(vc_script),arg,e))
                vc_script=None
                continue
        if not vc_script and sdk_script:
            debug('use_script 4: trying sdk script: %s' % sdk_script)
            try:
                d = script_env(sdk_script)
                found = sdk_script
            except BatchFileExecutionError as e:
                debug('use_script 5: failed running SDK script %s: Error:%s'%(repr(sdk_script), e))
                continue
        elif not vc_script and not sdk_script:
            debug('use_script 6: Neither VC script nor SDK script found')
            continue

        debug("Found a working script/target: %s/%s"%(repr(found),arg))
        break # We've found a working target_platform, so stop looking

    if _MSVC_EXPERIMENTAL_ACTIVE:
        if ver_num >= 14.1:
            # finalize: commit to specific version (found) or rollback (not found)
            msvc_finalize_specific_version(env, version, (not d))

    # If we cannot find a viable installed compiler, reset the TARGET_ARCH
    # To it's initial value
    if not d:
        env['TARGET_ARCH']=req_target_platform

    return d


def msvc_setup_env(env):
    debug('called')
    version = get_default_version(env)
    if version is None:
        warn_msg = "No version of Visual Studio compiler found - C/C++ " \
                   "compilers most likely not set correctly"
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None

    if _MSVC_EXPERIMENTAL_ACTIVE:
        # MSVC_VERSION extended format support:
        #    - Save the user version specification
        #    - Verify/validate user specification for 2017+
        #    - Remap version to product version if specified
        #    - Return a _VCVER compatible version
        version = msvc_version_from_toolset(env, version)

    # XXX: we set-up both MSVS version for backward
    # compatibility with the msvs tool
    env['MSVC_VERSION'] = version
    env['MSVS_VERSION'] = version
    env['MSVS'] = {}

    if _MSVC_EXPERIMENTAL_ACTIVE:
        if _MSVC_CONFIG.TESTING_DISPLAY_TOOLSET_DICT:
            _display_msvc_toolset(env, version, label='msvc_setup_env')


    use_script = env.get('MSVC_USE_SCRIPT', True)
    if SCons.Util.is_String(use_script):
        debug('use_script 1 %s' % repr(use_script))
        d = script_env(use_script)
    elif use_script:
        d = msvc_find_valid_batch_script(env,version)
        debug('use_script 2 %s' % d)
        if not d:
            return d
    else:
        debug('MSVC_USE_SCRIPT set to False')
        warn_msg = "MSVC_USE_SCRIPT set to False, assuming environment " \
                   "set correctly."
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)
        return None

    for k, v in d.items():
        env.PrependENVPath(k, v, delete_existing=True)
        debug("env['ENV']['%s'] = %s" % (k, env['ENV'][k]))

    # final check to issue a warning if the compiler is not present
    if not find_program_path(env, 'cl'):
        debug("did not find " + _CL_EXE_NAME)
        if CONFIG_CACHE:
            propose = "SCONS_CACHE_MSVC_CONFIG caching enabled, remove cache file {} if out of date.".format(CONFIG_CACHE)
        else:
            propose = "It may need to be installed separately with Visual Studio."
        warn_msg = "Could not find MSVC compiler 'cl'. {}".format(propose)
        SCons.Warnings.warn(SCons.Warnings.VisualCMissingWarning, warn_msg)

def msvc_exists(env=None, version=None):
    vcs = get_installed_vcs(env)
    if version is None:
        return len(vcs) > 0
    return version in vcs

# Notes:
#   Function names called the from existing code base begin with a letter.
#   Function names internal to the version specific code base begin with an underscore.
#
# TODO|JCB
#   - add a function to call from _check_cl_exists_in_vc_dir for 14.1+ since the
#     version specific code already found all of the cl executables.
#   - exception handling
#   - additional debug messages
#   - documentation

# use class variables as a single global namespace variable
class _MSVC_CONFIG:

    ### internal development flags

    # testing: print version tables
    TESTING_DISPLAY_TOOLSET_TABLES = False

    # testing: print MSVC_TOOLSET dictionary
    TESTING_DISPLAY_TOOLSET_DICT = False

    # number indent size for output display
    TESTING_DISPLAY_INDENT_NSPACES = 2

    # testing: ignore installed 2017+ products
    TESTING_IGNORE_INSTALLED_PRODUCT  = False
    TESTING_IGNORE_INSTALLED_PRODUCTS = []

    ### startup initialization 

    # toolset cache dictionary key
    MSVC_TOOLSET_CACHE = '_CACHE_'

    MSVC_RANK_EXPRESS = _MSVC_COMPONENTID_SELECTION_RANKING[_MSVC_COMPONENT_EXPRESS]
    MSVC_RANK_LEGACY  = _MSVC_COMPONENTID_SELECTION_RANKING[_MSVC_COMPONENT_LEGACY]

    ### internal initialization done once [not reset for tests]

    INTERNAL_SETUP_RUN_ONCE = False

    # map MSVC 2015 host/target directory names to (host,target) specification names
    HOST_DIRNAME_TO_HOST_TARGETNAME_EQ14 = {}

    # map MSVC 2017+ host/target directory names to (host,target) specification names
    HOST_DIRNAME_TO_HOST_TARGETNAME_GT14 = {}

    # map product version suffix to component id
    MSVC_VERSIONSUFFIX_COMPONENTID = {}

    # when using vswhere, map the major MSVS version to the MSVC_VERSION above
    # '14.1Exp' is handled as a special case
    MSVS_MAJORVERSION_TO_VCVER = {}

    # synthetic _VCVER symbols (e.g., "14.2Ent")
    MSVC_VCVER_SYNTHETIC = []

    # list of 14.1+ extended symbols
    MSVC_VCVER_EXTENDED = []

    ### internal configuration [reset for tests]

    VCVER_INSTALLED_TOOLSETS_DEFAULT = False
    VCVER_INSTALLED_TOOLSETS_PREPARED = False
    VCVER_INSTALLED_TOOLSETS_SETUP = False

    # vswhere installations found > 0
    MSVC_INSTALLED_ANY = False

    # vswhere -legacy installationPaths for 14.0 > 0
    MSVC_INSTALLED_140 = False

    # vswhere.exe instances found by _VCVER version
    # an instance is installed once
    MSVC_VSWHERE_INSTANCES_UNIQUE = {}

    # vswhere.exe instances found by _VCVER version w/synthetic alias
    # an instance may be installed with more than one key (key and synthetic key)
    MSVC_VSWHERE_INSTANCES = {}

    # global toolset version support for VS2017+
    VCVER_INSTALLED_SPECIFIC_VERSIONS = {}

    # MSVC toolset version support for VS2017+
    VCVER_VERSION_SPECIFIC_VERSIONS = {}

    # _VCVER versions of VS2017+
    VCVER_VERSION_LIST = []

    # numeric msvc versions of VS2017+
    VCVER_NUMERIC_VERSION_LIST = []
    VCVER_NUMERIC_COMPONENT_LIST = []

    # numeric msvc versions of VS2017+ with vcvars140.bat
    VCVER_VCVARS140_NUMERIC_VERSION_LIST = []

    # msvc VS2017+ products with vcvars140.bat
    VCVER_VCVARS140_PRODUCT_LIST = []

    # diagnostic counts (products does not include 14.0)
    N_PRODUCTS = 0
    N_TOOLSETS = 0

    # memoize _find_product_version results
    MEMOS_FIND_PRODUCT_VERSION = {}

    # memoize msvc_find_specific_version results
    MEMOS_FIND_SPECIFIC_VERSION = {}

    @classmethod
    def reset_installed(cls):

        cls.MSVC_INSTALLED_ANY = False
        cls.MSVC_INSTALLED_140 = False

        cls.MSVC_VSWHERE_INSTANCES_UNIQUE = {}
        cls.MSVC_VSWHERE_INSTANCES = {}

        cls.VCVER_INSTALLED_SPECIFIC_VERSIONS = {}

        cls.VCVER_VERSION_SPECIFIC_VERSIONS = {}

        cls.VCVER_VERSION_LIST = []

        cls.VCVER_NUMERIC_VERSION_LIST = []
        cls.VCVER_NUMERIC_COMPONENT_LIST = []

        cls.VCVER_VCVARS140_NUMERIC_VERSION_LIST = []
        cls.VCVER_VCVARS140_PRODUCT_LIST = []

        cls.MEMOS_FIND_PRODUCT_VERSION = {}
        cls.MEMOS_FIND_SPECIFIC_VERSION = {}

        cls.N_PRODUCTS = 0
        cls.N_TOOLSETS = 0

        cls.VCVER_INSTALLED_TOOLSETS_DEFAULT = False
        cls.VCVER_INSTALLED_TOOLSETS_PREPARED = False
        cls.VCVER_INSTALLED_TOOLSETS_SETUP = False

def _msvc_version_to_vcver_version(msvc_version):
    # convert a possibly specific version to a _VCVER version for numeric values (e.g., 14.2, 14.1)
    # otherwise, a second digit in the minor version could break existing major, minor numeric tests
    # assuming msvc version was validated with regular expression match
    prefix = ''.join([x for x in msvc_version if x in string_digits + '.'])
    suffix = msvc_version[len(prefix):]
    fields = prefix.split('.')
    return ''.join([fields[0],'.',fields[1][0],suffix])

def _msvc_product_to_vcver_version(msvc_product):
    if msvc_product in _MSVC_CONFIG.VCVER_VERSION_LIST:
        return msvc_product
    return ''.join([x for x in msvc_product if x in string_digits + '.'])

def msvc_version_from_toolset(env, msvc_version):

    version = msvc_version

    env['MSVC_TOOLSET'] = {

        'USERVER': None,  # save user version specification
        'VERSION': None,  # specific version without suffix
        'PRODUCT': None,  # product version (suffix optional)
        'MSVCVER': None,  # _VCVER compatible version
        'VARSVER': None,  # version used for vcvars batch file

        # cache values to allow state rollback if lookup fails
        _MSVC_CONFIG.MSVC_TOOLSET_CACHE: {},

    }

    env['MSVC_TOOLSET']['USERVER'] = ''.join(version.split(' '))

    # get_installed_vcs may not have been called earlier
    if not _MSVC_CONFIG.INTERNAL_SETUP_RUN_ONCE:
        _setup_internal_vctoolsets()

    m = _MSVC_EXTENDED_VERSION_RE.match(version)
    if not m:
        raise UnsupportedVersion('version: %s' % version)

    vc_version = m.group('version')
    vc_ver = _msvc_version_to_vcver_version(vc_version)

    if vc_ver not in _VCVER:
        raise UnsupportedVersion('version: %s (%s)' % (version, vc_ver))

    is_known = False
    is_synthetic = False

    vc_suffix = ''
    if m.group('suffix'):

        vc_suffix = m.group('suffix')

        if vc_suffix not in _MSVC_CONFIG.MSVC_VERSIONSUFFIX_COMPONENTID:
            raise MSVCProductInvalid('product type: %s (%s)' % (version, vc_suffix))

        if vc_ver + vc_suffix in _VCVER:
            is_known = True
        else:
            is_synthetic = True

    vc_product = ''
    if m.group('product'):

        vc_product = m.group('product')

        if vc_product not in _VCVER:
            raise UnsupportedVersion('product version: %s (%s)' % (version, vc_product))

        vc_product += vc_suffix

    elif is_known:

        # no product specified: attach suffix for known versions
        vc_product = vc_ver + vc_suffix

        # attach suffix for _VCVER version
        vc_ver += vc_suffix

    elif is_synthetic:

        # no product specified: attach suffix for synthetic versions
        vc_product = vc_ver + vc_suffix

    if not vc_product:
        vc_product = None

    # save specific version and product
    env['MSVC_TOOLSET']['VERSION'] = vc_version
    env['MSVC_TOOLSET']['PRODUCT'] = vc_product

    vc_vernum = float(get_msvc_version_numeric(vc_ver))
    vc_product_vernum = float(get_msvc_version_numeric(vc_product)) if vc_product else 0.0

    # version and/or product is 2017+
    if vc_vernum >= 14.1 or vc_product_vernum >= 14.1:

        # get_installed_vcs may not have been called earlier
        if not _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_PREPARED:
            setup_installed_vctoolsets(env)

        # version/product combination configuration
        vc_product, _, _ = _find_product_version(env, vc_ver)

        if vc_product:
            # replace version with user specified product version
            vc_version = _msvc_product_to_vcver_version(vc_product)

    else:

        # product specification for version <= 2015
        if vc_product:
            # record the product as the version
            vc_version = vc_product

    # _VCVER compatible version number to return
    version = _msvc_version_to_vcver_version(vc_version)

    if vc_ver != version:
        debug('using MSVC version %s' % repr(version))

    # save _VCVER version
    env['MSVC_TOOLSET']['MSVCVER'] = version

    if _MSVC_CONFIG.TESTING_DISPLAY_TOOLSET_DICT:
        _display_msvc_toolset(env, msvc_version, label='msvc_version_from_toolset')

    return version

_FIND_PRODUCT_VERSION_VAL = namedtuple('product_version', 'vc_product, vc_product_version_numeric, vc_component_rank')

def _find_product_version(env, msvc_version):

    ret = _FIND_PRODUCT_VERSION_VAL(None, None, None)

    msvc_toolset = env.get('MSVC_TOOLSET', None)
    if not msvc_toolset:
        debug("product_version: MSVC_TOOLSET undefined -> %s" % repr(ret))
        return ret

    vc_product = msvc_toolset.get('PRODUCT', None)
    if not vc_product:
        debug("product_version: (%s, None) -> %s" % (msvc_version, repr(ret)))
        return ret

    memo_key = (msvc_version, vc_product)
    memo_val = _MSVC_CONFIG.MEMOS_FIND_PRODUCT_VERSION.get(memo_key, None)

    if not memo_val:

        vcver_str = _msvc_version_to_vcver_version(msvc_version)
        vcver_num = float(get_msvc_version_numeric(vcver_str))

        vc_product_version_numeric = None
        vc_component_rank = None

        vc_product_version = get_msvc_version_numeric(vc_product)
        vc_product_version_numeric = float(vc_product_version)

        # validate product version: 2017+ and in supported version list
        if vc_product_version_numeric < 14.1 or vc_product_version not in _VCVER:
            raise MSVCProductInvalid('product: %s' % vc_product)

        # verify product version >= msvc version
        if vc_product_version_numeric < vcver_num:
            raise MSVCProductInvalid('product version %s < msvc version %s' % (vc_product_version_numeric, vcver_num))

        # verify product version installed
        if vc_product_version_numeric not in _MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST:
            raise MSVCProductNotFound('product not found: %s' % vc_product)

        if vc_product_version != vc_product:

            vc_product_suffix = vc_product[len(vc_product_version):]
            vc_component_id = _MSVC_CONFIG.MSVC_VERSIONSUFFIX_COMPONENTID.get(vc_product_suffix,_MSVC_COMPONENT_UNKNOWN)
            vc_component_rank = _MSVC_COMPONENTID_SELECTION_RANKING[vc_component_id]

            if vc_component_rank == 0:
                raise MSVCProductInvalid('msvc product: %s' % vc_product)

            if vc_component_rank not in _MSVC_CONFIG.VCVER_NUMERIC_COMPONENT_LIST:
                raise MSVCProductNotFound('product not found: %s' % vc_product)

        memo_val = _FIND_PRODUCT_VERSION_VAL(vc_product, vc_product_version_numeric, vc_component_rank)
        _MSVC_CONFIG.MEMOS_FIND_PRODUCT_VERSION[memo_key] = memo_val

    debug("product_version: %s -> %s" % (repr(memo_key), repr(memo_val)))
    return memo_val

def _search_tool_list_for_toolset(vc_tool_list, vc_specific_version, msvc_version_numeric_include):

    for vc_instance in vc_tool_list:
        # filter based on numeric version (if specified)
        if msvc_version_numeric_include and vc_instance['msvc_version_numeric'] not in msvc_version_numeric_include:
            continue
        # filter based on desired msvc_version
        if vc_instance['msvc_specific_version'].startswith(vc_specific_version):
            debug('tool list toolset found:%s %s %s %s' % (vc_specific_version, vc_instance['msvc_version'], vc_instance['msvc_product'], vc_instance['vcvars_ver']))
            return vc_instance

    debug('tool list toolset not found:%s' % vc_specific_version)
    raise MSVCToolsetNotFound('toolset not found: %s' % vc_specific_version)

def _find_toolset_installed(env, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include=None):

    try:
        vc_tool_list = _MSVC_CONFIG.VCVER_INSTALLED_SPECIFIC_VERSIONS[(vc_host, vc_target)]
    except KeyError:
        debug('installed toolset lookup failed:(%s,%s)' % (vc_host, vc_target))
        raise MSVCTargetNotFound('lookup failed: (%s,%s)' % (vc_host, vc_target))

    return _search_tool_list_for_toolset(vc_tool_list, vc_specific_version, msvc_version_numeric_include)

def _find_toolset_version(env, msvc_version, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include=None):

    try:
        vc_tool_d = _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS[msvc_version]
    except KeyError:
        debug('version toolset msvc_version not found:%s' % msvc_version)
        raise MSVCProductNotFound('product not found: %s' % msvc_version)

    try:
        vc_tool_list = vc_tool_d[(vc_host, vc_target)]
    except KeyError:
        debug('version toolset lookup failed:%s (%s,%s)' % (msvc_version, vc_host, vc_target))
        raise MSVCTargetNotFound('lookup failed: %s (%s,%s)' % (msvc_version, vc_host, vc_target))

    return _search_tool_list_for_toolset(vc_tool_list, vc_specific_version, msvc_version_numeric_include)

def _find_toolset(env, search_version, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include=None):

    if search_version:
        vc_instance = _find_toolset_version(env, search_version, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include)
    else:
        vc_instance = _find_toolset_installed(env, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include)

    return vc_instance

def _find_toolset_twolevel(env, search_version, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include=None):

    vc_instance = None

    if search_version:
        try:
            vc_instance = _find_toolset_version(env, search_version, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include)
        except (MSVCProductNotFound, MSVCTargetNotFound, MSVCToolsetNotFound):
            pass

    if not vc_instance:
        vc_instance = _find_toolset_installed(env, vc_host, vc_target, vc_specific_version, msvc_version_numeric_include)

    return vc_instance

def msvc_finalize_specific_version(env, version, rollback):

    if rollback:
        if env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE]:
            for key, value in env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE].items():
                env['MSVC_TOOLSET'][key] = value
    else:
        msvc_version = env['MSVC_TOOLSET']['MSVCVER']
        if env['MSVC_VERSION'] != msvc_version:
            #TODO|JCB: overwrite MSVC_VERSION, MSVS_VERSION?
            env['MSVC_VERSION'] = msvc_version
            env['MSVS_VERSION'] = msvc_version

    env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE] = {}

    if _MSVC_CONFIG.TESTING_DISPLAY_TOOLSET_DICT:
        _display_msvc_toolset(env, version, label='msvc_finalize_specific_version')

_MSVC_FIND_SPECIFIC_VERSION_KEY = namedtuple('specific_version_key','vc_specific_version, vc_product, vc_host, vc_target')
_MSVC_FIND_SPECIFIC_VERSION_VAL = namedtuple('specific_version','vc_ver, vc_product, vc_varsver, vcvars_ver')

def msvc_find_specific_version(env, msvc_version, vc_host, vc_target):

    # Rollback the cache if necessary (e.g., when called in a loop)
    if env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE]:
        for key, value in env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE].items():
            env['MSVC_TOOLSET'][key] = value
        env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE] = {}

    vc_specific_version = env['MSVC_TOOLSET']['VERSION']

    vc_product, vc_product_version_numeric, vc_component_rank = _find_product_version(env, msvc_version)

    # save initial values to detect changes
    ini_product = vc_product
    ini_version = env['MSVC_TOOLSET']['MSVCVER']
    ini_varsver = env['MSVC_TOOLSET']['VARSVER']

    memo_key = _MSVC_FIND_SPECIFIC_VERSION_KEY(vc_specific_version, vc_product, vc_host, vc_target)
    memo_val = _MSVC_CONFIG.MEMOS_FIND_SPECIFIC_VERSION.get(memo_key, None)

    if not memo_val:

        if not vc_specific_version.startswith("14.0"):

            if vc_product:

                # specific version with a product specification
                search_version = vc_product

                vc_instance = _find_toolset(env, search_version, vc_host, vc_target, vc_specific_version)

            else:

                # The default SCons version setup may come through here. The default
                # SCons version is the latest _VCVER product installed. Therefore, there
                # should not be an upcast promotion to a later product.  However, with
                # multiple products for the latest version, the product may change based 
                # on installed toolset versions.

                # specific version without a product specification
                search_version = _msvc_version_to_vcver_version(vc_specific_version)

                # perform two level probe:
                #   1st probe: version table [vcver] returns vcver product with specific version if found
                #   2nd probe: global table returns product with specific version if found

                vc_instance = _find_toolset_twolevel(env, search_version, vc_host, vc_target, vc_specific_version)

            # required variables for return processing
            vc_ver = vc_instance['msvc_version']
            vc_product = vc_instance['msvc_product']
            vc_varsver = vc_instance['vcvars_toolset_version']
            vcvars_ver = vc_instance['vcvars_ver']

            memo_val = _MSVC_FIND_SPECIFIC_VERSION_VAL(vc_ver, vc_product, vc_varsver, vcvars_ver)

        else:

            # 2017+ using the 2015 build tools: --vcvars_ver=14.0

            # Verify the (host,target) in two places:
            #   the vc_instance for the 2017+ version which will call
            #   the vc_instance for the 2015 version

            if not vc_product:
                # We do not have a product and the version is 14.0 (should *not* happen)
                raise MSVCProductInvalid('unexpected msvc version: %s' % vc_specific_version)

            # We have a product version.

            # If specified, verify the product type is installed as it was not checked earlier.
            if vc_component_rank is not None:

                if vc_product not in _MSVC_CONFIG.VCVER_VCVARS140_PRODUCT_LIST:
                    raise MSVCToolsetNotFound('vcvars140.bat not found: %s' % vc_product)

            # search the version table for default product version of 2017+
            search_version = vc_product
            vc_specific_version = get_msvc_version_numeric(vc_product)
            vc_instance = _find_toolset(env, search_version, vc_host, vc_target, vc_specific_version)

            # required variables for return processing
            vc_ver = vc_instance['msvc_version']
            vc_product = vc_instance['msvc_product']

            # search the version table for 2015
            search_version = '14.0'
            vc_specific_version = '14.0'
            vc_instance = _find_toolset(env, search_version, vc_host, vc_target, vc_specific_version)

            # required variables for return processing
            vc_varsver = vc_instance['vcvars_toolset_version']
            vcvars_ver = vc_instance['vcvars_ver']

            memo_val = _MSVC_FIND_SPECIFIC_VERSION_VAL(vc_ver, vc_product, vc_varsver, vcvars_ver)

        # memoize search results
        _MSVC_CONFIG.MEMOS_FIND_SPECIFIC_VERSION[memo_key] = memo_val

    # save modified PRODUCT before overwriting so that it can be rolled back if necessary
    if ini_product != memo_val.vc_product:
        key = 'PRODUCT'
        env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE][key] = env['MSVC_TOOLSET'][key]
        env['MSVC_TOOLSET'][key] = memo_val.vc_product

    # save modified MSVCVER before overwriting so that it can be rolled back if necessary
    if ini_version != memo_val.vc_ver:
        key = 'MSVCVER'
        env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE][key] = env['MSVC_TOOLSET'][key]
        env['MSVC_TOOLSET'][key] = memo_val.vc_ver

    # save VARSVER before overwriting so that it can be rolled back if necessary
    if ini_varsver != memo_val.vc_varsver:
        key = 'VARSVER'
        env['MSVC_TOOLSET'][_MSVC_CONFIG.MSVC_TOOLSET_CACHE][key] = env['MSVC_TOOLSET'][key]
        env['MSVC_TOOLSET'][key] = memo_val.vc_varsver

    if _MSVC_CONFIG.TESTING_DISPLAY_TOOLSET_DICT:
        _display_msvc_toolset(env, msvc_version, label='msvc_find_specific_version')

    debug("specific_version: %s -> %s" % (repr(memo_key), repr(memo_val)) )
    return (memo_val.vc_ver, memo_val.vcvars_ver)

def find_vc_pdir_vswhere_instance(msvc_version, env=None):

    if msvc_version not in _VCVER:
        raise UnsupportedVersion("Unknown version %s" % msvc_version)

    # get_installed_vcs may not have been called earlier
    if not _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_PREPARED:
        setup_installed_vctoolsets(env)

    # ignore when finding default environments
    if not _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_DEFAULT and env:
        vc_product, vc_product_version_numeric, vc_component_rank = _find_product_version(env, msvc_version)
        if vc_product:
            msvc_instances = _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.get(vc_product, None)
            if msvc_instances:
                debug('vc_product found in vswhere instances: %s' % vc_product)
                return os.path.join(msvc_instances[0]['installationPath'], 'VC')
            raise MSVCProductNotFound('product not found: %s' % vc_product)

    msvc_instances = _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.get(msvc_version, None)
    if msvc_instances:
        debug('msvc_version found in vswhere instances: %s' % msvc_version)
        return os.path.join(msvc_instances[0]['installationPath'], 'VC')

    debug('msvc_version not found in vswhere instances: %s' % msvc_version)
    return None

def _register_host_target_toolset(key, vc_specific_version, vc_version_numeric, vc_rank, vc_version, vc_product, vcvars_ver=None):

    if not vcvars_ver:
        vcvars_ver = vc_specific_version

    vc_instance = {
        'msvc_specific_version': vc_specific_version,
        'msvc_version_numeric': vc_version_numeric,
        'msvc_component_rank': vc_rank,
        'msvc_version': vc_version,
        'msvc_product': vc_product,
        'vcvars_toolset_version': vcvars_ver,
        'vcvars_ver': ' -vcvars_ver=' + vcvars_ver,
    }

    _MSVC_CONFIG.N_TOOLSETS += 1

    _MSVC_CONFIG.VCVER_INSTALLED_SPECIFIC_VERSIONS.setdefault(key,[]).append(vc_instance)

    _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS.setdefault(vc_version,{}).setdefault(key,[]).append(vc_instance)

    if vc_product != vc_version:
        _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS.setdefault(vc_product,{}).setdefault(key,[]).append(vc_instance)

    vc_vernum = get_msvc_version_numeric(vc_version)
    if vc_vernum != vc_version:
        _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS.setdefault(vc_vernum,{}).setdefault(key,[]).append(vc_instance)

    if vc_version not in _MSVC_CONFIG.VCVER_VERSION_LIST:
        _MSVC_CONFIG.VCVER_VERSION_LIST.append(vc_version)

    if vc_version_numeric not in _MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST:
        _MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST.append(vc_version_numeric)

    if vc_rank not in _MSVC_CONFIG.VCVER_NUMERIC_COMPONENT_LIST:
        _MSVC_CONFIG.VCVER_NUMERIC_COMPONENT_LIST.append(vc_rank)

def _find_all_cl_in_vc_dir(msvc_instance):

    is_express = False
    is_win64 = common.is_win64()

    vc_product = msvc_instance['msvc_product']

    vc_version = msvc_instance['msvc_version']
    vc_version_numeric = float(get_msvc_version_numeric(vc_version))

    vc_dir = msvc_instance['installationPath']
    vc_rank = msvc_instance['component_rank']

    # building with Express is a special case

    if vc_rank == _MSVC_CONFIG.MSVC_RANK_EXPRESS:
        is_express = True

    # building with 14.0 via 2017+ vcvars_ver=14.0 is a special case

    # expected file location: VC_DIR\Common7\Tools\vsdevcmd\ext\vcvars\vcvars140.bat
    vc_vcvars140 = os.path.join(vc_dir, 'Common7', 'Tools', 'vsdevcmd', 'ext', 'vcvars', 'vcvars140.bat')
    if os.path.exists(vc_vcvars140):

        if vc_version_numeric not in _MSVC_CONFIG.VCVER_VCVARS140_NUMERIC_VERSION_LIST:
            _MSVC_CONFIG.VCVER_VCVARS140_NUMERIC_VERSION_LIST.append(vc_version_numeric)

        if vc_product not in _MSVC_CONFIG.VCVER_VCVARS140_PRODUCT_LIST:
            _MSVC_CONFIG.VCVER_VCVARS140_PRODUCT_LIST.append(vc_product)

    # expected folder structure: VC_DIR\VC\Tools\MSVC\XX.XX.XXXXX\bin\HOST\TARGET\cl.exe
    vc_msvc_path = os.path.join(vc_dir, 'VC', 'Tools', 'MSVC')
    for vc_specific_version in os.listdir(vc_msvc_path):

        vc_tool_path = os.path.join(vc_msvc_path, vc_specific_version)
        if not os.path.isdir(vc_tool_path): continue

        # folder structure: VC_DIR\VC\Tools\MSVC\XX.XX.XXXXX
        debug('vc_specific_version: ' + vc_specific_version)

        vc_bin_path = os.path.join(vc_tool_path, 'bin')
        if not os.path.exists(vc_bin_path): continue

        for vc_host_dir in os.listdir(vc_bin_path):
            vc_host_path = os.path.join(vc_bin_path, vc_host_dir)
            if not os.path.isdir(vc_host_path): continue

            # folder structure: VC_DIR\VC\Tools\MSVC\XX.XX.XXXXX\bin\HOST
            debug('vc_host_dir: ' + vc_host_dir)

            vc_host_key = vc_host_dir.lower()

            if is_express:
                # remap express host folder on win64
                key = (vc_host_key, is_win64)
                vc_host_key = _MSVC_EXPRESS_HOSTNAME_ISWIN64_RENAMEHOST_GT14.get(key, vc_host_key)

            # only process folders for the current host platform
            key = (vc_host_key, is_win64)
            if not _MSVC_HOSTNAME_ISWIN64_PROCESS_TARGETS_GT14.get(key, False):
                continue

            for vc_target_dir in os.listdir(vc_host_path):

                vc_target_path = os.path.join(vc_host_path, vc_target_dir)
                if not os.path.isdir(vc_target_path): continue

                # folder structure: VC_DIR\VC\Tools\MSVC\XX.XX.XXXXX\bin\HOST\TARGET
                debug('vc_target_dir: ' + vc_target_dir)

                cl_tool_path = os.path.join(vc_target_path, _CL_EXE_NAME)
                if not os.path.exists(cl_tool_path): continue

                vc_target_key = vc_target_dir.lower()

                # map directory names to specication names
                vc_host_spec = _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_GT14[vc_host_key]
                vc_target_spec = _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_GT14[vc_target_key]

                # folder structure: VC_DIR\VC\Tools\MSVC\XX.XX.XXXXX\bin\HOST\TARGET\cl.exe
                debug('found cl.exe: %s\\%s\\%s (%s, %s, %s)' % (
                    vc_specific_version, vc_host_dir, vc_target_dir, 
                    vc_specific_version, vc_host_spec, vc_target_spec)
                )

                # key for (host,target) combination
                key = (vc_host_spec, vc_target_spec)

                # register specific version for target specification (host,target)
                _register_host_target_toolset(key, vc_specific_version, vc_version_numeric, vc_rank, vc_version, vc_product)


    return

def _register_msvc_instances_in_vswhere_json(vswhere_output):

    msvc_instances = []

    for instance in vswhere_output:

        productId = instance.get('productId','')
        if not productId:
            debug('productId not found in vswhere output')
            continue

        installationPath = instance.get('installationPath','')
        if not installationPath:
            debug('installationPath not found in vswhere output')
            continue

        installationVersion = instance.get('installationVersion','')
        if not installationVersion:
            debug('installationVersion not found in vswhere output')
            continue

        major = installationVersion.split('.')[0]
        try:
            msvc_vernum = _MSVC_CONFIG.MSVS_MAJORVERSION_TO_VCVER[major]
        except KeyError:
            debug("Unknown version of msvs: %s" % installationVersion)
            # TODO|JCB new exception type: MSVSProductUnknown?
            raise UnsupportedVersion("Unknown msvs version %s" % installationVersion)

        componentId = productId.split('.')[-1]
        if componentId not in _MSVC_PRODUCTVERSION_COMPONENTIDS[msvc_vernum]['Products']:
            debug('ignore componentId:%s' % componentId)
            continue

        component_rank = _MSVC_COMPONENTID_SELECTION_RANKING.get(componentId,0)
        if component_rank == 0:
            debug('unknown componentId:%s' % componentId)
            continue

        msvc_version = msvc_vernum
        msvc_product = msvc_version + _MSVC_COMPONENTID_VERSIONSUFFIX[componentId]

        if msvc_product in _VCVER:
            msvc_version = msvc_product

        if _MSVC_CONFIG.TESTING_IGNORE_INSTALLED_PRODUCT:
            if msvc_product in _MSVC_CONFIG.TESTING_IGNORE_INSTALLED_PRODUCTS:
                debug('ignoring product: ' + msvc_product)
                continue

        d = {
            'msvc_version' : msvc_version,
            'msvc_version_numeric' : msvc_vernum,
            'msvc_product' : msvc_product,
            'productId' : productId,
            'installationPath': installationPath,
            'componentId' : componentId,
            'component_rank' : component_rank,
        }

        debug('found msvc instance:(%s,%s)' % (productId, msvc_version))

        _MSVC_CONFIG.N_PRODUCTS += 1

        _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES_UNIQUE.setdefault(msvc_version,[]).append(d)

        _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.setdefault(msvc_version,[]).append(d)

        if msvc_product != msvc_version:
            # synthetic version number (e.g., 14.2Ent, 14.2Pro, 14.2Com, 14.2BT) needed when looking up vc_dir
            debug('found specific msvc instance:(%s,%s)' % (productId, msvc_product))
            _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.setdefault(msvc_product,[]).append(d)
        else:
            # Known products (e.g., 14.1Exp) are not entered in the "bare" version number list
            # due to vc_dir lookup when walking _VCVER list.
            # Extended version support will use the "fully qualified" product type list.
            pass

        msvc_instances.append(d)

    for version, instances in _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES_UNIQUE.items():
        if len(instances):
            # sort multiple instances remaining based on productId priority: largest rank to smallest rank
            _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES_UNIQUE[version] = sorted(instances, key = lambda x: x['component_rank'], reverse=True)

    for version, instances in _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.items():
        if len(instances):
            # sort multiple instances remaining based on productId priority: largest rank to smallest rank
            _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES[version] = sorted(instances, key = lambda x: x['component_rank'], reverse=True)

    return msvc_instances

def _vswhere_get_all_products(env):

    vswhere_args = ['-products', '*']
    vswhere_json = call_vswhere_json_output(vswhere_args, env)

    if vswhere_json is None:
        return 0

    msvc_instances = _register_msvc_instances_in_vswhere_json(vswhere_json)
    debug("number of vswhere msvc instances:%d" % len(msvc_instances))
    return len(msvc_instances)

def _find_all_cl_in_vc140_dir(vc_dir):

    installed = False

    vc_bin_path = os.path.join(vc_dir, 'bin')
    if not os.path.exists(vc_bin_path): return installed

    # synthetic legacy entry
    vc_specific_version = '14.00.00000'
    vc_version_numeric = 14.0
    vc_rank = _MSVC_CONFIG.MSVC_RANK_LEGACY
    vc_version = '14.0'
    vc_product = '14.0'
    vc_vcvarsver = '14.0'

    # check root (bin/) and leaf folders (e.g., bin/amd64)
    for cl_dir in [''] + os.listdir(vc_bin_path):

        cl_tool_path = os.path.join(vc_bin_path, cl_dir, _CL_EXE_NAME)
        if not os.path.exists(cl_tool_path): continue

        cl_key = cl_dir.lower()

        try:
            vc_host_spec, vc_target_spec = _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_EQ14[cl_key]
        except KeyError:
            continue

        # key for (host,target)
        key = (vc_host_spec, vc_target_spec)

        # register specific version for target specification (host,target)
        _register_host_target_toolset(key, vc_specific_version, vc_version_numeric, vc_rank, vc_version, vc_product, vcvars_ver=vc_vcvarsver)

        installed = True

    return installed 

def _registry_get_140_product(env):

    # vcvars140.bat compatible registry queries:
    #   HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\SxS\VC7 /v "14.0"
    #   HKLM\SOFTWARE\Microsoft\VisualStudio\SxS\VC7 /v "14.0"

    vc140_dir = None

    for vcvars140bat_key in (
        r'Software\WOW6432Node\Microsoft\VisualStudio\SxS\VC7\14.0',
        r'Software\Microsoft\VisualStudio\SxS\VC7\14.0',
    ):
        try:
            vc140_dir = common.read_reg(vcvars140bat_key, SCons.Util.HKEY_LOCAL_MACHINE)
            break
        except SCons.Util.WinError:
            # TODO|JCB: debug log error
            pass

    if not vc140_dir or not os.path.exists(vc140_dir):
        return False

    installed = _find_all_cl_in_vc140_dir(vc140_dir)

    return installed

def _display_msvc_toolset(env, version=None, label='environment'):

    version_env = env.get('MSVC_VERSION', None)

    if version is not None and version != version_env:
        version_arg = ' <%s>' % version
    else:
        version_arg = ''

    print("", file=sys.stderr)
    print("%s:" % label, file=sys.stderr)

    indent = " " * _MSVC_CONFIG.TESTING_DISPLAY_INDENT_NSPACES
    print("%sMSVC_VERSION: %s%s" % (indent, version_env, version_arg), file=sys.stderr)
    print("%sMSVC_TOOLSET:" % indent, file=sys.stderr)

    msvc_toolset = env.get('MSVC_TOOLSET', None)
    if not msvc_toolset: return

    indent += indent
    for key, val in msvc_toolset.items():
        print("%s%s: %s" % (indent, key, val), file=sys.stderr)

def _display_installed_vctoolsets():

    indent = " " * _MSVC_CONFIG.TESTING_DISPLAY_INDENT_NSPACES

    print("", file=sys.stderr)
    print("MSVC_INSTALLED_ANY: %s" % _MSVC_CONFIG.MSVC_INSTALLED_ANY, file=sys.stderr)
    print("MSVC_INSTALLED_140: %s" % _MSVC_CONFIG.MSVC_INSTALLED_140, file=sys.stderr)

    print("", file=sys.stderr)
    print("NUMERIC_VER: %s" % repr(_MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST), file=sys.stderr)
    print("NUMERIC_140: %s" % repr(_MSVC_CONFIG.VCVER_VCVARS140_NUMERIC_VERSION_LIST), file=sys.stderr)

    print("", file=sys.stderr)
    print("N_PRODUCTS: %d" % _MSVC_CONFIG.N_PRODUCTS, file=sys.stderr)
    print("N_TOOLSETS: %d" % _MSVC_CONFIG.N_TOOLSETS, file=sys.stderr)

    print("", file=sys.stderr)
    print("BEG VSWHERE PRODUCTS", file=sys.stderr)
    products = _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES.items()
    products = sorted(products)
    for vc_product, msvc_instances in products:
        print("", file=sys.stderr)
        print("%sBEG PRODUCT %s" % (indent, vc_product), file=sys.stderr)
        for d in msvc_instances:
            print("%sINSTANCE  %-7s %s %2d %-7s %-12s %s" % ( 
                indent*2,
                d['msvc_product'],
                d['msvc_version_numeric'],
                d['component_rank'],
                d['msvc_version'],
                d['componentId'],
                d['installationPath']), 
            file=sys.stderr)
        print("%sEND PRODUCT" % indent, file=sys.stderr)
    print("", file=sys.stderr)
    print("END VSWHERE PRODUCTS", file=sys.stderr)

    print("", file=sys.stderr)
    print("BEG INSTALLED VCTOOLSETS", file=sys.stderr)
    for vc_target_spec, vc_toolsets in _MSVC_CONFIG.VCVER_INSTALLED_SPECIFIC_VERSIONS.items():
        print("", file=sys.stderr)
        print("%sBEG TARGET %s" % (indent, repr(vc_target_spec)), file=sys.stderr)
        for d in vc_toolsets:
            print(
                "%sTOOLSET  %s %s %2d %-7s %-7s %s" % (
                indent*2,
                d['msvc_specific_version'],
                d['msvc_version_numeric'],
                d['msvc_component_rank'],
                d['msvc_version'],
                d['msvc_product'],
                d['vcvars_ver']),
            file=sys.stderr)
        print("%sEND TARGET" % indent, file=sys.stderr)
    print("", file=sys.stderr)
    print("END INSTALLED VCTOOLSETS", file=sys.stderr)

    print("", file=sys.stderr)
    print("BEG VERSION VCTOOLSETS", file=sys.stderr)
    versions = _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS.items()
    versions = sorted(versions)
    for msvc_version, vc_d in versions:
        print("", file=sys.stderr)
        print("%sBEG MSVC VERSION %s" % (indent, msvc_version), file=sys.stderr)
        for vc_target_spec, vc_toolsets in vc_d.items():
            print("", file=sys.stderr)
            print("%sBEG TARGET %s %s" % (indent*2, msvc_version,repr(vc_target_spec)), file=sys.stderr)
            for d in vc_toolsets:
                print(
                    "%sTOOLSET  %s %s %2d %-7s %-7s %s" % (
                    indent*3,
                    d['msvc_specific_version'],
                    d['msvc_version_numeric'],
                    d['msvc_component_rank'],
                    d['msvc_version'],
                    d['msvc_product'],
                    d['vcvars_ver']),
                file=sys.stderr)
            print("%sEND TARGET" % (indent*2,), file=sys.stderr)
        print("", file=sys.stderr)
        print("%sEND MSVC VERSION" % indent, file=sys.stderr)
    print("", file=sys.stderr)
    print("END VERSION VCTOOLSETS", file=sys.stderr)

def _setup_internal_vctoolsets():

    if _MSVC_CONFIG.INTERNAL_SETUP_RUN_ONCE:
        return

    # map msvc host/target directory names to (host,target) specification names
    for vc_target_pair, vc_dir in _HOST_TARGET_TO_CL_DIR.items():
        # case insensitive store and lookup
        _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_EQ14[vc_dir.lower()] = vc_target_pair

    # map msvc host/target directory names to (host,target) specification names
    for vc_target_pair, vc_dir_pair in _HOST_TARGET_TO_CL_DIR_GREATER_THAN_14.items():
        # case insensitive store and lookup
        _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_GT14[vc_dir_pair[0].lower()] = vc_target_pair[0]
        _MSVC_CONFIG.HOST_DIRNAME_TO_HOST_TARGETNAME_GT14[vc_dir_pair[1].lower()] = vc_target_pair[1]

    # map product version suffix to component id
    for componentid, versionsuffix in _MSVC_COMPONENTID_VERSIONSUFFIX.items():
        _MSVC_CONFIG.MSVC_VERSIONSUFFIX_COMPONENTID[versionsuffix] = componentid

    for vcver, d in _MSVC_PRODUCTVERSION_COMPONENTIDS.items():

        if vcver not in _MSVC_CONFIG.MSVC_VCVER_EXTENDED:
            _MSVC_CONFIG.MSVC_VCVER_EXTENDED.append(vcver)

        for componentid in d['Products']:

            versionsuffix = _MSVC_COMPONENTID_VERSIONSUFFIX[componentid]
            vcver_symbol = vcver + versionsuffix

            _MSVC_CONFIG.MSVS_MAJORVERSION_TO_VCVER[d['MSVS_MAJOR']] = vcver

            if vcver_symbol not in _VCVER:
                if vcver_symbol not in _MSVC_CONFIG.MSVC_VCVER_SYNTHETIC:
                    _MSVC_CONFIG.MSVC_VCVER_SYNTHETIC.append(vcver_symbol)

            if vcver_symbol not in _MSVC_CONFIG.MSVC_VCVER_EXTENDED:
                _MSVC_CONFIG.MSVC_VCVER_EXTENDED.append(vcver_symbol)

    _MSVC_CONFIG.INTERNAL_SETUP_RUN_ONCE = True
    return

def prepare_installed_vctoolsets(env, get_installed_vcs=False):

    # ignore toolset lookups when finding default environments
    if get_installed_vcs:
        _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_DEFAULT = True

    if _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_PREPARED:
        return

    if not _MSVC_CONFIG.INTERNAL_SETUP_RUN_ONCE:
        _setup_internal_vctoolsets()

    _MSVC_CONFIG.MSVC_INSTALLED_ANY = _vswhere_get_all_products(env) > 0
    _MSVC_CONFIG.MSVC_INSTALLED_140 = _registry_get_140_product(env)

    # process all of the msvc toolsets
    for version, instances in _MSVC_CONFIG.MSVC_VSWHERE_INSTANCES_UNIQUE.items():
        for msvc_instance in instances:
            _find_all_cl_in_vc_dir(msvc_instance)

    # sort the global toolset target lists
    for vc_target_spec, vc_toolsets in _MSVC_CONFIG.VCVER_INSTALLED_SPECIFIC_VERSIONS.items():
        # search order: toolset version, product numeric version, product type
        vc_toolsets = sorted(vc_toolsets, key = lambda x: (x['msvc_specific_version'],x['msvc_version_numeric'],x['msvc_component_rank']), reverse=True)
        _MSVC_CONFIG.VCVER_INSTALLED_SPECIFIC_VERSIONS[vc_target_spec] = vc_toolsets

    # sort the version toolset target lists
    for msvc_version, d in _MSVC_CONFIG.VCVER_VERSION_SPECIFIC_VERSIONS.items():
        for vc_target_spec, vc_toolsets in d.items():
            # search order: toolset version, product numeric version, product type
            vc_toolsets = sorted(vc_toolsets, key = lambda x: (x['msvc_specific_version'],x['msvc_version_numeric'],x['msvc_component_rank']), reverse=True)
            d[vc_target_spec] = vc_toolsets

    # sort the version numbers seen
    _MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST = sorted(_MSVC_CONFIG.VCVER_NUMERIC_VERSION_LIST, reverse=True)
    _MSVC_CONFIG.VCVER_VCVARS140_NUMERIC_VERSION_LIST = sorted(_MSVC_CONFIG.VCVER_VCVARS140_NUMERIC_VERSION_LIST, reverse=True)

    # internal testing and debugging
    if _MSVC_CONFIG.TESTING_DISPLAY_TOOLSET_TABLES:
        _display_installed_vctoolsets()

    _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_PREPARED = True
    return

def setup_installed_vctoolsets(env):

    if not _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_PREPARED:
        prepare_installed_vctoolsets(env)

    _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_DEFAULT = False

    _MSVC_CONFIG.VCVER_INSTALLED_TOOLSETS_SETUP = True

def reset_installed_vctoolsets():

    _MSVC_CONFIG.reset_installed()

# Dispatch to experimental code or classic code.
# Allows existing tests to work without changes.

if _MSVC_EXPERIMENTAL_ACTIVE:
    find_vc_pdir_vswhere = find_vc_pdir_vswhere_instance
    find_vc_pdir         = find_vc_pdir_specific
else:
    find_vc_pdir_vswhere = find_vc_pdir_vswhere_classic
    find_vc_pdir         = find_vc_pdir_classic

