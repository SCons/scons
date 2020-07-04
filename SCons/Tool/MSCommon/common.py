"""
Common helper functions for working with the Microsoft tool chain.
"""
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

import copy
import json
import os
import re
import subprocess
import sys
import glob

import SCons.Util

class _MSCOMMON_FILENAME:

    # Internal use only:
    #    SCONS_MSCOMMON_DEBUG=filename
    #    SCONS_MSCOMMON_TRACE=filename

    # Rewrite filename *ONLY* when the rootname ends in "-#":
    #    root, ext = splitext(filename) -> root[:-1] + NNNN + ext
    #    example: myfile-#.txt -> myfile-0001.txt
    #    next consecutive number from largest number in target folder or 1
    #    allows individual debug/trace file names for each launch of scons

    # Sync:
    #    debug sync=False: number for next debug file
    #    trace sync=True:  number set to debug number
    #    trace sync=False: number for next trace file

    FILENAME_SERIALNBR = '-#'
    FILENAME_NBRFORMAT = '%04d'

    _last_n = None

    @classmethod
    def _get_next_serialnbr(cls, fileglob):
        matches = glob.glob(fileglob)
        if not matches:
            return 1
        matches = sorted(matches)
        root, ext = os.path.splitext(matches[-1])
        n = int(root.split(cls.FILENAME_SERIALNBR[0])[-1])
        return n + 1

    @classmethod
    def _get_filename(cls, root, n, ext):
        filename = ''.join([root, cls.FILENAME_NBRFORMAT % n, ext])
        return filename

    @classmethod
    def rewrite(cls, filename, sync=False):
        if not filename:
            return filename
        root, ext = os.path.splitext(filename)
        if not root or root[-len(cls.FILENAME_SERIALNBR):] != cls.FILENAME_SERIALNBR:
            return filename
        root = root[:-1]
        if sync and cls._last_n is not None:
            n = cls._last_n
        else:
            fileglob = root + '*' + ext
            n = cls._get_next_serialnbr(fileglob)
            if not sync:
                cls._last_n = n
        filename = cls._get_filename(root, n, ext)
        return filename


# SCONS_MSCOMMON_DEBUG is internal-use so undocumented:
# set to '-' to print to console, else set to filename to log to
LOGFILE = os.environ.get('SCONS_MSCOMMON_DEBUG')
if LOGFILE == '-':
    def debug(message):
        print(message)
elif LOGFILE:
    import logging
    logging.basicConfig(
        # This looks like:
        #   00109ms:MSCommon/vc.py:find_vc_pdir#447:
        format=(
            '%(relativeCreated)05dms'
            ':MSCommon/%(filename)s'
            ':%(funcName)s'
            '#%(lineno)s'
            ':%(message)s: '
        ),
        filename=_MSCOMMON_FILENAME.rewrite(LOGFILE),
        level=logging.DEBUG)
    debug = logging.getLogger(name=__name__).debug
else:
    def debug(x): return None


# SCONS_CACHE_MSVC_CONFIG is public, and is documented.
CONFIG_CACHE = os.environ.get('SCONS_CACHE_MSVC_CONFIG')
if CONFIG_CACHE in ('1', 'true', 'True'):
    CONFIG_CACHE = os.path.join(os.path.expanduser('~'), '.scons_msvc_cache')


def read_script_env_cache():
    """ fetch cached msvc env vars if requested, else return empty dict """
    envcache = {}
    if CONFIG_CACHE:
        try:
            with open(CONFIG_CACHE, 'r') as f:
                envcache = json.load(f)
        except FileNotFoundError:
            # don't fail if no cache file, just proceed without it
            pass
    return envcache


def write_script_env_cache(cache):
    """ write out cache of msvc env vars if requested """
    if CONFIG_CACHE:
        try:
            with open(CONFIG_CACHE, 'w') as f:
                json.dump(cache, f, indent=2)
        except TypeError:
            # data can't serialize to json, don't leave partial file
            os.remove(CONFIG_CACHE)
        except IOError:
            # can't write the file, just skip
            pass


_is_win64 = None


def is_win64():
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


def has_reg(value):
    """Return True if the given key exists in HKEY_LOCAL_MACHINE, False
    otherwise."""
    try:
        SCons.Util.RegOpenKeyEx(SCons.Util.HKEY_LOCAL_MACHINE, value)
        ret = True
    except SCons.Util.WinError:
        ret = False
    return ret

# Functions for fetching environment variable settings from batch files.


