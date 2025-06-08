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
Common helper functions for working with the Microsoft tool chain.
"""

import base64
import copy
import hashlib
import json
import os
import re
import sys
import time
from collections import namedtuple
from contextlib import suppress
from subprocess import DEVNULL, PIPE
from pathlib import Path

import SCons.Errors
import SCons.Util
import SCons.Warnings


# TODO:  Hard-coded list of the variables that (may) need to be
# imported from os.environ[] for the chain of development batch
# files to execute correctly. One call to vcvars*.bat may
# end up running a dozen or more scripts, changes not only with
# each release but with what is installed at the time. We think
# in modern installations most are set along the way and don't
# need to be picked from the env, but include these for safety's sake.
# Any VSCMD variables definitely are picked from the env and
# control execution in interesting ways.
# Note these really should be unified - either controlled by vs.py,
# or synced with the the common_tools_var # settings in vs.py.
MSVC_ENVIRON_SHELLVARS = (
    'COMSPEC',  # path to "shell"
    'OS', # name of OS family: Windows_NT or undefined (95/98/ME)
    'VS170COMNTOOLS',  # path to common tools for given version
    'VS160COMNTOOLS',
    'VS150COMNTOOLS',
    'VS140COMNTOOLS',
    'VS120COMNTOOLS',
    'VS110COMNTOOLS',
    'VS100COMNTOOLS',
    'VS90COMNTOOLS',
    'VS80COMNTOOLS',
    'VS71COMNTOOLS',
    'VSCOMNTOOLS',
    'MSDevDir',
    'VSCMD_DEBUG',   # enable logging and other debug aids
    'VSCMD_SKIP_SENDTELEMETRY',
    'windir', # windows directory (SystemRoot not available in 95/98/ME)
    'VCPKG_DISABLE_METRICS',
    'VCPKG_ROOT',
    'POWERSHELL_TELEMETRY_OPTOUT',
    'PSDisableModuleAnalysisCacheCleanup',
    'PSModuleAnalysisCachePath',
)

# Hard-coded list of the variables that are imported from the msvc
# environment and added to the calling environment.  Currently, this
# list does not contain any variables that are in the shell variables
# list above.  Due to the existing implementation, variables in both
# lists may not work as expected (e.g., overwites, adding empty values,
# etc.).
MSVC_ENVIRON_KEEPVARS = (
    "INCLUDE",
    "LIB",
    "LIBPATH",
    "PATH",
    "VSCMD_ARG_app_plat",
    "VCINSTALLDIR",  # needed by clang -VS 2017 and newer
    "VCToolsInstallDir",  # needed by clang - VS 2015 and older
)

class MSVCCacheInvalidWarning(SCons.Warnings.WarningOnByDefault):
    pass

def _check_logfile(logfile):
    if logfile and '"' in logfile:
        err_msg = (
            "SCONS_MSCOMMON_DEBUG value contains double quote character(s)\n"
            f"  SCONS_MSCOMMON_DEBUG={logfile}"
        )
        raise SCons.Errors.UserError(err_msg)
    return logfile

# SCONS_MSCOMMON_DEBUG is internal-use so undocumented:
# set to '-' to print to console, else set to filename to log to
LOGFILE = _check_logfile(os.environ.get('SCONS_MSCOMMON_DEBUG'))
if LOGFILE:
    import logging

    class _Debug_Filter(logging.Filter):
        # custom filter for module relative filename

        modulelist = (
            # root module and parent/root module
            'MSCommon', 'Tool',
            # python library and below: correct iff scons does not have a lib folder
            'lib',
            # scons modules
            'SCons', 'test', 'scons'
        )

        def get_relative_filename(self, filename, module_list):
            if not filename:
                return filename
            for module in module_list:
                try:
                    ind = filename.rindex(module)
                    return filename[ind:]
                except ValueError:
                    pass
            return filename

        def filter(self, record) -> bool:
            relfilename = self.get_relative_filename(record.pathname, self.modulelist)
            relfilename = relfilename.replace('\\', '/')
            record.relfilename = relfilename
            return True

    class _CustomFormatter(logging.Formatter):

        # Log format looks like:
        #   00109ms:MSCommon/vc.py:find_vc_pdir#447: VC found '14.3'        [file]
        #   debug: 00109ms:MSCommon/vc.py:find_vc_pdir#447: VC found '14.3' [stdout]

        log_format=(
            '%(relativeCreated)05dms'
            ':%(relfilename)s'
            ':%(funcName)s'
            '#%(lineno)s'
            ': %(message)s'
        )

        log_format_classname=(
            '%(relativeCreated)05dms'
            ':%(relfilename)s'
            ':%(classname)s'
            '.%(funcName)s'
            '#%(lineno)s'
            ': %(message)s'
        )

        def __init__(self, log_prefix):
            super().__init__()
            if log_prefix:
                self.log_format = log_prefix + self.log_format
                self.log_format_classname = log_prefix + self.log_format_classname
            log_record = logging.LogRecord(
                '',    # name (str)
                0,     # level (int)
                '',    # pathname (str)
                0,     # lineno (int)
                None,  # msg (Any)
                {},    # args (tuple | dict[str, Any])
                None   # exc_info (tuple[type[BaseException], BaseException, types.TracebackType] | None)
            )
            self.default_attrs = set(log_record.__dict__.keys())
            self.default_attrs.add('relfilename')

        def format(self, record):
            extras = set(record.__dict__.keys()) - self.default_attrs
            if 'classname' in extras:
                log_format = self.log_format_classname
            else:
                log_format = self.log_format
            formatter = logging.Formatter(log_format)
            return formatter.format(record)

    if LOGFILE == '-':
        log_prefix = 'debug: '
        log_handler = logging.StreamHandler(sys.stdout)
    else:
        log_prefix = ''
        try:
            log_handler = logging.FileHandler(filename=LOGFILE)
        except (OSError, FileNotFoundError) as e:
            err_msg = (
                "Could not create logfile, check SCONS_MSCOMMON_DEBUG\n"
                f"  SCONS_MSCOMMON_DEBUG={LOGFILE}\n"
                f"  {e.__class__.__name__}: {str(e)}"
            )
            raise SCons.Errors.UserError(err_msg)
    log_formatter = _CustomFormatter(log_prefix)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger(name=__name__)
    logger.setLevel(level=logging.DEBUG)
    logger.addHandler(log_handler)
    logger.addFilter(_Debug_Filter())
    debug = logger.debug

    def debug_extra(cls=None):
        if cls:
            extra = {'classname': cls.__qualname__}
        else:
            extra = None
        return extra

    DEBUG_ENABLED = True

else:
    def debug(x, *args, **kwargs):
        return None

    def debug_extra(*args, **kwargs):
        return None

    DEBUG_ENABLED = False

# SCONS_CACHE_MSVC_CONFIG is public, and is documented.
CONFIG_CACHE = os.environ.get('SCONS_CACHE_MSVC_CONFIG', '')
if CONFIG_CACHE in ('1', 'true', 'True'):
    CONFIG_CACHE = os.path.join(os.path.expanduser('~'), 'scons_msvc_cache.json')

# SCONS_CACHE_MSVC_FORCE_DEFAULTS is internal-use so undocumented.
CONFIG_CACHE_FORCE_DEFAULT_ARGUMENTS = False
if CONFIG_CACHE:
    if os.environ.get('SCONS_CACHE_MSVC_FORCE_DEFAULTS') in ('1', 'true', 'True'):
        CONFIG_CACHE_FORCE_DEFAULT_ARGUMENTS = True

# Cache file version number:
# * bump the file version up every time the structure of the file changes
#   so that exising cache files are reconstructed.
_CACHE_FILE_VERSION = 1
_CACHE_RECORD_VERSION = 0

def register_cache_record_version(record_version) -> None:
    global _CACHE_RECORD_VERSION
    _CACHE_RECORD_VERSION=record_version

_CacheHeader = namedtuple('_CacheHeader', [
    'file_version',
    'record_version',
])


def read_script_env_cache() -> dict:
    """ fetch cached msvc env vars if requested, else return empty dict """
    envcache = {}
    p = Path(CONFIG_CACHE)
    if not CONFIG_CACHE or not p.is_file():
        return envcache

    envcache_dict = {}
    with SCons.Util.FileLock(CONFIG_CACHE, timeout=5, writer=False), p.open('r') as f:
        # Convert the list of cache entry dictionaries read from
        # json to the cache dictionary. Reconstruct the cache key
        # tuple from the key list written to json.
        # Note we need to take a write lock on the cachefile, as if there's
        # an error and we try to remove it, that's "writing" on Windows.
        try:
            envcache_dict = json.load(f)
        except json.JSONDecodeError:
            # If we couldn't decode it, it could be corrupt. Toss.
            with suppress(FileNotFoundError):
                p.unlink()
            warn_msg = "Could not decode msvc cache file %s: dropping."
            SCons.Warnings.warn(MSVCCacheInvalidWarning, warn_msg % CONFIG_CACHE)
            debug(warn_msg, CONFIG_CACHE)
            return envcache

    is_valid = False
    do_once = True
    while do_once:
        do_once = False
        if not isinstance(envcache_dict, dict):
            break
        envcache_header = envcache_dict.get("header")
        if not isinstance(envcache_header, dict):
            break
        try:
            envcache_header_t = _CacheHeader(**envcache_header)
        except TypeError:
            break
        if envcache_header_t.file_version != _CACHE_FILE_VERSION:
            break
        if envcache_header_t.record_version != _CACHE_RECORD_VERSION:
            break
        envcache_records = envcache_dict.get("records")
        if not isinstance(envcache_records, list):
            break
        is_valid = True
        envcache = {
            tuple(d['key']): d['val'] for d in envcache_records
        }

    if not is_valid:
        # don't fail if incompatible format, just proceed without it
        warn_msg = "Incompatible format for msvc cache file %s: file may be overwritten."
        SCons.Warnings.warn(MSVCCacheInvalidWarning, warn_msg % CONFIG_CACHE)
        debug(warn_msg, CONFIG_CACHE)

    return envcache


def write_script_env_cache(cache) -> None:
    """ write out cache of msvc env vars if requested """
    if not CONFIG_CACHE:
        return

    cache_header = _CacheHeader(
        file_version=_CACHE_FILE_VERSION,
        record_version=_CACHE_RECORD_VERSION,
    )

    p = Path(CONFIG_CACHE)
    try:
        with SCons.Util.FileLock(CONFIG_CACHE, timeout=5, writer=True), p.open('w') as f:
            # Convert the cache dictionary to a list of cache entry
            # dictionaries. The cache key is converted from a tuple to
            # a list for compatibility with json.
            envcache_dict = {
                'header':  cache_header._asdict(),
                'records': [
                    {'key': list(key), 'val': val._asdict()}
                    for key, val in cache.items()
                ],
            }
            json.dump(envcache_dict, f, indent=2)
    except TypeError:
        # data can't serialize to json, don't leave partial file
        with suppress(FileNotFoundError):
            p.unlink()
    except OSError:
        # can't write the file, just skip
        pass

    return


_is_win64 = None


def is_win64() -> bool:
    """Return true if running on windows 64 bits.

    Works whether python itself runs in 64 bits or 32 bits."""
    # Unfortunately, python does not provide a useful way to determine
    # if the underlying Windows OS is 32-bit or 64-bit.  Worse, whether
    # the Python itself is 32-bit or 64-bit affects what it returns,
    # so nothing in sys.* or os.* help.

    # Apparently the best solution is to use env vars that Windows
    # sets.  If PROCESSOR_ARCHITECTURE is not x86, then the python
    # process is running in 64 bit mode (on a 64-bit OS, 64-bit
    # hardware, obviously).
    # If this python is 32-bit but the OS is 64, Windows will set
    # ProgramW6432 and PROCESSOR_ARCHITEW6432 to non-null.
    # (Checking for HKLM\Software\Wow6432Node in the registry doesn't
    # work, because some 32-bit installers create it.)
    global _is_win64
    if _is_win64 is None:
        # I structured these tests to make it easy to add new ones or
        # add exceptions in the future, because this is a bit fragile.
        _is_win64 = False
        if os.environ.get('PROCESSOR_ARCHITECTURE', 'x86') != 'x86':
            _is_win64 = True
        if os.environ.get('PROCESSOR_ARCHITEW6432'):
            _is_win64 = True
        if os.environ.get('ProgramW6432'):
            _is_win64 = True
    return _is_win64


def read_reg(value, hkroot=SCons.Util.HKEY_LOCAL_MACHINE):
    return SCons.Util.RegGetValue(hkroot, value)[0]


def has_reg(value) -> bool:
    """Return True if the given key exists in HKEY_LOCAL_MACHINE."""
    try:
        SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE, value)
        ret = True
    except OSError:
        ret = False
    return ret

# Functions for shell variables and keep variables cache key.

class _EnvVarsUtil:

    _VarListEncode = namedtuple('_VarListEncode', [
        'n_elem',
        'n_char',
        'digest',
        'keystr',
    ])

    _cache_varlist_unique = {}

    @classmethod
    def varlist_unique_t(cls, varlist):
        key = tuple(varlist)
        unique = cls._cache_varlist_unique.get(key)
        if unique is None:
            seen = set()
            unique = []
            for var in varlist:
                var_key = var.lower()
                if var_key in seen:
                    continue
                seen.add(var_key)
                unique.append(var)
            unique = tuple(sorted(unique, key=str.lower))
            cls._cache_varlist_unique[key] = unique
        return unique

    _cache_varlist_norm = {}

    @classmethod
    def varlist_norm_t(cls, varlist):
        unique_t = cls.varlist_unique_t(varlist)
        norm_t = cls._cache_varlist_norm.get(unique_t)
        if norm_t is None:
            norm_t = tuple(var.lower() for var in unique_t)
            cls._cache_varlist_norm[unique_t] = norm_t
        return norm_t

    _cache_varlist_encode = {}

    @classmethod
    def varlist_encode(cls, varlist):
        norm_t = cls.varlist_norm_t(varlist)
        encode_t = cls._cache_varlist_encode.get(norm_t)
        if encode_t is None:
            message = ":".join(norm_t)
            hash_object = hashlib.sha224()
            hash_object.update(message.encode())
            digest = base64.b85encode(hash_object.digest()).decode("ascii")
            n_elem = len(norm_t)
            n_char = len(message)
            if n_elem > 1:
                n_char -= n_elem - 1
            encode_t = cls._VarListEncode(
                n_elem=n_elem,
                n_char=n_char,
                digest=digest,
                keystr=f'{n_elem}:{n_char}:{digest}',

            )
            cls._cache_varlist_encode[norm_t] = encode_t
        return encode_t

    _cache_msvc_environ_keys = {}

    @classmethod
    def msvc_environ_keys(cls):
        shell_encode_t = cls.varlist_encode(MSVC_ENVIRON_SHELLVARS)
        keep_encode_t = cls.varlist_encode(MSVC_ENVIRON_KEEPVARS)
        key = (shell_encode_t, keep_encode_t)
        keys = cls._cache_msvc_environ_keys.get(key)
        if not keys:
            keys = (shell_encode_t.keystr, keep_encode_t.keystr)
            cls._cache_msvc_environ_keys[key] = keys
        return keys

def msvc_environ_cache_keys():
    keys = _EnvVarsUtil.msvc_environ_keys()
    debug("keys=%r", keys)
    return keys

# Populate cache with default variable lists.
# Useful when logging to detect user modifications of default variable lists.
_ = msvc_environ_cache_keys()


# Functions for fetching environment variable settings from batch files.


def _force_vscmd_skip_sendtelemetry(env):

    if 'VSCMD_SKIP_SENDTELEMETRY' in env['ENV']:
        return False

    env['ENV']['VSCMD_SKIP_SENDTELEMETRY'] = '1'
    debug("force env['ENV']['VSCMD_SKIP_SENDTELEMETRY']=%s", env['ENV']['VSCMD_SKIP_SENDTELEMETRY'])

    return True


class _PathManager:

    _PSEXECUTABLES = (
        "pwsh.exe",
        "powershell.exe",
    )

    _PSMODULEPATH_MAP = {os.path.normcase(os.path.abspath(p)): p for p in [
        # os.path.expandvars(r"%USERPROFILE%\Documents\PowerShell\Modules"),  # current user
        os.path.expandvars(r"%ProgramFiles%\PowerShell\Modules"),  # all users
        os.path.expandvars(r"%ProgramFiles%\PowerShell\7\Modules"),  # installation location
        # os.path.expandvars(r"%USERPROFILE%\Documents\WindowsPowerShell\Modules"),  # current user
        os.path.expandvars(r"%ProgramFiles%\WindowsPowerShell\Modules"),  # all users
        os.path.expandvars(r"%windir%\System32\WindowsPowerShell\v1.0\Modules"),  # installation location
    ]}

    _cache_norm_path = {}

    @classmethod
    def _get_norm_path(cls, p):
        norm_path = cls._cache_norm_path.get(p)
        if norm_path is None:
            norm_path = os.path.normcase(os.path.abspath(p))
            cls._cache_norm_path[p] = norm_path
            cls._cache_norm_path[norm_path] = norm_path
        return norm_path

    _cache_is_psmodulepath = {}

    @classmethod
    def _is_psmodulepath(cls, p):
        is_psmodulepath = cls._cache_is_psmodulepath.get(p)
        if is_psmodulepath is None:
            norm_path = cls._get_norm_path(p)
            is_psmodulepath = bool(norm_path in cls._PSMODULEPATH_MAP)
            cls._cache_is_psmodulepath[p] = is_psmodulepath
            cls._cache_is_psmodulepath[norm_path] = is_psmodulepath
        return is_psmodulepath

    _cache_psmodulepath_paths = {}

    @classmethod
    def get_psmodulepath_paths(cls, pathspec):
        psmodulepath_paths = cls._cache_psmodulepath_paths.get(pathspec)
        if psmodulepath_paths is None:
            psmodulepath_paths = []
            for p in pathspec.split(os.pathsep):
                p = p.strip()
                if not p:
                    continue
                if not cls._is_psmodulepath(p):
                    continue
                psmodulepath_paths.append(p)
            psmodulepath_paths = tuple(psmodulepath_paths)
            cls._cache_psmodulepath_paths[pathspec] = psmodulepath_paths
        return psmodulepath_paths

    _cache_psexe_paths = {}

    @classmethod
    def get_psexe_paths(cls, pathspec):
        psexe_paths = cls._cache_psexe_paths.get(pathspec)
        if psexe_paths is None:
            psexe_set = set(cls._PSEXECUTABLES)
            psexe_paths = []
            for p in pathspec.split(os.pathsep):
                p = p.strip()
                if not p:
                    continue
                for psexe in psexe_set:
                    psexe_path = os.path.join(p, psexe)
                    if not os.path.exists(psexe_path):
                        continue
                    psexe_paths.append(p)
                    psexe_set.remove(psexe)
                    break
                if psexe_set:
                    continue
                break
            psexe_paths = tuple(psexe_paths)
            cls._cache_psexe_paths[pathspec] = psexe_paths
        return psexe_paths

    _cache_minimal_pathspec = {}

    @classmethod
    def get_minimal_pathspec(cls, pathlist):
        pathlist_t = tuple(pathlist)
        minimal_pathspec = cls._cache_minimal_pathspec.get(pathlist_t)
        if minimal_pathspec is None:
            minimal_paths = []
            seen = set()
            for p in pathlist:
                p = p.strip()
                if not p:
                    continue
                norm_path = cls._get_norm_path(p)
                if norm_path in seen:
                    continue
                seen.add(norm_path)
                minimal_paths.append(p)
            minimal_pathspec = os.pathsep.join(minimal_paths)
            cls._cache_minimal_pathspec[pathlist_t] = minimal_pathspec
        return minimal_pathspec


def normalize_env(env, keys, force: bool=False):
    """Given a dictionary representing a shell environment, add the variables
    from os.environ needed for the processing of .bat files; the keys are
    controlled by the keys argument.

    It also makes sure the environment values are correctly encoded.

    If force=True, then all of the key values that exist are copied
    into the returned dictionary.  If force=false, values are only
    copied if the key does not already exist in the copied dictionary.

    Note: the environment is copied."""
    normenv = {}
    if env:
        for k, v in env.items():
            normenv[k] = copy.deepcopy(v)

        for k in keys:
            if k in os.environ and (force or k not in normenv):
                normenv[k] = os.environ[k]
                debug("keys: normenv[%s]=%s", k, normenv[k])
            else:
                debug("keys: skipped[%s]", k)

    syspath_pathlist = normenv.get("PATH", "").split(os.pathsep)

    # add some things to PATH to prevent problems:
    # Shouldn't be necessary to add system32, since the default environment
    # should include it, but keep this here to be safe (needed for reg.exe)
    sys32_dir = os.path.join(
        os.environ.get("SystemRoot", os.environ.get("windir", r"C:\Windows")), "System32"
    )
    syspath_pathlist.append(sys32_dir)

    # Without Wbem in PATH, vcvarsall.bat has a "'wmic' is not recognized"
    # error starting with Visual Studio 2017, although the script still
    # seems to work anyway.
    sys32_wbem_dir = os.path.join(sys32_dir, 'Wbem')
    syspath_pathlist.append(sys32_wbem_dir)

    # Without Powershell in PATH, an internal call to a telemetry
    # function (starting with a VS2019 update) can fail
    # Note can also set VSCMD_SKIP_SENDTELEMETRY to avoid this.

    # Find the powershell executable paths.  Add the known powershell.exe
    # path to the end of the shell system path (just in case).
    # The VS vcpkg component prefers pwsh.exe if it's on the path.
    sys32_ps_dir = os.path.join(sys32_dir, 'WindowsPowerShell', 'v1.0')
    psexe_searchlist = os.pathsep.join([os.environ.get("PATH", ""), sys32_ps_dir])
    psexe_pathlist = _PathManager.get_psexe_paths(psexe_searchlist)

    # Add powershell executable paths in the order discovered.
    syspath_pathlist.extend(psexe_pathlist)

    normenv['PATH'] = _PathManager.get_minimal_pathspec(syspath_pathlist)
    debug("PATH: %s", normenv['PATH'])

    # Add psmodulepath paths in the order discovered.
    psmodulepath_pathlist = _PathManager.get_psmodulepath_paths(os.environ.get("PSModulePath", ""))
    if psmodulepath_pathlist:
        normenv["PSModulePath"] = _PathManager.get_minimal_pathspec(psmodulepath_pathlist)

    debug("PSModulePath: %s", normenv.get('PSModulePath',''))
    return normenv


def get_output(vcbat, args=None, env=None, skip_sendtelemetry=False):
    """Parse the output of given bat file, with given args."""

    if env is None:
        # Create a blank environment, for use in launching the tools
        env = SCons.Environment.Environment(tools=[])

    shellvars_t = _EnvVarsUtil.varlist_unique_t(MSVC_ENVIRON_SHELLVARS)

    env['ENV'] = normalize_env(env['ENV'], shellvars_t, force=False)

    if skip_sendtelemetry:
        _force_vscmd_skip_sendtelemetry(env)

    # debug("ENV=%r", env['ENV'])

    if args:
        debug("Calling '%s %s'", vcbat, args)
        cmd_str = '"%s" %s & set' % (vcbat, args)
    else:
        debug("Calling '%s'", vcbat)
        cmd_str = '"%s" & set' % vcbat

    beg_time = time.time()

    cp = SCons.Action.scons_subproc_run(
        env, cmd_str, stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
    )

    end_time = time.time()
    debug("Elapsed %.2fs", end_time - beg_time)

    # Extra debug logic, uncomment if necessary
    # debug('stdout:%s', cp.stdout)
    # debug('stderr:%s', cp.stderr)

    # Ongoing problems getting non-corrupted text led to this
    # changing to "oem" from "mbcs" - the scripts run presumably
    # attached to a console, so some particular rules apply.
    OEM = "oem"
    if cp.stderr:
        # TODO: find something better to do with stderr;
        # this at least prevents errors from getting swallowed.
        sys.stderr.write(cp.stderr.decode(OEM))
    if cp.returncode != 0:
        raise OSError(cp.stderr.decode(OEM))

    return cp.stdout.decode(OEM)


def parse_output(output, keep=None):
    """
    Parse output from running visual c++/studios vcvarsall.bat and running set
    To capture the values listed in keep
    """

    if keep is None:
        keep = MSVC_ENVIRON_KEEPVARS

    keep = _EnvVarsUtil.varlist_unique_t(keep)

    # dkeep is a dict associating key: path_list, where key is one item from
    # keep, and path_list the associated list of paths
    dkeep = {i: [] for i in keep}

    # rdk will  keep the regex to match the .bat file output line starts
    rdk = {}
    for i in keep:
        rdk[i] = re.compile(r'%s=(.*)' % i, re.I)

    def add_env(rmatch, key, dkeep=dkeep) -> None:
        path_list = rmatch.group(1).split(os.pathsep)
        for path in path_list:
            # Do not add empty paths (when a var ends with ;)
            if path:
                # XXX: For some reason, VC98 .bat file adds "" around the PATH
                # values, and it screws up the environment later, so we strip
                # it.
                path = path.strip('"')
                dkeep[key].append(str(path))
                debug("dkeep[%s].append(%r)", key, path)

    for line in output.splitlines():
        for k, value in rdk.items():
            match = value.match(line)
            if match:
                add_env(match, k)

    return dkeep

def get_pch_node(env, target, source):
    """
    Get the actual PCH file node
    """
    pch_subst = env.get('PCH', False) and env.subst('$PCH',target=target, source=source, conv=lambda x:x)

    if not pch_subst:
        return ""

    if SCons.Util.is_String(pch_subst):
        pch_subst = target[0].dir.File(pch_subst)

    return pch_subst


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
