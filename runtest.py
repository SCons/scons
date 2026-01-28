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
from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from pathlib import Path, PurePath, PureWindowsPath
from queue import Queue

# Helper for Windows
if sys.platform == 'win32':
    import ctypes

    def get_template_command(filetype, verb=None):
        """Return the association-related string for *filetype*.

        Args:
            filetype: The file type extension (e.g., '.py').
            verb: The verb (optional).

        Returns:
            The command string.
        """
        # thanks to Eryk Sun for this recipe
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
        E_POINTER = ctypes.c_long(0x80004003).value

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

@dataclass
class Summary:
    """The overall results of the test run.

    Attributes:
        time_start: Start time of the test run.
        total_time: Total execution time.
        total_num_tests: Total number of tests executed.
        jobs: Number of parallel jobs used.
        passed: List of passed tests.
        failed: List of failed tests.
        no_result: List of tests with no result.
        python: Python interpreter used.
    """
    time_start: datetime = field(default_factory=datetime.now)
    total_time: float = 0.0
    total_num_tests: int = 0
    jobs: int = 1
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    no_result: list[str] = field(default_factory=list)
    python: str = ""

@dataclass
class RunContext:
    """Holds configuration and state for the test run.

    Attributes:
        args: Parsed command-line arguments.
        stats: Summary object for collecting statistics.
        logger: Logger for console output.
        scriptpath: Path to the script directory.
        unittests: List of discovered unit tests.
        debug: Debug mode string (e.g., 'pdb') or None.
    """
    args: argparse.Namespace
    stats: Summary
    logger: logging.Logger
    scriptpath: Path
    unittests: list[Path]
    debug: str | None = None

class Test:
    """Class holding a single test file.

    Args:
        path: Path to the test file.
        spe: Specific path entries (optional).
    """
    _ids = itertools.count(1)  # to generate test # automatically

    def __init__(self, path: Path, spe=None):
        self.path = path
        self.testno = next(self._ids)
        self.stdout: str | None = None
        self.stderr: str | None = None
        self.status: int | None = None
        self.abspath = path.absolute()
        self.command_args: list = []
        self.command_str: str = ""
        self.headline: str = ""
        self.test_time: float = 0.0
        if spe:
            for dirpath in spe:
                file = dirpath / path
                if file.is_file():
                    self.abspath = file
                    break

    def execute(self, env: dict, allow_pipe_files: bool = True) -> None:
        """Execute the test.

        Args:
            env: Environment variables for the test execution.
            allow_pipe_files: Whether to use temporary files for stdout/stderr to avoid hanging.
        """
        if allow_pipe_files:
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
            with tempfile.TemporaryFile(mode='w+t') as tmp_stdout, \
                 tempfile.TemporaryFile(mode='w+t') as tmp_stderr:
                
                cp = subprocess.run(
                    self.command_args,
                    stdout=tmp_stdout,
                    stderr=tmp_stderr,
                    shell=False,
                    env=env,
                    check=False,
                )
                self.status = cp.returncode

                # Rewind to start of files
                tmp_stdout.seek(0)
                tmp_stderr.seek(0)
                # Read output
                self.stdout = tmp_stdout.read()
                self.stderr = tmp_stderr.read()

        else:
            # We get here only if the user gave the '--nopipefiles'
            # option, meaning the "temp file" approach for
            # subprocess.communicate() above shouldn't be used.
            # He hopefully knows what he's doing, but again we have a
            # potential deadlock situation.
            cp = subprocess.run(
                self.command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                env=env,
                check=False,
                text=True # Ensure output is string
            )
            self.status = cp.returncode
            self.stdout = cp.stdout
            self.stderr = cp.stderr


def posint(arg: str) -> int:
    """Special positive-int type for :mod:`argparse`.

    Args:
        arg: The argument string to convert.

    Returns:
        The converted integer.

    Raises:
        argparse.ArgumentTypeError: If the value is negative.
    """
    num = int(arg)
    if num < 0:
        raise argparse.ArgumentTypeError("JOBS value must not be negative")
    return num


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser.

    Returns:
        The configured argument parser.
    """
    script = PurePath(sys.argv[0]).name
    usagestr = f"{script} [OPTIONS] [TEST ...]"
    epilogstr = """