def normalize_env(env, keys, force=False):
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

    # add some things to PATH to prevent problems:
    # Shouldn't be necessary to add system32, since the default environment
    # should include it, but keep this here to be safe (needed for reg.exe)
    sys32_dir = os.path.join(
        os.environ.get("SystemRoot", os.environ.get("windir", r"C:\Windows")), "System32"
)
    if sys32_dir not in normenv["PATH"]:
        normenv["PATH"] = normenv["PATH"] + os.pathsep + sys32_dir

    # Without Wbem in PATH, vcvarsall.bat has a "'wmic' is not recognized"
    # error starting with Visual Studio 2017, although the script still
    # seems to work anyway.
    sys32_wbem_dir = os.path.join(sys32_dir, 'Wbem')
    if sys32_wbem_dir not in normenv['PATH']:
        normenv['PATH'] = normenv['PATH'] + os.pathsep + sys32_wbem_dir

    # Without Powershell in PATH, an internal call to a telemetry
    # function (starting with a VS2019 update) can fail
    # Note can also set VSCMD_SKIP_SENDTELEMETRY to avoid this.
    sys32_ps_dir = os.path.join(sys32_dir, r'WindowsPowerShell\v1.0')
    if sys32_ps_dir not in normenv['PATH']:
        normenv['PATH'] = normenv['PATH'] + os.pathsep + sys32_ps_dir

    debug("PATH: %s" % normenv['PATH'])
    return normenv


