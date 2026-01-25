#!/usr/bin/env python
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""runtest - wrapper script for running SCons tests

The SCons test suite consists of:

 * unit tests        - *Tests.py files from the SCons/ directory
 * end-to-end tests  - *.py files in the test/ directory that
                       require the custom SCons framework from
                       testing/framework.

This script adds SCons/ and testing/ directories to PYTHONPATH,
performs test discovery and processes tests according to options.
"""

from __future__ import annotations

import argparse
import itertools
import logging
import os
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path, PurePath, PureWindowsPath
from queue import Queue

cwd = os.getcwd()
debug: str | None = None
scons: str | None = None
suppress_output: bool = False
script = PurePath(sys.argv[0]).name
usagestr = f"{script} [OPTIONS] [TEST ...]"
epilogstr = """\
Environment Variables:
  PRESERVE, PRESERVE_{PASS,FAIL,NO_RESULT}: preserve test subdirs
  TESTCMD_VERBOSE: turn on verbosity in TestCommand\
"""

@dataclass
class Summary:
    """The overall results of the test run.

    This exists to collect what would otherwise be a bunch of globals
    into one place. Things the report printers want should be added here.
    """

    time_start: datetime
    total_time: float = 0.0
    total_num_tests: int = 0
    jobs: int = 1
    passed: list[str] | None = None
    failed: list[str] | None = None
    no_result: list[str] | None = None

stats = Summary(time_start=datetime.now())

# this is currently expected to be global, maybe refactor later?
unittests: list[str]

parser = argparse.ArgumentParser(
    usage=usagestr,
    epilog=epilogstr,
    allow_abbrev=False,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

# test selection options:
testsel = parser.add_argument_group(description='Test selection options:')
testsel.add_argument(metavar='TEST', nargs='*', dest='testlist',
                     help="Select TEST(s) (tests and/or directories) to run")
testlisting = testsel.add_mutually_exclusive_group()
testlisting.add_argument('-f', '--file', metavar='FILE', dest='testlistfile',
                     help="Select only tests in FILE")
testlisting.add_argument('-a', '--all', action='store_true',
                     help="Select all tests")
testlisting.add_argument('--retry', action='store_true',
                     help="Rerun the last failed tests in 'failed_tests.log'")
testsel.add_argument('--exclude-list', metavar="FILE", dest='excludelistfile',
                     help="""Exclude tests in FILE from current selection""")
testtype = testsel.add_mutually_exclusive_group()
testtype.add_argument('--e2e-only', action='store_true',
                      help="Exclude unit tests from selection")
testtype.add_argument('--unit-only', action='store_true',
                      help="Exclude end-to-end tests from selection")

# miscellaneous options
parser.add_argument('-b', '--baseline', metavar='BASE',
                    help="Run test scripts against baseline BASE.")
parser.add_argument('-d', '--debug', action='store_true',
                    help="Run test scripts under the Python debugger.")
parser.add_argument('-D', '--devmode', action='store_true',
                    help="Run tests in Python's development mode (Py3.7+ only).")
parser.add_argument('-e', '--external', action='store_true',
                    help="Run the script in external mode (for external Tools)")

def posint(arg: str) -> int:
    """Special positive-int type for :mod:`argparse`"""
    num = int(arg)
    if num < 0:
        raise argparse.ArgumentTypeError("JOBS value must not be negative")
    return num

parser.add_argument('-j', '--jobs', metavar='JOBS', default=1, type=posint,
                    help="Run tests in JOBS parallel jobs (0 for cpu_count).")
parser.add_argument('-l', '--list', action='store_true', dest='list_only',
                    help="List available tests and exit.")
parser.add_argument('-n', '--no-exec', action='store_false',
                    dest='execute_tests',
                    help="No execute, just print command lines.")
parser.add_argument('--nopipefiles', action='store_false',
                    dest='allow_pipe_files',
                    help="""Do not use the "file pipe" workaround for subprocess
                           for starting tests. See source code for warnings.""")
parser.add_argument('-P', '--python', metavar='PYTHON',
                    help="Use the specified Python interpreter.")
parser.add_argument('--quit-on-failure', action='store_true',
                    help="Quit on any test failure.")
parser.add_argument('--runner', metavar='CLASS',
                    help="Test runner class for unit tests.")
parser.add_argument('-X', dest='scons_exec', action='store_true',
                    help="Test script is executable, don't feed to Python.")
parser.add_argument('-x', '--exec', metavar="SCRIPT",
                    help="Test using SCRIPT as path to SCons.")
parser.add_argument('--faillog', dest='error_log', metavar="FILE",
                    default='failed_tests.log',
                    help="Log failed tests to FILE (enabled by default, "
                         "default file 'failed_tests.log')")
parser.add_argument('--no-faillog', dest='error_log',
                    action='store_const', const=None,
                    default='failed_tests.log',
                    help="Do not log failed tests to a file")

parser.add_argument('--no-ignore-skips', action='store_true', default=False,
                    help="If any tests are skipped, exit status 2")

outctl = parser.add_argument_group(description='Output control options:')
outctl.add_argument('-k', '--no-progress', action='store_false',
                    dest='print_progress',
                    help="Suppress count and progress percentage messages.")
outctl.add_argument('--passed', action='store_true',
                    dest='print_passed_summary',
                    help="Summarize which tests passed.")
outctl.add_argument('-q', '--quiet', action='store_false',
                    dest='printcommand',
                    help="Don't print the test being executed.")
outctl.add_argument('-s', '--short-progress', action='store_true',
                    help="""Short progress, prints only the command line
                             and a progress percentage, no results.""")
outctl.add_argument('-t', '--time', action='store_true', dest='print_times',
                    help="Print test execution time.")
outctl.add_argument('--verbose', metavar='LEVEL', type=int, choices=range(1, 4),
                    help="""Set verbose level
                             (1=print executed commands,
                             2=print commands and non-zero output,
                             3=print commands and all output).""")
# maybe add?
# outctl.add_argument('--version', action='version', version=f'{script} 1.0')

logctl = parser.add_argument_group(description='Log control options:')
logctl.add_argument('-o', '--output', metavar='LOG', help="Save console output to LOG.")
logctl.add_argument(
    '--xml',
    metavar='XML',
    help="Save results to XML in SCons XML format (use - for stdout).",
)

# process args and handle a few specific cases:
args: argparse.Namespace = parser.parse_args()

# we can't do this check with an argparse exclusive group, since those
# only work with optional args, and the cmdline tests (args.testlist)
# are not optional args,
if args.testlist and (args.testlistfile or args.all or args.retry):
    sys.stderr.write(
        parser.format_usage()
        + "error: command line tests cannot be combined with -f/--file, -a/--all or --retry\n"
    )
    sys.exit(1)

if args.retry:
    args.testlistfile = 'failed_tests.log'

if args.testlistfile:
    # args.testlistfile changes from a string to a pathlib Path object
    try:
        ptest = Path(args.testlistfile)
        args.testlistfile = ptest.resolve(strict=True)
    except FileNotFoundError:
        sys.stderr.write(
            parser.format_usage()
            + f'error: -f/--file testlist file "{args.testlistfile}" not found\n'
        )
        sys.exit(1)

if args.excludelistfile:
    # args.excludelistfile changes from a string to a pathlib Path object
    try:
        pexcl = Path(args.excludelistfile)
        args.excludelistfile = pexcl.resolve(strict=True)
    except FileNotFoundError:
        sys.stderr.write(
            parser.format_usage()
            + f'error: --exclude-list file "{args.excludelistfile}" not found\n'
        )
        sys.exit(1)

if args.jobs == 0:
    try:
        # on Linux, check available rather than physical CPUs
        args.jobs = len(os.sched_getaffinity(0))
    except AttributeError:
        # Windows
        args.jobs = os.cpu_count()

# sanity check
if args.jobs == 0:
    sys.stderr.write(
        parser.format_usage()
        + "Unable to detect CPU count, give -j a non-zero value\n"
    )
    sys.exit(1)

stats.jobs = args.jobs

if not args.printcommand:
    suppress_output = True

if args.verbose:
    os.environ['TESTCMD_VERBOSE'] = str(args.verbose)

if args.debug:
    # TODO: add a way to pass a specific debugger
    debug = "pdb"

if args.exec:
    scons = args.exec

# --- define helpers ----
if sys.platform == 'win32':
    # thanks to Eryk Sun for this recipe
    import ctypes

    shlwapi = ctypes.OleDLL('shlwapi')
    shlwapi.AssocQueryStringW.argtypes = (
        ctypes.c_ulong,  # flags
        ctypes.c_ulong,  # str
        ctypes.c_wchar_p,  # pszAssoc
        ctypes.c_wchar_p,  # pszExtra
        ctypes.c_wchar_p,  # pszOut
        ctypes.POINTER(ctypes.c_ulong),  # pcchOut
    )

    ASSOCF_NOTRUNCATE = 0x00000020
    ASSOCF_INIT_IGNOREUNKNOWN = 0x00000400
    ASSOCSTR_COMMAND = 1
    ASSOCSTR_EXECUTABLE = 2
    E_POINTER = ctypes.c_long(0x80004003).value

    def get_template_command(filetype, verb=None):
        """Return the association-related string for *filetype*"""
        flags = ASSOCF_INIT_IGNOREUNKNOWN | ASSOCF_NOTRUNCATE
        assoc_str = ASSOCSTR_COMMAND
        cch = ctypes.c_ulong(260)
        while True:
            buf = (ctypes.c_wchar * cch.value)()
            try:
                shlwapi.AssocQueryStringW(
                    flags, assoc_str, filetype, verb, buf, ctypes.byref(cch)
                )
            except OSError as e:
                if e.winerror != E_POINTER:
                    raise
                continue
            break
        return buf.value


logger = logging.getLogger("runtest.console")
logger.setLevel(logging.DEBUG)
# Create stdout handler for logging to the console
console_handler = logging.StreamHandler(sys.stdout)
if suppress_output:
    # leaves out INFO, so console output is blocked
    console_handler.setLevel(logging.WARNING)
else:
    console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(CustomFormatter(fmt))
logger.addHandler(console_handler)

if args.output:
    # Create file handler for logging to a file
    file_handler = logging.FileHandler(filename=args.output, mode="w")
    file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(file_handler)
    # start time does not go to console but does go to logfile
    logger.debug("Test started at %s", stats.time_start)

xml_logger: logging.Logger = logging.getLogger("runtest.xml")
xml_logger.setLevel(logging.DEBUG)
if args.xml:

    class XmlFormatter(logging.Formatter):
        """Specialized formatter for producing xml output.

        This class abuses logging syntax a bit: we log one "record",
        which is usually the list of all the tests run, and that's
        formatted into the scons-xml output format.

        The output may not be complete. Originally, It was expected an
        external tool (e.g. bin/scons-test.py) would generate a wrapper
        around the contents for a complete xml test description and
        also including lots of information collected about the test
        environment.  So if the xml output file is set to '-', just dump
        the results of each test to support that usecase (the logger
        destination will have been set to stdout in this situatin).
        If a real filename was supplied, assume we are not being called
        that way, so synthesize just enough of the wrapper to at least
        make a complete file.

        The format is unique to SCons, and does not use the well-known
        JUnit XML schema.
        """
        wrap_output = True

        def _format_header(self) -> str:
            head = (
                # Mismatches even if direct copied to test/runtest/xml/output.py
                # '<?xml version="1.0" encoding="utf-8"?>\n'
                "<scons_testsuite>\n"
                "  <tests>\n"
            ) if self.wrap_output else "  <tests>\n"
            return head

        @staticmethod
        def _format_stats() -> str:
            return (
                "  <summary>\n"
                f"    <tests>{stats.total_num_tests}</tests>\n"
                f"    <failed>{len(stats.failed)}</failed>\n"
                f"    <no_result>{len(stats.no_result)}</no_result>\n"
                f"    <interpreter>{stats.python}</interpreter>\n"
                f"    <threads>{stats.jobs}</threads>\n"
                f"    <time>{stats.total_time:.1f}</time>\n"
                f"    <timestamp>{stats.time_start}</timestamp>\n"
                "  </summary>\n"
            )

        def _format_footer(self) -> str:
            end = "  </tests>\n"
            summary = self._format_stats()
            foot = "</scons_testsuite>"
            if self.wrap_output:
               return end + summary + foot
            return end

        @staticmethod
        def _format_tests(record):
            """generate xml string describing one test result."""
            # We don't want the newline terminators in the xml
            stdout = record.stdout.rstrip('\n')
            stderr = record.stderr.rstrip('\n')
            return (
                f'    <test>\n'
                f'      <file_name>{record.path}</file_name>\n'
                f'      <command_line>{record.command_str[:-1]}</command_line>\n'
                f'      <exit_status>{record.status}</exit_status>\n'
                f'      <stdout>{stdout}</stdout>\n'
                f'      <stderr>{stderr}</stderr>\n'
                f'      <time>{record.test_time:.1f}</time>\n'
                f'    </test>\n'
            )

        def format(self, record):
            """format results into xml.

            Accepts two forms of input: if a list, assume this is the
            list of all the tests run, and format up each individual
            record, possibly with header and footer content.  If it is
            a string, assume it's already xml-ified so return it unchanged.
            There is no case for actually "formatting" a string.
            """
            rv = ""
            records = record.msg
            if isinstance(records, list) and len(records) > 0:
                rv = rv + self._format_header()
                for record in records:
                    rv = rv + self._format_tests(record)
                rv = rv + self._format_footer()
            else:
                rv = records
            return rv

    xml_logger.setLevel(logging.DEBUG)
    fmt = '%(asctime)s | %(levelname)8s | %(message)s'

    if args.xml == '-':
        xml_handler = logging.StreamHandler()
        XmlFormatter.wrap_output = False
    else:
        xml_handler = logging.FileHandler(filename=args.xml, mode='w')
    xml_handler.setLevel(logging.DEBUG)
    xml_handler.setFormatter(XmlFormatter())
    xml_logger.addHandler(xml_handler)
else:
    xml_handler = logging.NullHandler()
    xml_logger.addHandler(xml_handler)


class Test:
    """Class holding a single test file."""
    _ids = itertools.count(1)  # to geenerate test # automatically

    def __init__(self, path, spe=None):
        self.path = path
        self.testno = next(self._ids)
        self.stdout = self.stderr = self.status = None
        self.abspath = path.absolute()
        self.command_args: list = []
        self.command_str: str = ""
        self.headline: str = ""
        self.test_time: float = 0.0
        if spe:
            for dirpath in spe:
                file = os.path.join(dirpath, path)
                if os.path.isfile(file):
                    self.abspath = file
                    break

    def execute(self, env) -> None:
        if args.allow_pipe_files:
            # The subprocess.Popen() suffers from a well-known
            # problem. Data for stdout/stderr is read into a
            # memory buffer of fixed size, 65K which is not very much.
            # When it fills up, it simply stops letting the child process
            # write to it. The child will then sit and patiently wait to
            # be able to write the rest of its output. Hang!
            # In order to work around this, we follow a suggestion
            # by Anders Pearson in
            #   https://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
            # and pass temp file objects to Popen() instead of the ubiquitous
            # subprocess.PIPE.
            tmp_stdout = tempfile.TemporaryFile(mode='w+t')
            tmp_stderr = tempfile.TemporaryFile(mode='w+t')
            cp = subprocess.run(
                self.command_args,
                stdout=tmp_stdout,
                stderr=tmp_stderr,
                shell=False,
                env=env,
                check=False,
            )
            self.status = cp.returncode

            try:
                # Rewind to start of files
                tmp_stdout.seek(0)
                tmp_stderr.seek(0)
                # Read output
                self.stdout = tmp_stdout.read()
                self.stderr = tmp_stderr.read()
            finally:
                # Remove temp files by closing them
                tmp_stdout.close()
                tmp_stderr.close()
        else:
            # We get here only if the user gave the '--nopipefiles'
            # option, meaning the "temp file" approach for
            # subprocess.communicate() above shouldn't be used.
            # He hopefully knows what he's doing, but again we have a
            # potential deadlock situation in the following code:
            #   If the subprocess writes a lot of data to its stderr,
            #   the pipe will fill up (nobody's reading it yet) and the
            #   subprocess will wait for someone to read it.
            #   But the parent process is trying to read from stdin
            #   (but the subprocess isn't writing anything there).
            #   Hence a deadlock.
            # Be dragons here! Better don't use this!
            cp = subprocess.run(
                self.command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                env=env,
                check=False,
            )
            self.status, self.stdout, self.stderr = cp.returncode, cp.stdout, cp.stderr

# --- start processing ---

if not args.baseline or args.baseline == '.':
    baseline = cwd
elif args.baseline == '-':
    sys.stderr.write(
        "'baseline' logic used to checkout from svn. It has been removed. "
        "If you used this, please let us know on devel mailing list, "
        "IRC, or discord server\n"
    )
    sys.exit(-1)
else:
    baseline = args.baseline
scons_runtest_dir = baseline

if not args.external:
    scons_script_dir = os.path.join(baseline, 'scripts')
    scons_tools_dir = os.path.join(baseline, 'bin')
    scons_lib_dir = baseline
else:
    scons_script_dir = ''
    scons_tools_dir = ''
    scons_lib_dir = ''

testenv = {
    'SCONS_RUNTEST_DIR': scons_runtest_dir,
    'SCONS_TOOLS_DIR': scons_tools_dir,
    'SCONS_SCRIPT_DIR': scons_script_dir,
    'SCONS_CWD': cwd,
}

if scons:
    # Let the version of SCons that the -x option pointed to find
    # its own modules.
    testenv['SCONS'] = scons
elif scons_lib_dir:
    # Because SCons is really aggressive about finding its modules,
    # it sometimes finds SCons modules elsewhere on the system.
    # This forces SCons to use the modules that are being tested.
    testenv['SCONS_LIB_DIR'] = scons_lib_dir

if args.scons_exec:
    testenv['SCONS_EXEC'] = '1'

if args.external:
    testenv['SCONS_EXTERNAL_TEST'] = '1'

# Insert scons path and path for testing framework to PYTHONPATH
scriptpath = os.path.dirname(os.path.realpath(__file__))
frameworkpath = os.path.join(scriptpath, 'testing', 'framework')
testenv['PYTHONPATH'] = os.pathsep.join((scons_lib_dir, frameworkpath))
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath:
    testenv['PYTHONPATH'] = testenv['PYTHONPATH'] + os.pathsep + pythonpath

if sys.platform == 'win32':
    # Windows doesn't support "shebang" lines directly (the Python launcher
    # and Windows Store version do, but you have to get them launched first)
    # so to directly launch a script we depend on an assoc for .py to work.
    # Some systems may have none, and in some cases IDE programs take over
    # the assoc.  Detect this so the small number of tests affected can skip.
    try:
        python_assoc = get_template_command('.py')
    except OSError:
        python_assoc = None
    if not python_assoc or "py" not in python_assoc:
        testenv['SCONS_NO_DIRECT_SCRIPT'] = '1'

os.environ.update(testenv)

# Clear _JAVA_OPTIONS which java tools output to stderr when run breaking tests
if '_JAVA_OPTIONS' in os.environ:
    del os.environ['_JAVA_OPTIONS']


# ---[ test discovery ]------------------------------------
# This section figures out which tests to run.
#
# The initial testlist is made by reading from the testlistfile,
# if supplied, or by looking at the test arguments, if supplied,
# or by looking for all test files if the "all" argument is supplied.
# One of the three is required.
#
# Each test path, whichever of the three sources it comes from,
# specifies either a test file or a directory to search for
# SCons tests. SCons code layout assumes that any file under the 'SCons'
# subdirectory that ends with 'Tests.py' is a unit test, and any Python
# script (*.py) under the 'test' subdirectory is an end-to-end test.
# We need to track these because they are invoked differently.
# find_unit_tests and find_e2e_tests are used for this searching.
#
# Note that there are some tests under 'SCons' that *begin* with
# 'test_', but they're packaging and installation tests, not
# functional tests, so we don't execute them by default.  (They can
# still be executed by hand, though).
#
# Test exclusions, if specified, are then applied.


def scanlist(testfile):
    """Process a testlist file."""
    data = StringIO(testfile.read_text())
    tests = [t.strip() for t in data.readlines() if not t.startswith('#')]
    # in order to allow scanned lists to work whether they use forward or
    # backward slashes, first create the object as a PureWindowsPath which
    # accepts either, then use that to make a Path object to use for
    # comparisons like "file in scanned_list".
    return [Path(PureWindowsPath(t)) for t in tests if t]


def find_unit_tests(directory):
    """Look for unit tests."""
    result = []
    for dirpath, _, filenames in os.walk(directory):
        # Skip folders containing a sconstest.skip file
        if 'sconstest.skip' in filenames:
            continue
        for fname in filenames:
            if fname.endswith("Tests.py"):
                result.append(Path(dirpath, fname))

    return sorted(result)


def find_e2e_tests(directory):
    """Look for end-to-end tests"""
    result = []
    for dirpath, _, filenames in os.walk(directory):
        # Skip folders containing a sconstest.skip file
        if 'sconstest.skip' in filenames:
            continue

        # Gather up the data from any exclude lists
        excludes = []
        if ".exclude_tests" in filenames:
            excludefile = Path(dirpath, ".exclude_tests").resolve()
            excludes = scanlist(excludefile)

        for fname in filenames:
            if fname.endswith(".py") and Path(fname) not in excludes:
                result.append(Path(dirpath, fname))

    return sorted(result)


# Initial test selection:
unittests = []
endtests = []
if args.testlistfile:
    tests = scanlist(args.testlistfile)
else:
    testpaths = []
    if args.all:  # -a flag
        testpaths = [Path('SCons'), Path('test')]
    elif args.testlist:  # paths given on cmdline
        testpaths = [Path(PureWindowsPath(t)) for t in args.testlist]

    for path in testpaths:
        # Clean up path removing leading ./ or .\
        name = str(path)
        if name.startswith('.') and name[1] in (os.sep, os.altsep):
            path = path.with_name(name[2:])

        if path.exists():
            if path.is_dir():
                if path.parts[0] == "SCons" or path.parts[0] == "testing":
                    unittests.extend(find_unit_tests(path))
                elif path.parts[0] == 'test':
                    endtests.extend(find_e2e_tests(path))
                elif args.external and 'test' in path.parts:
                    endtests.extend(find_e2e_tests(path))
            else:
                if path.match("*Tests.py"):
                    unittests.append(path)
                elif path.match("*.py"):
                    endtests.append(path)

    tests = sorted(unittests + endtests)

# Remove exclusions:
if args.e2e_only:
    tests = [t for t in tests if not t.match("*Tests.py")]
if args.unit_only:
    tests = [t for t in tests if t.match("*Tests.py")]
if args.excludelistfile:
    excludetests = scanlist(args.excludelistfile)
    tests = [t for t in tests if t not in excludetests]

# did we end up with any tests?
if not tests:
    sys.stderr.write(parser.format_usage() + """