Environment Variables:
  PRESERVE, PRESERVE_{PASS,FAIL,NO_RESULT}: preserve test subdirs
  TESTCMD_VERBOSE: turn on verbosity in TestCommand
"""
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
                         help="Exclude tests in FILE from current selection")
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
    parser.add_argument('-j', '--jobs', metavar='JOBS', default=1, type=posint,
                        help="Run tests in JOBS parallel jobs (0 for cpu_count).")
    parser.add_argument('-l', '--list', action='store_true', dest='list_only',
                        help="List available tests and exit.")
    parser.add_argument('-n', '--no-exec', action='store_false',
                        dest='execute_tests',
                        help="No execute, just print command lines.")
    parser.add_argument('--nopipefiles', action='store_false',
                        dest='allow_pipe_files',
                        help='Do not use the "file pipe" workaround for subprocess '
                             'for starting tests. See source code for warnings.')
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
                        help="Short progress, prints only the command line "
                             "and a progress percentage, no results.")
    outctl.add_argument('-t', '--time', action='store_true', dest='print_times',
                        help="Print test execution time.")
    outctl.add_argument('--verbose', metavar='LEVEL', type=int, choices=range(1, 4),
                        help="Set verbose level "
                             "(1=print executed commands, "
                             "2=print commands and non-zero output, "
                             "3=print commands and all output).")

    logctl = parser.add_argument_group(description='Log control options:')
    logctl.add_argument('-o', '--output', metavar='LOG', help="Save console output to LOG.")
    logctl.add_argument(
        '--xml',
        metavar='XML',
        help="Save results to XML in SCons XML format (use - for stdout).",
    )
    return parser

def process_arguments(args: argparse.Namespace, parser: argparse.ArgumentParser) -> argparse.Namespace:
    """Validate and process parsed arguments.

    Args:
        args: The parsed arguments.
        parser: The argument parser (used for error reporting).

    Returns:
        The processed arguments.
    """
    # Post-processing args
    if args.testlist and (args.testlistfile or args.all or args.retry):
        sys.stderr.write(
            parser.format_usage()
            + "error: command line tests cannot be combined with -f/--file, -a/--all or --retry\n"
        )
        sys.exit(1)

    if args.retry:
        args.testlistfile = 'failed_tests.log'

    if args.testlistfile:
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

    if args.jobs == 0:
        sys.stderr.write(
            parser.format_usage()
            + "Unable to detect CPU count, give -j a non-zero value\n"
        )
        sys.exit(1)

    return args

def parse_args() -> tuple[argparse.Namespace, argparse.ArgumentParser]:
    """Parse command line arguments.

    Returns:
        A tuple containing the parsed arguments and the parser object.
    """
    parser = build_parser()
    args = parser.parse_args()
    args = process_arguments(args, parser)
    return args, parser


def scanlist(testfile: Path) -> list[Path]:
    """Process a testlist file.

    Args:
        testfile: Path to the file containing a list of tests.

    Returns:
        A list of Path objects for the tests.
    """
    data = StringIO(testfile.read_text())
    tests = [t.strip() for t in data.readlines() if not t.startswith('#')]
    # in order to allow scanned lists to work whether they use forward or
    # backward slashes, first create the object as a PureWindowsPath which
    # accepts either, then use that to make a Path object to use for
    # comparisons like "file in scanned_list".
    return [Path(PureWindowsPath(t)) for t in tests if t]


def find_unit_tests(directory: Path) -> list[Path]:
    """Look for unit tests.

    Args:
        directory: The directory to search in.

    Returns:
        A list of unit test paths.
    """
    result = []
    for dirpath, _, filenames in os.walk(directory):
        # Skip folders containing a sconstest.skip file
        if 'sconstest.skip' in filenames:
            continue
        for fname in filenames:
            if fname.endswith("Tests.py"):
                result.append(Path(dirpath, fname))

    return sorted(result)


def find_e2e_tests(directory: Path) -> list[Path]:
    """Look for end-to-end tests

    Args:
        directory: The directory to search in.

    Returns:
        A list of end-to-end test paths.
    """
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

def setup_logging(args: argparse.Namespace, stats: Summary):
    """Set up logging to console and file.

    Args:
        args: Command-line arguments.
        stats: Summary object.

    Returns:
        A tuple of (console logger, xml logger).
    """
    logger = logging.getLogger("runtest.console")
    logger.setLevel(logging.DEBUG)
    
    # Create stdout handler for logging to the console
    console_handler = logging.StreamHandler(sys.stdout)
    if not args.printcommand:
        # leaves out INFO, so console output is blocked
        console_handler.setLevel(logging.WARNING)
    else:
        console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    if args.output:
        # Create file handler for logging to a file
        file_handler = logging.FileHandler(filename=args.output, mode="w")
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        # start time does not go to console but does go to logfile
        logger.debug("Test started at %s", stats.time_start)

    # XML Logging Setup
    xml_logger = logging.getLogger("runtest.xml")
    xml_logger.setLevel(logging.DEBUG)

    if args.xml:
        class XmlFormatter(logging.Formatter):
            """Formatter for SCons XML logging."""
            wrap_output = True

            def _format_header(self) -> str:
                head = (
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
                stdout = record.stdout.rstrip('\n') if record.stdout else ''
                stderr = record.stderr.rstrip('\n') if record.stderr else ''
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
                """Format the specified record as XML.

                Args:
                    record: The log record.

                Returns:
                    The formatted string.
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
    
    return logger, xml_logger