def get_output(vcbat, args=None, env=None):
    """Parse the output of given bat file, with given args."""

    if env is None:
        # Create a blank environment, for use in launching the tools
        env = SCons.Environment.Environment(tools=[])

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
    vs_vc_vars = [
        'COMSPEC',  # path to "shell"
        'VS160COMNTOOLS',  # path to common tools for given version
        'VS150COMNTOOLS',
        'VS140COMNTOOLS',
        'VS120COMNTOOLS',
        'VS110COMNTOOLS',
        'VS100COMNTOOLS',
        'VS90COMNTOOLS',
        'VS80COMNTOOLS',
        'VS71COMNTOOLS',
        'VS70COMNTOOLS',
        'VS60COMNTOOLS',
        'VSCMD_DEBUG',   # enable logging and other debug aids
        'VSCMD_SKIP_SENDTELEMETRY',
    ]
    env['ENV'] = normalize_env(env['ENV'], vs_vc_vars, force=False)

    if args:
        debug("Calling '%s %s'" % (vcbat, args))
        popen = SCons.Action._subproc(env,
                                      '"%s" %s & set' % (vcbat, args),
                                      stdin='devnull',
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    else:
        debug("Calling '%s'" % vcbat)
        popen = SCons.Action._subproc(env,
                                      '"%s" & set' % vcbat,
                                      stdin='devnull',
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    # Use the .stdout and .stderr attributes directly because the
    # .communicate() method uses the threading module on Windows
    # and won't work under Pythons not built with threading.
    with popen.stdout:
        stdout = popen.stdout.read()
    with popen.stderr:
        stderr = popen.stderr.read()

    # Extra debug logic, uncomment if necessary
    # debug('stdout:%s' % stdout)
    # debug('stderr:%s' % stderr)

    # Ongoing problems getting non-corrupted text led to this
    # changing to "oem" from "mbcs" - the scripts run presumably
    # attached to a console, so some particular rules apply.
    # Unfortunately, "oem" not defined in Python 3.5, so get another way
    if sys.version_info.major == 3 and sys.version_info.minor < 6:
        from ctypes import windll

        OEM = "cp{}".format(windll.kernel32.GetConsoleOutputCP())
    else:
        OEM = "oem"
    if stderr:
        # TODO: find something better to do with stderr;
        # this at least prevents errors from getting swallowed.
        sys.stderr.write(stderr.decode(OEM))
    if popen.wait() != 0:
        raise IOError(stderr.decode(OEM))

    return stdout.decode(OEM)


KEEPLIST = (
    "INCLUDE",
    "LIB",
    "LIBPATH",
    "PATH",
    "VSCMD_ARG_app_plat",
    "VCINSTALLDIR",  # needed by clang -VS 2017 and newer
    "VCToolsInstallDir",  # needed by clang - VS 2015 and older
)


def parse_output(output, keep=KEEPLIST):
    """
    Parse output from running visual c++/studios vcvarsall.bat and running set
    To capture the values listed in keep
    """

    # dkeep is a dict associating key: path_list, where key is one item from
    # keep, and path_list the associated list of paths
    dkeep = dict([(i, []) for i in keep])

    # rdk will  keep the regex to match the .bat file output line starts
    rdk = {}
    for i in keep:
        rdk[i] = re.compile('%s=(.*)' % i, re.I)

    def add_env(rmatch, key, dkeep=dkeep):
        path_list = rmatch.group(1).split(os.pathsep)
        for path in path_list:
            # Do not add empty paths (when a var ends with ;)
            if path:
                # XXX: For some reason, VC98 .bat file adds "" around the PATH
                # values, and it screws up the environment later, so we strip
                # it.
                path = path.strip('"')
                dkeep[key].append(str(path))

    for line in output.splitlines():
        for k, value in rdk.items():
            match = value.match(line)
            if match:
                add_env(match, k)

    return dkeep


class _MSCOMMON_TRACE:

    # SCONS_MSCOMMON_TRACE is internal-use so undocumented:
    # set to '-' to print to stderr, else set to filename to log to
    TRACE_FILENAME = os.environ.get('SCONS_MSCOMMON_TRACE')

    # display the function argument list w/select values
    DISPLAY_FUNCTION_ARGLIST = True
    DISPLAY_FUNCTION_LOCATION = True

    # number of frames above the current module
    FRAME_CALLER_FRAMES = 5

    # when enabled, allow these external module/function calls (see debug below)
    FRAME_WHITELIST_ENABLED = False
    FRAME_WHITELIST_FUNCTIONS = [
    ]

    # when enabled, ignore these internal module/function calls (see debug below)
    FRAME_BLACKLIST_ENABLED = False
    FRAME_BLACKLIST_FUNCTIONS = [
    ]

    # debugging using the logging module
    DEBUG_LOGGING_ENABLED = True if LOGFILE and LOGFILE != "-" else False

    # keep extenal debug calls when using the logging module
    DEBUG_WHITELIST_ENABLED = DEBUG_LOGGING_ENABLED
    DEBUG_WHITELIST_FUNCTIONS = [
        ('logging', 'debug'),
    ]

    # ignore internal debug calls when not using the logging module
    DEBUG_BLACKLIST_ENABLED = not DEBUG_LOGGING_ENABLED
    DEBUG_BLACKLIST_FUNCTIONS = [
        ('common', 'debug'),
    ]

    # function argument values of interest
    FRAME_ARGUMENT_VALUES = (
        'version',
        'msvc_version',
        'value',
        'host_arch',
        'target_arch',
        'vc_specific_version',
        'vc_product',
        'search_version',
        'rollback',
    )

    # function call indentation
    FRAME_INDENT_NSPACES = 2
    FRAME_INDENT_LITERAL = " " * FRAME_INDENT_NSPACES

    # start of new call chain
    FRAME_ENTRY_DEPTH = 0
    FRAME_ENTRY_LOCATION = []
    FRAME_ENTRY_SLOT = -1

    # parent module of this script (e.g, MSCommon)
    PARENT_MODULE = __name__.split('.')[-2]

    # trace file processing

    TRACE_ENABLED = False
    TRACE_FH = None

    if TRACE_FILENAME == '-':
        TRACE_ENABLED = True
        TRACE_FH = sys.stderr
    elif TRACE_FILENAME:
        try:
            TRACE_FH = open(_MSCOMMON_FILENAME.rewrite(TRACE_FILENAME, sync=DEBUG_LOGGING_ENABLED), 'w')
            TRACE_ENABLED = True
        except:
            pass

    @classmethod
    def get_relative_filename(cls, filename):
        try:
            # SCons and below
            ind = filename.rindex('SCons')
            return filename[ind:]
        except:
            # Not in SCons tree
            return filename

    @classmethod
    def get_frame_arglist(cls, frame):
        args = "("
        for i in range(frame.f_code.co_argcount):
            if i: args += ', '
            name = frame.f_code.co_varnames[i]
            args += name
            if name in cls.FRAME_ARGUMENT_VALUES:
                args += "=%s" % frame.f_locals[name]
        args += ")"
        return args

    @classmethod
    def print_message(cls, message):
        print(message, file=cls.TRACE_FH, flush=True)

    @classmethod
    def display_frame(cls, frame, indent, divider=False):
        current_func = frame.f_code.co_name
        if cls.DISPLAY_FUNCTION_LOCATION:
            current_file = cls.get_relative_filename(frame.f_code.co_filename)
            if frame.f_back:
                from_file = cls.get_relative_filename(frame.f_back.f_code.co_filename)
                from_line = frame.f_back.f_lineno
                if frame.f_back.f_code.co_filename == frame.f_code.co_filename:
                    from_where = " from %d" % from_line
                else:
                    from_where = " from %s:%d" % (from_file, from_line)
            else:
                from_where = ""
            location = " <%s:%d%s>" % (current_file, frame.f_lineno, from_where)
        else:
            location = ""

        if cls.DISPLAY_FUNCTION_ARGLIST:
            arglist = cls.get_frame_arglist(frame)
        else:
            arglist = ""

        outstr = "%s%s%s%s" % (indent, current_func, arglist, location)
        cls.print_message(outstr)

        if divider and cls.FRAME_CALLER_FRAMES > 1:
            divstr = "%s%s" % (indent, "-" * len(outstr))
            cls.print_message(divstr)

    @classmethod
    def split_parent_child(cls, filename):
        if not filename:
            return (None, None)
        parent = None
        more, child = os.path.split(filename)
        child = os.path.splitext(child)[0]
        if more:
            _, parent = os.path.split(more)
        return (parent, child)

    @classmethod
    def is_whitelisted(cls, module, function):
        pair = (module, function)
        if cls.DEBUG_WHITELIST_ENABLED and pair in cls.DEBUG_WHITELIST_FUNCTIONS:
            return True
        if cls.FRAME_WHITELIST_ENABLED and pair in cls.FRAME_WHITELIST_FUNCTIONS:
            return True
        return False

    @classmethod
    def is_blacklisted(cls, module, function):
        pair = (module, function)
        if cls.DEBUG_BLACKLIST_ENABLED and pair in cls.DEBUG_BLACKLIST_FUNCTIONS:
            return True
        if cls.FRAME_BLACKLIST_ENABLED and pair in cls.FRAME_BLACKLIST_FUNCTIONS:
            return True
        return False

    @classmethod
    def trace_current_module(cls, frame, event, arg):

        if event != 'call':
            return

        # ignore native python calls (e.g., list comprehension)
        if frame.f_code.co_name[0] == "<":
            return

        # ignore calls that are not directly the below parent module
        parent, child = cls.split_parent_child(frame.f_code.co_filename)
        if parent != cls.PARENT_MODULE:

            # ignore calls that are not whitelisted (e.g., logging debug)
            if not cls.is_whitelisted(parent, frame.f_code.co_name):
                return

        # ignore calls that are blacklisted (e.g., common debug)
        if cls.is_blacklisted(child, frame.f_code.co_name):
            return

        # walk the stack frames above the current call
        # save the slot for the top-most module entry point
        # construct a frame chain: root -> current frame

        entry_slot = None
        frame_chain = []
        f = frame
        while f:
            if cls.PARENT_MODULE in f.f_code.co_filename:
                entry_slot = len(frame_chain)
            frame_chain.insert(0, f)
            f = f.f_back

        # calculate the starting slot: up to n frames above the entry point
        top = entry_slot + cls.FRAME_CALLER_FRAMES
        if top >= len(frame_chain):
            top = len(frame_chain) - 1

        # adjust the frame chain: starting slot -> current frame
        offset = len(frame_chain) - top - 1
        frame_chain = frame_chain[offset:]

        # entry location is the filename and line number of the first frame
        entry_location = [(f.f_code.co_filename, f.f_lineno) for f in frame_chain[:1]]

        if not cls.FRAME_ENTRY_LOCATION:
            start_new_chain = True
        else:
            start_new_chain = entry_location != cls.FRAME_ENTRY_LOCATION

        if start_new_chain:

            # new call chain: write all of the frames

            if cls.FRAME_ENTRY_LOCATION:
                cls.print_message("")

            divider_index = cls.FRAME_CALLER_FRAMES - 1

            indent = ''
            for i, f in enumerate(frame_chain):
                cls.display_frame(f, indent, divider=(i==divider_index))
                indent += cls.FRAME_INDENT_LITERAL

            # save the entry point location information

            cls.FRAME_ENTRY_SLOT = entry_slot
            cls.FRAME_ENTRY_LOCATION = entry_location
            cls.FRAME_ENTRY_DEPTH = len(frame_chain) - 1

        else:

            # existing call chain: write current frame

            n_indent = cls.FRAME_ENTRY_DEPTH
            n_indent += entry_slot - cls.FRAME_ENTRY_SLOT

            indent = cls.FRAME_INDENT_LITERAL * n_indent
            cls.display_frame(frame, indent)

    @classmethod
    def trace(cls):
        import traceback
        sys.settrace(cls.trace_current_module)

if _MSCOMMON_TRACE.TRACE_ENABLED:
    _MSCOMMON_TRACE.trace()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