error: no tests matching the specification were found.
       See "Test selection options" in the help for details on
       how to specify and/or exclude tests.
""")
    sys.exit(1)

# ---[ test processing ]-----------------------------------
tests = [Test(t) for t in tests]
stats.total_num_tests = len(tests)

if args.list_only:
    for t in tests:
        print(t.path)
    sys.exit(0)

if not args.python:
    if os.name == 'java':
        args.python = os.path.join(sys.prefix, 'jython')
    else:
        args.python = sys.executable
os.environ["python_executable"] = args.python
stats.python = args.python

def log_result(t: Test) -> None:
    """Log the result of a test.

    "log" in this case means writing to stdout (and/or if configured,
    to a file). Since we might be called from any of several threads,
    confine the result to a single logging call to avoid interleaving.

    Args:
        t: (completed) testcase instance
    """
    times = f"Test execution time: {t.test_time:.1f} seconds" if args.print_times else ""
    if args.short_progress:
        # not sure if short-progress should turn off times,
        # since times had to be explicitly selected. Leave in for now?
        logger.info(t.headline + t.command_str + times)
    else:
        logger.info(t.headline + t.command_str + t.stdout + t.stderr + times)

    if args.quit_on_failure and t.status == 1:
        logger.error("Exiting due to error : %s", t.status)
        sys.exit(1)


def run_test(t: Test) -> None:
    """Run a testcase.

    Builds the command line to give to execute().  Also record information
    that will be used in output, when :func:`log_resut` is called.

    Args:
        t: testcase instance
    """
    command_args = []
    if debug:
        command_args.extend(['-m', debug])
    if args.devmode:
        command_args.append('-X dev')
    command_args.append(str(t.path))
    if args.runner and t.path in unittests:
        # For example --runner TestUnit.TAPTestRunner
        command_args.append('--runner ' + args.runner)
    t.command_args = [args.python] + command_args
    t.command_str = " ".join(t.command_args) + "\n"
    if args.print_progress:
        # if enabled, compute progress message before test, but defer
        # emitting it until the test has run - avoids interleaving.
        t.headline += (
            f"{t.testno}/{stats.total_num_tests} "
            f"({(t.testno * 100 / stats.total_num_tests):.2f}%) "
        )

    head, _ = os.path.split(t.abspath)
    fixture_dirs = []
    if head:
        fixture_dirs.append(head)
    fixture_dirs.append(os.path.join(scriptpath, 'test', 'fixture'))

    # Set the list of fixture dirs directly in the environment. Just putting
    # it in os.environ and spawning the process is racy. Make it reliable by
    # overriding the environment passed to execute().
    env = os.environ.copy()
    env['FIXTURE_DIRS'] = os.pathsep.join(fixture_dirs)

    test_start_time: float = time.perf_counter()
    if args.execute_tests:
        t.execute(env)

    t.test_time = time.perf_counter() - test_start_time
    log_result(t)


class TestRunner(threading.Thread):
    """Test Runner thread.

    One instance will be created for each job in multi-job mode
    """

    def __init__(self, queue=None, group=None, target=None, name=None):
        super().__init__(group=group, target=target, name=name)
        self.queue = queue

    def run(self):
        for test in iter(self.queue.get, None):
            run_test(test)
            self.queue.task_done()

if args.jobs == 1:
    for test in tests:
        run_test(test)
else:
    logger.info("Running tests using %d jobs", stats.jobs)
    testq = Queue()
    for test in tests:
        testq.put(test)
    threads = [TestRunner(queue=testq) for _ in range(args.jobs)]
    for thread in threads:
        thread.daemon = True
        thread.start()
    # wait on the queue rather than the individual threads
    testq.join()

# --- all tests are complete by the time we get here ---
if not tests:
    sys.exit(0)

stats.total_time = (datetime.now() - stats.time_start).total_seconds()
stats.passed = [str(t.path) for t in tests if t.status == 0]
stats.failed = [str(t.path) for t in tests if t.status == 1]
stats.no_result = [str(t.path) for t in tests if t.status == 2]

logger.info(
    "Summary: %s selected, %s failed, %s no result%s",
    stats.total_num_tests,
    len(stats.failed),
    len(stats.no_result),
    ", total execution time %.1f seconds" % stats.total_time if args.print_times else "",
)

# print category summaries (skip if only one test run)
if args.execute_tests and stats.total_num_tests > 1:
    if stats.passed and args.print_passed_summary:
        if len(stats.passed) == 1:
            logger.info("\nPassed the following test:\n\t%s", stats.passed[0])
        else:
            logger.info(
                "\nPassed the following %d tests:\n\t%s",
                len(stats.passed),
                "\n\t".join(stats.passed),
            )
    if stats.failed:
        if len(stats.failed) == 1:
            logger.info("\nFailed the following test:\n\t%s", stats.failed[0])
        else:
            logger.info(
                "\nFailed the following %d tests:\n\t%s",
                len(stats.failed),
                "\n\t".join(stats.failed),
            )
    if stats.no_result:
        if len(stats.no_result) == 1:
            logger.info("\nNO RESULT from the following test:\n\t%s", stats.no_result[0])
        else:
            logger.info(
                "\nNO RESULT from the following %d tests:\n\t%s",
                len(stats.no_result),
                "\n\t".join(stats.no_result),
            )

# save the fails to a file
if args.error_log:
    with open(args.error_log, "w", encoding="utf-8") as f:
        if stats.failed:
            for test in stats.failed:
                print(test, file=f)
        # if there are no fails, file will be cleared

# xml output format
if args.xml:
    xml_logger.info(tests)

if stats.failed:
    sys.exit(1)
elif stats.no_result and args.no_ignore_skips:
    # if no fails, but skips were found
    sys.exit(2)
else:
    sys.exit(0)