def log_result(t: Test, context: RunContext) -> None:
    """Log the result of a test.

    Args:
        t: The test object.
        context: The run context.
    """
    times = f"Test execution time: {t.test_time:.1f} seconds" if context.args.print_times else ""
    
    output = f"{t.headline}{t.command_str}"
    if not context.args.short_progress:
        if t.stdout: output += t.stdout
        if t.stderr: output += t.stderr
    
    output += times
    context.logger.info(output)

    if context.args.quit_on_failure and t.status == 1:
        context.logger.error("Exiting due to error : %s", t.status)
        sys.exit(1)


def run_test(t: Test, context: RunContext) -> None:
    """Run a testcase.

    Args:
        t: The test object.
        context: The run context.
    """
    command_args = []
    if context.debug:
        command_args.extend(['-m', context.debug])
    if context.args.devmode:
        command_args.append('-X dev')
    command_args.append(str(t.path))
    
    if context.args.runner and t.path in context.unittests:
        command_args.append('--runner ' + context.args.runner)
    
    t.command_args = [context.args.python] + command_args
    t.command_str = " ".join(t.command_args) + "\n"
    
    if context.args.print_progress:
        t.headline += (
            f"{t.testno}/{context.stats.total_num_tests} "
            f"({(t.testno * 100 / context.stats.total_num_tests):.2f}%) "
        )

    # Calculate fixture dirs
    head = t.abspath.parent
    fixture_dirs = []
    if head:
        fixture_dirs.append(str(head))
    fixture_dirs.append(str(context.scriptpath / 'test' / 'fixture'))

    env = os.environ.copy()
    env['FIXTURE_DIRS'] = os.pathsep.join(fixture_dirs)

    test_start_time: float = time.perf_counter()
    if context.args.execute_tests:
        t.execute(env, allow_pipe_files=context.args.allow_pipe_files)

    t.test_time = time.perf_counter() - test_start_time
    log_result(t, context)


class TestRunner(threading.Thread):
    """Test Runner thread.

    Args:
        queue: Queue containing tests to run.
        context: The run context.
    """
    def __init__(self, queue, context: RunContext):
        super().__init__()
        self.queue = queue
        self.context = context
        self.daemon = True

    def run(self):
        while True:
            test = self.queue.get()
            if test is None:
                self.queue.task_done()
                break
            run_test(test, self.context)
            self.queue.task_done()

def setup_env(args: argparse.Namespace) -> None:
    """Set up the execution environment (environment variables, paths).

    Args:
        args: Command-line arguments.
    """
    if args.verbose:
        os.environ['TESTCMD_VERBOSE'] = str(args.verbose)

    cwd = Path.cwd()
    
    # Baseline logic
    if not args.baseline or args.baseline == '.':
        baseline = cwd
    elif args.baseline == '-':
        sys.stderr.write(
            "'baseline' logic used to checkout from svn. It has been removed.\n"
        )
        sys.exit(-1)
    else:
        baseline = Path(args.baseline)

    scons_runtest_dir = baseline

    if not args.external:
        scons_script_dir = baseline / 'scripts'
        scons_tools_dir = baseline / 'bin'
        scons_lib_dir = baseline
    else:
        scons_script_dir = ''
        scons_tools_dir = ''
        scons_lib_dir = ''

    # Test environment setup
    testenv = {
        'SCONS_RUNTEST_DIR': str(scons_runtest_dir),
        'SCONS_TOOLS_DIR': str(scons_tools_dir),
        'SCONS_SCRIPT_DIR': str(scons_script_dir),
        'SCONS_CWD': str(cwd),
    }

    if args.exec:
        testenv['SCONS'] = args.exec
    elif scons_lib_dir:
        testenv['SCONS_LIB_DIR'] = str(scons_lib_dir)

    if args.scons_exec:
        testenv['SCONS_EXEC'] = '1'

    if args.external:
        testenv['SCONS_EXTERNAL_TEST'] = '1'

    # Insert scons path and path for testing framework to PYTHONPATH
    scriptpath = Path(__file__).resolve().parent
    frameworkpath = scriptpath / 'testing' / 'framework'
    
    paths = [str(scons_lib_dir), str(frameworkpath)]
    if scons_lib_dir == '': paths = [str(frameworkpath)] # handle empty scons_lib_dir
    
    existing_pythonpath = os.environ.get('PYTHONPATH')
    if existing_pythonpath:
        paths.append(existing_pythonpath)
    
    testenv['PYTHONPATH'] = os.pathsep.join(paths)

    # Windows check
    if sys.platform == 'win32':
        try:
            python_assoc = get_template_command('.py')
        except OSError:
            python_assoc = None
        if not python_assoc or "py" not in python_assoc:
            testenv['SCONS_NO_DIRECT_SCRIPT'] = '1'

    os.environ.update(testenv)

    if '_JAVA_OPTIONS' in os.environ:
        del os.environ['_JAVA_OPTIONS']

def discover_tests(args: argparse.Namespace, parser: argparse.ArgumentParser) -> tuple[list[Path], list[Path]]:
    """Discover tests based on arguments.

    Args:
        args: Command-line arguments.
        parser: The argument parser.

    Returns:
        A tuple of (list of tests to run, list of all unit tests).
    """
    unittests = []
    endtests = []
    
    if args.testlistfile:
        tests = scanlist(args.testlistfile)
    else:
        testpaths = []
        if args.all:
            testpaths = [Path('SCons'), Path('test')]
        elif args.testlist:
            testpaths = [Path(PureWindowsPath(t)) for t in args.testlist]

        for path in testpaths:
            # Clean up path removing leading ./ or .\
            # Path(str) cleans simple ./ but let's ensure
            if str(path).startswith('.') and len(str(path)) > 1 and str(path)[1] in (os.sep, os.altsep or '/') :
                path = Path(str(path)[2:])
            
            if path.exists():
                if path.is_dir():
                    parts = path.parts
                    if parts[0] == "SCons" or parts[0] == "testing":
                        unittests.extend(find_unit_tests(path))
                    elif parts[0] == 'test':
                        endtests.extend(find_e2e_tests(path))
                    elif args.external and 'test' in parts:
                         endtests.extend(find_e2e_tests(path))
                else:
                    if path.match("*Tests.py"):
                        unittests.append(path)
                    elif path.match("*.py"):
                        endtests.append(path)

        tests = sorted(unittests + endtests)

    # Remove exclusions
    if args.e2e_only:
        tests = [t for t in tests if not t.match("*Tests.py")]
    if args.unit_only:
        tests = [t for t in tests if t.match("*Tests.py")]
    if args.excludelistfile:
        excludetests = scanlist(args.excludelistfile)
        tests = [t for t in tests if t not in excludetests]

    if not tests:
        sys.stderr.write(parser.format_usage() + """
error: no tests matching the specification were found.
       See "Test selection options" in the help for details on
       how to specify and/or exclude tests.
""")
        sys.exit(1)

    return tests, unittests

def create_run_context(args, stats, logger, unittests):
    """Create the run context object.

    Args:
        args: Command-line arguments.
        stats: Summary object.
        logger: Logger object.
        unittests: List of unit tests.

    Returns:
        A populated RunContext object.
    """
    # Determine Python executable
    if not args.python:
        if os.name == 'java':
            args.python = os.path.join(sys.prefix, 'jython')
        else:
            args.python = sys.executable
    os.environ["python_executable"] = args.python
    stats.python = args.python
    
    scriptpath = Path(__file__).resolve().parent
    debug = "pdb" if args.debug else None

    return RunContext(
        args=args,
        stats=stats,
        logger=logger,
        scriptpath=scriptpath,
        unittests=unittests,
        debug=debug
    )

def execute_tests(test_objects: list[Test], context: RunContext) -> None:
    """Execute the identified tests.

    Args:
        test_objects: List of Test objects to run.
        context: The run context.
    """
    if context.args.jobs == 1:
        for test in test_objects:
            run_test(test, context)
    else:
        context.logger.info("Running tests using %d jobs", context.stats.jobs)
        testq = Queue()
        for test in test_objects:
            testq.put(test)
        
        # Add None markers to stop threads
        for _ in range(context.args.jobs):
            testq.put(None)

        threads = [TestRunner(queue=testq, context=context) for _ in range(context.args.jobs)]
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

def display_results(context: RunContext, test_objects: list[Test], xml_logger: logging.Logger) -> None:
    """Report the results of the test run.

    Args:
        context: The run context.
        test_objects: List of executed Test objects.
        xml_logger: Logger for XML output.
    """
    stats = context.stats
    args = context.args
    logger = context.logger

    if not test_objects:
        sys.exit(0)

    stats.total_time = (datetime.now() - stats.time_start).total_seconds()
    stats.passed = [str(t.path) for t in test_objects if t.status == 0]
    stats.failed = [str(t.path) for t in test_objects if t.status == 1]
    stats.no_result = [str(t.path) for t in test_objects if t.status == 2]

    logger.info(
        "Summary: %s selected, %s failed, %s no result%s",
        stats.total_num_tests,
        len(stats.failed),
        len(stats.no_result),
        ", total execution time %.1f seconds" % stats.total_time if args.print_times else "",
    )

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

    if args.error_log:
        # if there are no fails, file will be cleared (opened with 'w')
        with open(args.error_log, "w", encoding="utf-8") as f:
            if stats.failed:
                for test in stats.failed:
                    print(test, file=f)

    if args.xml:
        xml_logger.info(test_objects)

    if stats.failed:
        sys.exit(1)
    elif stats.no_result and args.no_ignore_skips:
        sys.exit(2)
    else:
        sys.exit(0)

def main():
    """Main entry point for runtest."""
    args, parser = parse_args()
    stats = Summary(jobs=args.jobs)
    logger, xml_logger = setup_logging(args, stats)
    
    setup_env(args)
    
    tests, unittests = discover_tests(args, parser)
    test_objects = [Test(t) for t in tests]
    
    if args.list_only:
        for t in test_objects:
            print(t.path)
        sys.exit(0)

    stats.total_num_tests = len(test_objects)
    
    context = create_run_context(args, stats, logger, unittests)
    
    execute_tests(test_objects, context)
    display_results(context, test_objects, xml_logger)

if __name__ == "__main__":
    main()