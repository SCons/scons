"""
A testing framework for commands and scripts.

The TestCmd module provides a framework for portable automated testing
of executable commands and scripts (in any language, not just Python),
especially commands and scripts that require file system interaction.

In addition to running tests and evaluating conditions, the TestCmd
module manages and cleans up one or more temporary workspace
directories, and provides methods for creating files and directories in
those workspace directories from in-line data, here-documents), allowing
tests to be completely self-contained.

A TestCmd environment object is created via the usual invocation:

    import TestCmd
    test = TestCmd.TestCmd()

There are a bunch of keyword arguments available at instantiation:

    test = TestCmd.TestCmd(
        description='string',
        program='program_or_script_to_test',
        interpreter='script_interpreter',
        workdir='prefix',
        subdir='subdir',
        verbose=Boolean,
        match=default_match_function,
        match_stdout=default_match_stdout_function,
        match_stderr=default_match_stderr_function,
        diff=default_diff_stderr_function,
        diff_stdout=default_diff_stdout_function,
        diff_stderr=default_diff_stderr_function,
        combine=Boolean,
    )

There are a bunch of methods that let you do different things:

    test.verbose_set(1)

    test.description_set('string')

    test.program_set('program_or_script_to_test')

    test.interpreter_set('script_interpreter')
    test.interpreter_set(['script_interpreter', 'arg'])

    test.workdir_set('prefix')
    test.workdir_set('')

    test.workpath('file')
    test.workpath('subdir', 'file')

    test.subdir('subdir', ...)

    test.rmdir('subdir', ...)

    test.write('file', "contents\n")
    test.write(['subdir', 'file'], "contents\n")

    test.read('file')
    test.read(['subdir', 'file'])
    test.read('file', mode)
    test.read(['subdir', 'file'], mode)

    test.writable('dir', 1)
    test.writable('dir', None)

    test.preserve(condition, ...)

    test.cleanup(condition)

    test.command_args(
        program='program_or_script_to_run',
        interpreter='script_interpreter',
        arguments='arguments to pass to program',
    )

    test.run(
        program='program_or_script_to_run',
        interpreter='script_interpreter',
        arguments='arguments to pass to program',
        chdir='directory_to_chdir_to',
        stdin='input to feed to the program\n',
        universal_newlines=True,
    )

    p = test.start(
        program='program_or_script_to_run',
        interpreter='script_interpreter',
        arguments='arguments to pass to program',
        universal_newlines=None,
    )

    test.finish(self, p)

    test.pass_test()
    test.pass_test(condition)
    test.pass_test(condition, function)

    test.fail_test()
    test.fail_test(condition)
    test.fail_test(condition, function)
    test.fail_test(condition, function, skip)
    test.fail_test(condition, function, skip, message)

    test.no_result()
    test.no_result(condition)
    test.no_result(condition, function)
    test.no_result(condition, function, skip)

    test.stdout()
    test.stdout(run)

    test.stderr()
    test.stderr(run)

    test.symlink(target, link)

    test.banner(string)
    test.banner(string, width)

    test.diff(actual, expected)

    test.diff_stderr(actual, expected)

    test.diff_stdout(actual, expected)

    test.match(actual, expected)

    test.match_stderr(actual, expected)

    test.match_stdout(actual, expected)

    test.set_match_function(match, stdout, stderr)

    test.match_exact("actual 1\nactual 2\n", "expected 1\nexpected 2\n")
    test.match_exact(["actual 1\n", "actual 2\n"],
                     ["expected 1\n", "expected 2\n"])
    test.match_caseinsensitive("Actual 1\nACTUAL 2\n", "expected 1\nEXPECTED 2\n")

    test.match_re("actual 1\nactual 2\n", regex_string)
    test.match_re(["actual 1\n", "actual 2\n"], list_of_regexes)

    test.match_re_dotall("actual 1\nactual 2\n", regex_string)
    test.match_re_dotall(["actual 1\n", "actual 2\n"], list_of_regexes)

    test.tempdir()
    test.tempdir('temporary-directory')

    test.sleep()
    test.sleep(seconds)

    test.where_is('foo')
    test.where_is('foo', 'PATH1:PATH2')
    test.where_is('foo', 'PATH1;PATH2', '.suffix3;.suffix4')

    test.unlink('file')
    test.unlink('subdir', 'file')

The TestCmd module provides pass_test(), fail_test(), and no_result()
unbound functions that report test results for use with the Aegis change
management system.  These methods terminate the test immediately,
reporting PASSED, FAILED, or NO RESULT respectively, and exiting with
status 0 (success), 1 or 2 respectively.  This allows for a distinction
between an actual failed test and a test that could not be properly
evaluated because of an external condition (such as a full file system
or incorrect permissions).

    import TestCmd

    TestCmd.pass_test()
    TestCmd.pass_test(condition)
    TestCmd.pass_test(condition, function)

    TestCmd.fail_test()
    TestCmd.fail_test(condition)
    TestCmd.fail_test(condition, function)
    TestCmd.fail_test(condition, function, skip)
    TestCmd.fail_test(condition, function, skip, message)

    TestCmd.no_result()
    TestCmd.no_result(condition)
    TestCmd.no_result(condition, function)
    TestCmd.no_result(condition, function, skip)

The TestCmd module also provides unbound global functions that handle
matching in the same way as the match_*() methods described above.

    import TestCmd

    test = TestCmd.TestCmd(match=TestCmd.match_exact)

    test = TestCmd.TestCmd(match=TestCmd.match_caseinsensitive)

    test = TestCmd.TestCmd(match=TestCmd.match_re)

    test = TestCmd.TestCmd(match=TestCmd.match_re_dotall)

These functions are also available as static methods:

    import TestCmd

    test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_exact)

    test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_caseinsensitive)

    test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_re)

    test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_re_dotall)

These static methods can be accessed by a string naming the method:

    import TestCmd

    test = TestCmd.TestCmd(match='match_exact')

    test = TestCmd.TestCmd(match='match_caseinsensitive')

    test = TestCmd.TestCmd(match='match_re')

    test = TestCmd.TestCmd(match='match_re_dotall')

The TestCmd module provides unbound global functions that can be used
for the "diff" argument to TestCmd.TestCmd instantiation:

    import TestCmd

    test = TestCmd.TestCmd(match=TestCmd.match_re, diff=TestCmd.diff_re)

    test = TestCmd.TestCmd(diff=TestCmd.simple_diff)

    test = TestCmd.TestCmd(diff=TestCmd.context_diff)

    test = TestCmd.TestCmd(diff=TestCmd.unified_diff)

These functions are also available as static methods:

    import TestCmd

    test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_re, diff=TestCmd.TestCmd.diff_re)

    test = TestCmd.TestCmd(diff=TestCmd.TestCmd.simple_diff)

    test = TestCmd.TestCmd(diff=TestCmd.TestCmd.context_diff)

    test = TestCmd.TestCmd(diff=TestCmd.TestCmd.unified_diff)

These static methods can be accessed by a string naming the method:

    import TestCmd

    test = TestCmd.TestCmd(match='match_re', diff='diff_re')

    test = TestCmd.TestCmd(diff='simple_diff')

    test = TestCmd.TestCmd(diff='context_diff')

    test = TestCmd.TestCmd(diff='unified_diff')

The "diff" argument can also be used with standard difflib functions:

    import difflib

    test = TestCmd.TestCmd(diff=difflib.context_diff)

    test = TestCmd.TestCmd(diff=difflib.unified_diff)

Lastly, the where_is() method also exists in an unbound function
version.

    import TestCmd

    TestCmd.where_is('foo')
    TestCmd.where_is('foo', 'PATH1:PATH2')
    TestCmd.where_is('foo', 'PATH1;PATH2', '.suffix3;.suffix4')
"""

# Copyright 2000-2010 Steven Knight
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

__author__ = "Steven Knight <knight at baldmt dot com>"
__revision__ = "TestCmd.py 1.3.D001 2010/06/03 12:58:27 knight"
__version__ = "1.3"

import atexit
import difflib
import errno
import hashlib
import os
import re
try:
    import psutil
except ImportError:
    HAVE_PSUTIL = False
else:
    HAVE_PSUTIL = True
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from collections import UserList, UserString
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import Optional

IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_64_BIT = sys.maxsize > 2**32
IS_PYPY = hasattr(sys, 'pypy_translation_info')
NEED_HELPER = os.environ.get('SCONS_NO_DIRECT_SCRIPT')

# sentinel for cases where None won't do
_Null = object()

__all__ = [
    'diff_re',
    'fail_test',
    'no_result',
    'pass_test',
    'match_exact',
    'match_caseinsensitive',
    'match_re',
    'match_re_dotall',
    'python',
    '_python_',
    'TestCmd',
    'to_bytes',
    'to_str',
]


def is_List(e):
    return isinstance(e, (list, UserList))


def to_bytes(s):
    if isinstance(s, bytes):
        return s
    return bytes(s, 'utf-8')


def to_str(s):
    if is_String(s):
        return s
    return str(s, 'utf-8')


def is_String(e):
    return isinstance(e, (str, UserString))

testprefix = 'testcmd.'
if os.name in ('posix', 'nt'):
    testprefix += f"{os.getpid()}."

re_space = re.compile(r'\s')


def _caller(tblist, skip):
    string = ""
    arr = []
    for file, line, name, text in tblist:
        if file[-10:] == "TestCmd.py":
            break
        arr = [(file, line, name, text)] + arr
    atfrom = "at"
    for file, line, name, text in arr[skip:]:
        if name in ("?", "<module>"):
            name = ""
        else:
            name = f" ({name})"
        string = string + ("%s line %d of %s%s\n" % (atfrom, line, file, name))
        atfrom = "\tfrom"
    return string


def clean_up_ninja_daemon(self, result_type) -> None:
    """
    Kill any running scons daemon started by ninja and clean up

    Working directory and temp files are removed.
    Skipped if this platform doesn't have psutil (e.g. msys2 on Windows)
    """
    if not self:
        return

    for path in Path(self.workdir).rglob('.ninja'):
        daemon_dir = Path(tempfile.gettempdir()) / (
            f"scons_daemon_{str(hashlib.md5(str(path.resolve()).encode()).hexdigest())}"
        )
        pidfiles = [daemon_dir / 'pidfile', path / 'scons_daemon_dirty']
        for pidfile in pidfiles:
            if pidfile.exists():
                with open(pidfile) as f:
                    try:
                        pid = int(f.read())
                        os.kill(pid, signal.SIGINT)
                    except OSError:
                        pass

                    while HAVE_PSUTIL:
                        if pid not in [proc.pid for proc in psutil.process_iter()]:
                            break
                        else:
                            time.sleep(0.1)

        if not self._preserve[result_type]:
            if daemon_dir.exists():
                shutil.rmtree(daemon_dir)


def fail_test(self=None, condition=True, function=None, skip=0, message=None):
    """Causes a test to exit with a fail.

    Reports that the test FAILED and exits with a status of 1, unless
    a condition argument is supplied; if so the completion processing
    takes place only if the condition is true.

    Args:
        self: a test class instance. Must be passed in explicitly
            by the caller since this is an unbound method.
        condition (optional): if false, return to let test continue.
        function (optional): function to call before completion processing.
        skip (optional): how many lines at the top of the traceback to skip.
        message (optional): additional text to include in the fail message.
    """
    if not condition:
        return
    if function is not None:
        function()
    clean_up_ninja_daemon(self, 'fail_test')
    of = ""
    desc = ""
    sep = " "
    if self is not None:
        if self.program:
            of = f" of {self.program}"
            sep = "\n\t"
        if self.description:
            desc = f" [{self.description}]"
            sep = "\n\t"

    at = _caller(traceback.extract_stack(), skip)
    if message:
        msg = f"\t{message}\n"
    else:
        msg = ""
    sys.stderr.write(f"FAILED test{of}{desc}{sep}{at}{msg}")

    sys.exit(1)


def no_result(self=None, condition=True, function=None, skip=0):
    """Causes a test to exit with a no result.

    In testing parlance NO RESULT means the test could not be completed
    for reasons that imply neither success nor failure - for example a
    component needed to run the test could be found. However, at this
    point we still have an "outcome", so record the information and exit
    with a status code of 2, unless a condition argument is supplied;
    if so the completion processing takes place only if the condition is true.

    The different exit code and message allows other logic to distinguish
    from a fail and decide how to treat NO RESULT tests.

    Args:
        self: a test class instance. Must be passed in explicitly
            by the caller since this is an unbound method.
        condition (optional): if false, return to let test continue.
        function (optional): function to call before completion processing.
        skip (optional): how many lines at the top of the traceback to skip.
    """
    if not condition:
        return
    if function is not None:
        function()
    clean_up_ninja_daemon(self, 'no_result')
    of = ""
    desc = ""
    sep = " "
    if self is not None:
        if self.program:
            of = f" of {self.program}"
            sep = "\n\t"
        if self.description:
            desc = f" [{self.description}]"
            sep = "\n\t"

    at = _caller(traceback.extract_stack(), skip)
    sys.stderr.write(f"NO RESULT for test{of}{desc}{sep}{at}")

    sys.exit(2)


def pass_test(self=None, condition=True, function=None):
    """Causes a test to exit with a pass.

    Reports that the test PASSED and exits with a status of 0, unless
    a condition argument is supplied; if so the completion processing
    takes place only if the condition is true.

    the test passes only if the condition is true.

    Args:
        self: a test class instance. Must be passed in explicitly
            by the caller since this is an unbound method.
        condition (optional): if false, return to let test continue.
        function (optional): function to call before completion processing.
    """
    if not condition:
        return
    if function is not None:
        function()
    clean_up_ninja_daemon(self, 'pass_test')
    sys.stderr.write("PASSED\n")
    sys.exit(0)


def match_exact(lines=None, matches=None, newline=os.sep):
    """Match function using exact match.

    :param lines: data lines
    :type lines: str or list[str]
    :param matches: expected lines to match
    :type matches: str or list[str]
    :param newline: line separator
    :returns: None on failure, 1 on success.

    """
    if isinstance(lines, bytes):
        newline = to_bytes(newline)

    if not is_List(lines):
        lines = lines.split(newline)
    if not is_List(matches):
        matches = matches.split(newline)
    if len(lines) != len(matches):
        return None
    for line, match in zip(lines, matches):
        if line != match:
            return None
    return 1


def match_caseinsensitive(lines=None, matches=None):
    """Match function using case-insensitive matching.

    Only a simplistic comparison is done, based on casefolding
    the strings. This may still fail but is the suggestion of
    the Unicode Standard.

    :param lines: data lines
    :type lines: str or list[str]
    :param matches: expected lines to match
    :type matches: str or list[str]
    :returns: None on failure, 1 on success.

    """
    if not is_List(lines):
        lines = lines.split("\n")
    if not is_List(matches):
        matches = matches.split("\n")
    if len(lines) != len(matches):
        return None
    for line, match in zip(lines, matches):
        if line.casefold() != match.casefold():
            return None
    return 1


def match_re(lines=None, res=None):
    """Match function using line-by-line regular expression match.

    :param lines: data lines
    :type lines: str or list[str]
    :param res: regular expression(s) for matching
    :type res: str or list[str]
    :returns: None on failure, 1 on success.

    """
    if not is_List(lines):
        # CRs mess up matching (Windows) so split carefully
        lines = re.split('\r?\n', lines)
    if not is_List(res):
        res = res.split("\n")
    if len(lines) != len(res):
        print(f"match_re: expected {len(res)} lines, found {len(lines)}")
        return None
    for i, (line, regex) in enumerate(zip(lines, res)):
        s = r"^{}$".format(regex)
        try:
            expr = re.compile(s)
        except re.error as e:
            msg = "Regular expression error in %s: %s"
            raise re.error(msg % (repr(s), e.args[0]))
        if not expr.search(line):
            miss_tmpl = "match_re: mismatch at line {}:\n  search re='{}'\n  line='{}'"
            print(miss_tmpl.format(i, s, line))
            return None
    return 1


def match_re_dotall(lines=None, res=None):
    """Match function using regular expression match.

    Unlike match_re, the arguments are converted to strings (if necessary)
    and must match exactly.

    :param lines: data lines
    :type lines: str or list[str]
    :param res: regular expression(s) for matching
    :type res: str or list[str]
    :returns: a match object on match, else None, like re.match

    """
    if not isinstance(lines, str):
        lines = "\n".join(lines)
    if not isinstance(res, str):
        res = "\n".join(res)
    s = r"^{}$".format(res)
    try:
        expr = re.compile(s, re.DOTALL)
    except re.error as e:
        msg = "Regular expression error in %s: %s"
        raise re.error(msg % (repr(s), e.args[0]))
    return expr.match(lines)


def simple_diff(a, b, fromfile='', tofile='',
                fromfiledate='', tofiledate='', n=0, lineterm=''):
    r"""Compare two sequences of lines; generate the delta as a simple diff.

    Similar to difflib.context_diff and difflib.unified_diff but
    output is like from the "diff" command without arguments. The function
    keeps the same signature as the difflib ones so they will be
    interchangeable,  but except for lineterm, the arguments beyond the
    two sequences are ignored in this version. By default, the
    diff is not created with trailing newlines, set the lineterm
    argument to '\n' to do so.

    Example:

    >>> print(''.join(simple_diff('one\ntwo\nthree\nfour\n'.splitlines(True),
    ...       'zero\none\ntree\nfour\n'.splitlines(True), lineterm='\n')))
    0a1
    > zero
    2,3c3
    < two
    < three
    ---
    > tree

    """
    a = [to_str(q) for q in a]
    b = [to_str(q) for q in b]
    sm = difflib.SequenceMatcher(None, a, b)

    def comma(x1, x2):
        return x1 + 1 == x2 and str(x2) or f'{x1 + 1},{x2}'

    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'delete':
            yield f"{comma(a1, a2)}d{b1}{lineterm}"
            for l in a[a1:a2]:
                yield f"< {l}"
        elif op == 'insert':
            yield f"{a1}a{comma(b1, b2)}{lineterm}"
            for l in b[b1:b2]:
                yield f"> {l}"
        elif op == 'replace':
            yield f"{comma(a1, a2)}c{comma(b1, b2)}{lineterm}"
            for l in a[a1:a2]:
                yield f"< {l}"
            yield f'---{lineterm}'
            for l in b[b1:b2]:
                yield f"> {l}"


def diff_re(a, b, fromfile='', tofile='',
            fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    """Compare a and b (lists of strings) where a are regular expressions.

    A simple "diff" of two sets of lines when the expected lines
    are regular expressions.  This is a really dumb thing that
    just compares each line in turn, so it doesn't look for
    chunks of matching lines and the like--but at least it lets
    you know exactly which line first didn't compare correctl...

    Raises:
        re.error: if a regex fails to compile
    """
    result = []
    diff = len(a) - len(b)
    if diff < 0:
        a = a + [''] * (-diff)
    elif diff > 0:
        b = b + [''] * diff
    for i, (aline, bline) in enumerate(zip(a, b)):
        s = r"^{}$".format(aline)
        try:
            expr = re.compile(s)
        except re.error as e:
            msg = "Regular expression error in %s: %s"
            raise re.error(msg % (repr(s), e.args[0]))
        if not expr.search(bline):
            result.append(f"{i + 1}c{i + 1}")
            result.append(f"< {repr(a[i])}")
            result.append('---')
            result.append(f"> {repr(b[i])}")
    return result


if os.name == 'posix':
    def escape(arg):
        """escape shell special characters"""
        slash = '\\'
        special = '"$'
        arg = arg.replace(slash, slash + slash)
        for c in special:
            arg = arg.replace(c, slash + c)
        if re_space.search(arg):
            arg = f"\"{arg}\""
        return arg
else:
    # Windows does not allow special characters in file names
    # anyway, so no need for an escape function, we will just quote
    # the arg.
    def escape(arg):
        if re_space.search(arg):
            arg = f"\"{arg}\""
        return arg

if os.name == 'java':
    python = os.path.join(sys.prefix, 'jython')
else:
    python = os.environ.get('python_executable', sys.executable)
_python_ = escape(python)

if sys.platform == 'win32':

    default_sleep_seconds = 2

    def where_is(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = path.split(os.pathsep)
        if pathext is None:
            pathext = os.environ['PATHEXT']
        if is_String(pathext):
            pathext = pathext.split(os.pathsep)
        for ext in pathext:
            if ext.casefold() == file[-len(ext):].casefold():
                pathext = ['']
                break
        for dir in path:
            f = os.path.join(dir, file)
            for ext in pathext:
                fext = f + ext
                if os.path.isfile(fext):
                    return fext
        return None

else:

    def where_is(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = path.split(os.pathsep)
        for dir in path:
            f = os.path.join(dir, file)
            if os.path.isfile(f):
                try:
                    st = os.stat(f)
                except OSError:
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0o111:
                    return f
        return None

    default_sleep_seconds = 1


# From Josiah Carlson,
# ASPN : Python Cookbook : Module to allow Asynchronous subprocess use on Windows and Posix platforms
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/440554

if sys.platform == 'win32':  # and subprocess.mswindows:
    try:
        from win32file import ReadFile, WriteFile
        from win32pipe import PeekNamedPipe
    except ImportError:
        # If PyWin32 is not available, try ctypes instead
        # XXX These replicate _just_enough_ PyWin32 behaviour for our purposes
        import ctypes
        from ctypes.wintypes import DWORD

        def ReadFile(hFile, bufSize, ol=None):
            assert ol is None
            lpBuffer = ctypes.create_string_buffer(bufSize)
            bytesRead = DWORD()
            bErr = ctypes.windll.kernel32.ReadFile(
                hFile, lpBuffer, bufSize, ctypes.byref(bytesRead), ol)
            if not bErr:
                raise ctypes.WinError()
            return (0, ctypes.string_at(lpBuffer, bytesRead.value))

        def WriteFile(hFile, data, ol=None):
            assert ol is None
            bytesWritten = DWORD()
            bErr = ctypes.windll.kernel32.WriteFile(
                hFile, data, len(data), ctypes.byref(bytesWritten), ol)
            if not bErr:
                raise ctypes.WinError()
            return (0, bytesWritten.value)

        def PeekNamedPipe(hPipe, size):
            assert size == 0
            bytesAvail = DWORD()
            bErr = ctypes.windll.kernel32.PeekNamedPipe(
                hPipe, None, size, None, ctypes.byref(bytesAvail), None)
            if not bErr:
                raise ctypes.WinError()
            return ("", bytesAvail.value, None)
    import msvcrt
else:
    import select
    import fcntl

    try:
        fcntl.F_GETFL
    except AttributeError:
        fcntl.F_GETFL = 3

    try:
        fcntl.F_SETFL
    except AttributeError:
        fcntl.F_SETFL = 4


class Popen(subprocess.Popen):
    def recv(self, maxsize=None):
        return self._recv('stdout', maxsize)

    def recv_err(self, maxsize=None):
        return self._recv('stderr', maxsize)

    def send_recv(self, input='', maxsize=None):
        return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize

    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    if sys.platform == 'win32':  # and subprocess.mswindows:
        def send(self, input):
            input = to_bytes(input)
            if not self.stdin:
                return None

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input)
            except ValueError:
                return self._close('stdin')
            except (subprocess.pywintypes.error, Exception) as why:
                if why.args[0] in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except (subprocess.pywintypes.error, Exception) as why:
                if why.args[0] in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise

            # if self.universal_newlines:
            #    read = self._translate_newlines(read)
            return read

    else:
        def send(self, input):
            if not self.stdin:
                return None

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(),
                                   bytearray(input, 'utf-8'))
            except OSError as why:
                if why.args[0] == errno.EPIPE:  # broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            try:
                flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            except TypeError:
                flags = None
            else:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            try:
                if not select.select([conn], [], [], 0)[0]:
                    return ''

                r = conn.read(maxsize)
                if not r:
                    return self._close(which)

                # if self.universal_newlines:
                #    r = self._translate_newlines(r)
                return r
            finally:
                if not conn.closed and flags is not None:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)


disconnect_message = "Other end disconnected!"


def recv_some(p, t=.1, e=1, tr=5, stderr=0):
    if tr < 1:
        tr = 1
    x = time.time() + t
    y = []
    r = ''
    pr = p.recv
    if stderr:
        pr = p.recv_err
    while time.time() < x or r:
        r = pr()
        if r is None:
            if e:
                raise Exception(disconnect_message)
            else:
                break
        elif r:
            y.append(r)
        else:
            time.sleep(max((x - time.time()) / tr, 0))
    return ''.join(y)


def send_all(p, data):
    while len(data):
        sent = p.send(data)
        if sent is None:
            raise Exception(disconnect_message)
        data = memoryview(data)[sent:]


_Cleanup = []


@atexit.register
def _clean():
    global _Cleanup
    cleanlist = [c for c in _Cleanup if c]
    del _Cleanup[:]
    cleanlist.reverse()
    for test in cleanlist:
        test.cleanup()


class TestCmd:
    """Class TestCmd"""

    def __init__(
        self,
        description=None,
        program=None,
        interpreter=None,
        workdir=None,
        subdir=None,
        verbose=None,
        match=None,
        match_stdout=None,
        match_stderr=None,
        diff=None,
        diff_stdout=None,
        diff_stderr=None,
        combine=0,
        universal_newlines=True,
        timeout=None,
    ):
        self.external = os.environ.get('SCONS_EXTERNAL_TEST', 0)
        self._cwd = os.getcwd()
        self.description_set(description)
        self.program_set(program)
        self.interpreter_set(interpreter)
        if verbose is None:
            try:
                verbose = max(0, int(os.environ.get('TESTCMD_VERBOSE', 0)))
            except ValueError:
                verbose = 0
        self.verbose_set(verbose)
        self.combine = combine
        self.universal_newlines = universal_newlines
        self.process = None
        # Two layers of timeout: one at the test class instance level,
        # one set on an individual start() call (usually via a run() call)
        self.timeout = timeout
        self.start_timeout = None
        self.set_match_function(match, match_stdout, match_stderr)
        self.set_diff_function(diff, diff_stdout, diff_stderr)
        self._dirlist = []
        self._preserve = {'pass_test': 0, 'fail_test': 0, 'no_result': 0}
        preserve_value = os.environ.get('PRESERVE', False)
        if preserve_value not in [0, '0', 'False']:
            self._preserve['pass_test'] = os.environ['PRESERVE']
            self._preserve['fail_test'] = os.environ['PRESERVE']
            self._preserve['no_result'] = os.environ['PRESERVE']
        else:
            try:
                self._preserve['pass_test'] = os.environ['PRESERVE_PASS']
            except KeyError:
                pass
            try:
                self._preserve['fail_test'] = os.environ['PRESERVE_FAIL']
            except KeyError:
                pass
            try:
                self._preserve['no_result'] = os.environ['PRESERVE_NO_RESULT']
            except KeyError:
                pass
        self._stdout = []
        self._stderr = []
        self.status = None
        self.condition = 'no_result'
        self.workdir_set(workdir)
        self.subdir(subdir)

        try:
            self.fixture_dirs = (os.environ['FIXTURE_DIRS']).split(os.pathsep)
        except KeyError:
            self.fixture_dirs = []


    def __del__(self):
        self.cleanup()

    def __repr__(self):
        return f"{id(self):x}"

    banner_char = '='
    banner_width = 80

    def banner(self, s, width=None):
        if width is None:
            width = self.banner_width
        return f"{s:{self.banner_char}<{width}}"

    escape = staticmethod(escape)

    def canonicalize(self, path):
        if is_List(path):
            path = os.path.join(*path)
        if not os.path.isabs(path):
            path = os.path.join(self.workdir, path)
        return path

    def chmod(self, path, mode):
        """Changes permissions on the specified file or directory."""
        path = self.canonicalize(path)
        os.chmod(path, mode)

    def cleanup(self, condition=None):
        """Removes any temporary working directories.

        Cleans the TestCmd instance.  If the environment variable PRESERVE was
        set when the TestCmd environment was created, temporary working
        directories are not removed.  If any of the environment variables
        PRESERVE_PASS, PRESERVE_FAIL, or PRESERVE_NO_RESULT were set
        when the TestCmd environment was created, then temporary working
        directories are not removed if the test passed, failed, or had
        no result, respectively.  Temporary working directories are also
        preserved for conditions specified via the preserve method.

        Typically, this method is not called directly, but is used when
        the script exits to clean up temporary working directories as
        appropriate for the exit status.
        """
        if not self._dirlist:
            return
        os.chdir(self._cwd)
        self.workdir = None
        if condition is None:
            condition = self.condition
        if self._preserve[condition]:
            for dir in self._dirlist:
                print(f"Preserved directory {dir}")
        else:
            list = self._dirlist[:]
            list.reverse()
            for dir in list:
                self.writable(dir, 1)
                shutil.rmtree(dir, ignore_errors=1)
            self._dirlist = []

            global _Cleanup
            if self in _Cleanup:
                _Cleanup.remove(self)

    def command_args(self, program=None, interpreter=None, arguments=None):
        if not self.external:
            if program:
                if isinstance(program, str) and not os.path.isabs(program):
                    program = os.path.join(self._cwd, program)
            else:
                program = self.program
                if not interpreter:
                    interpreter = self.interpreter
        else:
            if not program:
                program = self.program
                if not interpreter:
                    interpreter = self.interpreter
        if not isinstance(program, (list, tuple)):
            program = [program]
        cmd = list(program)
        if interpreter:
            if not isinstance(interpreter, (list, tuple)):
                interpreter = [interpreter]
            cmd = list(interpreter) + cmd
        if arguments:
            if isinstance(arguments, dict):
                cmd.extend([f"{k}={v}" for k, v in arguments.items()])
                return cmd
            if isinstance(arguments, str):
                arguments = arguments.split()
            cmd.extend(arguments)
        return cmd

    def description_set(self, description):
        """Set the description of the functionality being tested. """
        self.description = description

    def set_diff_function(self, diff=_Null, stdout=_Null, stderr=_Null):
        """Sets the specified diff functions."""
        if diff is not _Null:
            self._diff_function = diff
        if stdout is not _Null:
            self._diff_stdout_function = stdout
        if stderr is not _Null:
            self._diff_stderr_function = stderr

    def diff(self, a, b, name=None, diff_function=None, *args, **kw):
        if diff_function is None:
            try:
                diff_function = getattr(self, self._diff_function)
            except TypeError:
                diff_function = self._diff_function
                if diff_function is None:
                    diff_function = self.simple_diff
        if name is not None:
            print(self.banner(name))

        if not is_List(a):
            a=a.splitlines()
        if not is_List(b):
            b=b.splitlines()

        args = (a, b) + args
        for line in diff_function(*args, **kw):
            print(line)

    def diff_stderr(self, a, b, *args, **kw):
        """Compare actual and expected file contents."""
        try:
            diff_stderr_function = getattr(self, self._diff_stderr_function)
        except TypeError:
            diff_stderr_function = self._diff_stderr_function
        return self.diff(a, b, diff_function=diff_stderr_function, *args, **kw)

    def diff_stdout(self, a, b, *args, **kw):
        """Compare actual and expected file contents."""
        try:
            diff_stdout_function = getattr(self, self._diff_stdout_function)
        except TypeError:
            diff_stdout_function = self._diff_stdout_function
        return self.diff(a, b, diff_function=diff_stdout_function, *args, **kw)

    simple_diff = staticmethod(simple_diff)

    diff_re = staticmethod(diff_re)

    context_diff = staticmethod(difflib.context_diff)

    unified_diff = staticmethod(difflib.unified_diff)

    def fail_test(self, condition=True, function=None, skip=0, message=None):
        """Cause the test to fail."""
        if not condition:
            return
        self.condition = 'fail_test'
        fail_test(self=self,
                  condition=condition,
                  function=function,
                  skip=skip,
                  message=message)

    def interpreter_set(self, interpreter):
        """Set the program to be used to interpret the program
        under test as a script.
        """
        self.interpreter = interpreter

    def set_match_function(self, match=_Null, stdout=_Null, stderr=_Null):
        """Sets the specified match functions. """
        if match is not _Null:
            self._match_function = match
        if stdout is not _Null:
            self._match_stdout_function = stdout
        if stderr is not _Null:
            self._match_stderr_function = stderr

    def match(self, lines, matches):
        """Compare actual and expected file contents."""
        try:
            match_function = getattr(self, self._match_function)
        except TypeError:
            match_function = self._match_function
            if match_function is None:
                # Default is regular expression matches.
                match_function = self.match_re
        return match_function(lines, matches)

    def match_stderr(self, lines, matches):
        """Compare actual and expected file contents."""
        try:
            match_stderr_function = getattr(self, self._match_stderr_function)
        except TypeError:
            match_stderr_function = self._match_stderr_function
            if match_stderr_function is None:
                # Default is to use whatever match= is set to.
                match_stderr_function = self.match
        return match_stderr_function(lines, matches)

    def match_stdout(self, lines, matches):
        """Compare actual and expected file contents."""
        try:
            match_stdout_function = getattr(self, self._match_stdout_function)
        except TypeError:
            match_stdout_function = self._match_stdout_function
            if match_stdout_function is None:
                # Default is to use whatever match= is set to.
                match_stdout_function = self.match
        return match_stdout_function(lines, matches)

    match_exact = staticmethod(match_exact)

    match_caseinsensitive = staticmethod(match_caseinsensitive)

    match_re = staticmethod(match_re)

    match_re_dotall = staticmethod(match_re_dotall)

    def no_result(self, condition=True, function=None, skip=0):
        """Report that the test could not be run."""
        if not condition:
            return
        self.condition = 'no_result'
        no_result(self=self,
                  condition=condition,
                  function=function,
                  skip=skip)

    def pass_test(self, condition=True, function=None):
        """Cause the test to pass."""
        if not condition:
            return
        self.condition = 'pass_test'
        pass_test(self=self, condition=condition, function=function)

    def preserve(self, *conditions):
        """Preserves temporary working directories.

        Arrange for the temporary working directories for the
        specified TestCmd environment to be preserved for one or more
        conditions.  If no conditions are specified, arranges for
        the temporary working directories to be preserved for all
        conditions.
        """
        if not conditions:
            conditions = ('pass_test', 'fail_test', 'no_result')
        for cond in conditions:
            self._preserve[cond] = 1

    def program_set(self, program):
        """Sets the executable program or script to be tested."""
        if not self.external:
            if program and not os.path.isabs(program):
                program = os.path.join(self._cwd, program)
        self.program = program

    def read(self, file, mode='rb', newline=None):
        """Reads and returns the contents of the specified file name.

        The file name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The file is
        assumed to be under the temporary working directory unless it
        is an absolute path name.  The I/O mode for the file may
        be specified; it must begin with an 'r'.  The default is
        'rb' (binary read).
        """
        file = self.canonicalize(file)
        if mode[0] != 'r':
            raise ValueError("mode must begin with 'r'")
        if 'b' not in mode:
            with open(file, mode, newline=newline) as f:
                return f.read()
        else:
            with open(file, mode) as f:
                return f.read()

    def rmdir(self, dir):
        """Removes the specified dir name.

        The dir name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The dir is
        assumed to be under the temporary working directory unless it
        is an absolute path name.
        The dir must be empty.
        """
        dir = self.canonicalize(dir)
        os.rmdir(dir)


    def parse_path(self, path, suppress_current=False):
        """Return a list with the single path components of path."""
        head, tail = os.path.split(path)
        result = []
        if not tail:
            if head == path:
                return [head]
        else:
            result.append(tail)
        head, tail = os.path.split(head)
        while head and tail:
            result.append(tail)
            head, tail = os.path.split(head)
        result.append(head or tail)
        result.reverse()

        return result

    def dir_fixture(self, srcdir, dstdir=None):
        """ Copies the contents of the fixture directory to the test directory.

        If srcdir is an absolute path, it is tried directly, else
        the fixture_dirs are searched in order to find the named fixture
        directory.  To tightly control the search order, the harness may
        be called with FIXTURE_DIRS set including the test source directory
        in the desired position, else it will be tried last.

        If dstdir not an absolute path, it is taken as a destination under
        the working dir (if omitted of the default None indicates '.',
        aka the test dir).  dstdir is created automatically if needed.

        srcdir or dstdir may be a list, in which case the elements are first
        joined into a pathname.
        """
        if is_List(srcdir):
            srcdir = os.path.join(*srcdir)
        spath = srcdir
        if srcdir and self.fixture_dirs and not os.path.isabs(srcdir):
            for dir in self.fixture_dirs:
                spath = os.path.join(dir, srcdir)
                if os.path.isdir(spath):
                    break
            else:
                spath = srcdir

        if not dstdir or dstdir == '.':
            dstdir = self.workdir
        else:
            if is_List(dstdir):
                dstdir = os.path.join(*dstdir)
            if os.path.isabs(dstdir):
                os.makedirs(dstdir, exist_ok=True)
            else:
                dstlist = self.parse_path(dstdir)
                if dstlist and dstlist[0] == ".":
                    dstdir = os.path.join(dstlist[1:])
                self.subdir(dstdir)

        for entry in os.listdir(spath):
            epath = os.path.join(spath, entry)
            dpath = os.path.join(dstdir, entry)
            if os.path.isdir(epath):
                # Copy the subfolder
                shutil.copytree(epath, dpath)
            else:
                shutil.copy(epath, dpath)

    def file_fixture(self, srcfile, dstfile=None):
        """ Copies a fixture file to the test directory, optionally renaming.

        If srcfile is an absolute path, it is tried directly, else
        the fixture_dirs are searched in order to find the named fixture
        file.  To tightly control the search order, the harness may
        be called with FIXTURE_DIRS also including the test source directory
        in the desired place, it will otherwise be tried last.

        dstfile is the name to give the copied file; if the argument
        is omitted the basename of srcfile is used. If dstfile is not
        an absolute path name.  Any directory components of dstfile are
        created automatically if needed.

        srcfile or dstfile may be a list, in which case the elements are first
        joined into a pathname.
        """
        if is_List(srcfile):
            srcfile = os.path.join(*srcfile)

        srcpath, srctail = os.path.split(srcfile)
        spath = srcfile
        if srcfile and self.fixture_dirs and not os.path.isabs(srcfile):
            for dir in self.fixture_dirs:
                spath = os.path.join(dir, srcfile)
                if os.path.isfile(spath):
                    break
            else:
                spath = srcfile

        if not dstfile:
            if srctail:
                dpath = os.path.join(self.workdir, srctail)
            else:
                return
        else:
            dstdir, dsttail = os.path.split(dstfile)
            if dstdir:
                # if dstfile has a dir part, and is not abspath, create
                if os.path.isabs(dstdir):
                    os.makedirs(dstdir, exist_ok=True)
                    dpath = dstfile
                else:
                    dstlist = self.parse_path(dstdir)
                    if dstlist and dstlist[0] == ".":
                        # strip leading ./ if present
                        dstdir = os.path.join(dstlist[1:])
                    self.subdir(dstdir)
                    dpath = os.path.join(self.workdir, dstfile)
            else:
                dpath = os.path.join(self.workdir, dstfile)

        shutil.copy(spath, dpath)

    def start(self, program=None,
              interpreter=None,
              arguments=None,
              universal_newlines=None,
              timeout=None,
              **kw):
        """ Starts a program or script for the test environment.

        The specified program will have the original directory
        prepended unless it is enclosed in a [list].
        """
        cmd = self.command_args(program, interpreter, arguments)
        if self.verbose:
            cmd_string = ' '.join([self.escape(c) for c in cmd])
            sys.stderr.write(cmd_string + "\n")
        if universal_newlines is None:
            universal_newlines = self.universal_newlines

        # On Windows, if we make stdin a pipe when we plan to send
        # no input, and the test program exits before
        # Popen calls msvcrt.open_osfhandle, that call will fail.
        # So don't use a pipe for stdin if we don't need one.
        stdin = kw.get('stdin', None)
        if stdin is not None:
            stdin = PIPE

        combine = kw.get('combine', self.combine)
        if combine:
            stderr_value = STDOUT
        else:
            stderr_value = PIPE

        if timeout:
            self.start_timeout = timeout

        if sys.platform == 'win32':
            # Set this otherwist stdout/stderr pipes default to
            # windows default locale cp1252 which will throw exception
            # if using non-ascii characters.
            # For example test/Install/non-ascii-name.py
            os.environ['PYTHONIOENCODING'] = 'utf-8'

        # It seems that all pythons up to py3.6 still set text mode if you set encoding.
        # TODO: File enhancement request on python to propagate universal_newlines even
        # if encoding is set.hg c
        p = Popen(cmd,
                  stdin=stdin,
                  stdout=PIPE,
                  stderr=stderr_value,
                  env=os.environ,
                  universal_newlines=False)

        self.process = p
        return p

    @staticmethod
    def fix_binary_stream(stream):
        """Handle stream from popen when we specify not universal_newlines

        This will read from the pipes in binary mode, will not decode the
        output, and will not convert line endings to \n.
        We do this because in py3 (3.5) with universal_newlines=True, it will
        choose the default system locale to decode the output, and this breaks unicode
        output. Specifically test/option--tree.py which outputs a unicode char.

        py 3.6 allows us to pass an encoding param to popen thus not requiring the decode
        nor end of line handling, because we propagate universal_newlines as specified.

        TODO: Do we need to pass universal newlines into this function?
        """

        if not stream:
            return stream
        # It seems that py3.6 still sets text mode if you set encoding.
        stream = stream.decode('utf-8', errors='replace')
        return stream.replace('\r\n', '\n')

    def finish(self, popen=None, **kw):
        """ Finishes and waits for the process.

        Process being run under control of the specified popen argument
        is waited for, recording the exit status, output and error output.
        """
        if popen is None:
            popen = self.process
        if self.start_timeout:
            timeout = self.start_timeout
            # we're using a timeout from start, now reset it to default
            self.start_timeout = None
        else:
            timeout = self.timeout
        try:
            stdout, stderr = popen.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            popen.terminate()
            stdout, stderr = popen.communicate()

        # this is instead of using Popen as a context manager:
        if popen.stdout:
            popen.stdout.close()
        if popen.stderr:
            popen.stderr.close()
        try:
            if popen.stdin:
                popen.stdin.close()
        finally:
            popen.wait()

        stdout = self.fix_binary_stream(stdout)
        stderr = self.fix_binary_stream(stderr)

        self.status = popen.returncode
        self.process = None
        self._stdout.append(stdout or '')
        self._stderr.append(stderr or '')

    def run(self, program=None,
            interpreter=None,
            arguments=None,
            chdir=None,
            stdin=None,
            universal_newlines=None,
            timeout=None):
        """Runs a test of the program or script for the test environment.

        Output and error output are saved for future retrieval via
        the stdout() and stderr() methods.

        The specified program will have the original directory
        prepended unless it is enclosed in a [list].

        argument: If this is a dict() then will create arguments with KEY+VALUE for
                  each entry in the dict.
        """
        if self.external:
            if not program:
                program = self.program
            if not interpreter:
                interpreter = self.interpreter

        if universal_newlines is None:
            universal_newlines = self.universal_newlines

        if chdir:
            oldcwd = os.getcwd()
            if not os.path.isabs(chdir):
                chdir = os.path.join(self.workpath(chdir))
            if self.verbose:
                sys.stderr.write(f"chdir({chdir})\n")
            os.chdir(chdir)
        if not timeout:
            timeout = self.timeout
        p = self.start(program=program,
                       interpreter=interpreter,
                       arguments=arguments,
                       universal_newlines=universal_newlines,
                       timeout=timeout,
                       stdin=stdin)
        if is_List(stdin):
            stdin = ''.join(stdin)

        if stdin:
            stdin = to_bytes(stdin)

        # TODO(sgk):  figure out how to re-use the logic in the .finish()
        # method above.  Just calling it from here causes problems with
        # subclasses that redefine .finish().  We could abstract this
        # into Yet Another common method called both here and by .finish(),
        # but that seems ill-thought-out.
        try:
            stdout, stderr = p.communicate(input=stdin, timeout=timeout)
        except subprocess.TimeoutExpired:
            p.terminate()
            stdout, stderr = p.communicate()
        
        # this is instead of using Popen as a context manager:
        if p.stdout:
            p.stdout.close()
        if p.stderr:
            p.stderr.close()
        try:
            if p.stdin:
                p.stdin.close()
        finally:
            p.wait()
       
        self.status = p.returncode
        self.process = None

        stdout = self.fix_binary_stream(stdout)
        stderr = self.fix_binary_stream(stderr)

        self._stdout.append(stdout or '')
        self._stderr.append(stderr or '')

        if chdir:
            os.chdir(oldcwd)
        if self.verbose >= 2:
            write = sys.stdout.write
            write('============ STATUS: %d\n' % self.status)
            out = self.stdout()
            if out or self.verbose >= 3:
                write(f'============ BEGIN STDOUT (len={len(out)}):\n')
                write(out)
                write('============ END STDOUT\n')
            err = self.stderr()
            if err or self.verbose >= 3:
                write(f'============ BEGIN STDERR (len={len(err)})\n')
                write(err)
                write('============ END STDERR\n')

    def sleep(self, seconds=default_sleep_seconds):
        """Sleeps at least the specified number of seconds.

        If no number is specified, sleeps at least the minimum number of
        seconds necessary to advance file time stamps on the current
        system.  Sleeping more seconds is all right.
        """
        time.sleep(seconds)

    def stderr(self, run=None) -> Optional[str]:
        """Returns the stored standard error output from a given run.

        Args:
            run: run number to select.  If run number is omitted,
                return the standard error of the most recent run.
                If negative, use as a relative offset, e.g. -2
                means the run two prior to the most recent.

        Returns:
            selected sterr string or None if there are no stored runs.
        """
        if not run:
            run = len(self._stderr)
        elif run < 0:
            run = len(self._stderr) + run
        run -= 1
        try:
            return self._stderr[run]
        except IndexError:
            return None

    def stdout(self, run=None) -> Optional[str]:
        """Returns the stored standard output from a given run.

        Args:
            run: run number to select.  If run number is omitted,
                return the standard output of the most recent run.
                If negative, use as a relative offset, e.g. -2
                means the run two prior to the most recent.

        Returns:
            selected stdout string or None if there are no stored runs.
        """
        if not run:
            run = len(self._stdout)
        elif run < 0:
            run = len(self._stdout) + run
        run -= 1
        try:
            return self._stdout[run]
        except IndexError:
            return None

    def subdir(self, *subdirs):
        """Creates new subdirectories under the temporary working directory.

        Creates a subdir for each argument.  An argument may be a list,
        in which case the list elements are joined into a path.

        Returns the number of directories created, not including
        intermediate directories, for historical reasons.  A directory
        which already existed is counted as "created".
        """
        count = 0
        for sub in subdirs:
            if sub is None:
                continue
            if is_List(sub):
                sub = os.path.join(*sub)
            new = os.path.join(self.workdir, sub)
            try:
                # okay to exist, we just do this for counting
                os.makedirs(new, exist_ok=True)
                count = count + 1
            except OSError as e:
                pass

        return count


    def symlink(self, target, link):
        """Creates a symlink to the specified target.

        The link name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The link is
        assumed to be under the temporary working directory unless it
        is an absolute path name. The target is *not* assumed to be
        under the temporary working directory.
        """
        if sys.platform == 'win32':
            # Skip this on windows as we're not enabling it due to
            # it requiring user permissions which aren't always present
            # and we don't have a good way to detect those permissions yet.
            return
        link = self.canonicalize(link)
        try:
            os.symlink(target, link)
        except AttributeError:
            pass                # Windows has no symlink

    def tempdir(self, path=None):
        """Creates a temporary directory.

        A unique directory name is generated if no path name is specified.
        The directory is created, and will be removed when the TestCmd
        object is destroyed.
        """
        if path is None:
            try:
                path = tempfile.mkdtemp(prefix=testprefix)
            except TypeError:
                path = tempfile.mkdtemp()
        else:
            os.mkdir(path)

        # Symlinks in the path will report things
        # differently from os.getcwd(), so chdir there
        # and back to fetch the canonical path.
        cwd = os.getcwd()
        try:
            os.chdir(path)
            path = os.getcwd()
        finally:
            os.chdir(cwd)

        # Uppercase the drive letter since the case of drive
        # letters is pretty much random on win32:
        drive, rest = os.path.splitdrive(path)
        if drive:
            path = drive.upper() + rest

        #
        self._dirlist.append(path)

        global _Cleanup
        if self not in _Cleanup:
            _Cleanup.append(self)

        return path

    def touch(self, path, mtime=None):
        """Updates the modification time on the specified file or directory.

        The default is to update to the
        current time if no explicit modification time is specified.
        """
        path = self.canonicalize(path)
        atime = os.path.getatime(path)
        if mtime is None:
            mtime = time.time()
        os.utime(path, (atime, mtime))

    def unlink(self, file):
        """Unlinks the specified file name.

        The file name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The file is
        assumed to be under the temporary working directory unless it
        is an absolute path name.
        """
        file = self.canonicalize(file)
        os.unlink(file)

    def verbose_set(self, verbose):
        """Sets the verbose level."""
        self.verbose = verbose

    def where_is(self, file, path=None, pathext=None):
        """Finds an executable file."""
        if is_List(file):
            file = os.path.join(*file)
        if not os.path.isabs(file):
            file = where_is(file, path, pathext)
        return file

    def workdir_set(self, path):
        """Creates a temporary working directory with the specified path name.

        If the path is a null string (''), a unique directory name is created.
        """
        if path is not None:
            if path == '':
                path = None
            path = self.tempdir(path)
        self.workdir = path

    def workpath(self, *args):
        """Returns the absolute path name to a subdirectory or file within the current temporary working directory.

        Concatenates the temporary working directory name with the specified
        arguments using the os.path.join() method.
        """
        return os.path.join(self.workdir, *args)

    def readable(self, top, read=True):
        """Makes the specified directory tree readable or unreadable.

        Tree is made readable if `read` evaluates True (the default),
        else it is made not readable.

        This method has no effect on Windows systems, which use a
        completely different mechanism to control file readability.
        """

        if sys.platform == 'win32':
            return

        if read:
            def do_chmod(fname):
                try:
                    st = os.stat(fname)
                except OSError:
                    pass
                else:
                    os.chmod(fname, stat.S_IMODE(
                        st[stat.ST_MODE] | stat.S_IREAD))
        else:
            def do_chmod(fname):
                try:
                    st = os.stat(fname)
                except OSError:
                    pass
                else:
                    os.chmod(fname, stat.S_IMODE(
                        st[stat.ST_MODE] & ~stat.S_IREAD))

        if os.path.isfile(top):
            # If it's a file, that's easy, just chmod it.
            do_chmod(top)
        elif read:
            # It's a directory and we're trying to turn on read
            # permission, so it's also pretty easy, just chmod the
            # directory and then chmod every entry on our walk down the
            # tree.
            do_chmod(top)
            for dirpath, dirnames, filenames in os.walk(top):
                for name in dirnames + filenames:
                    do_chmod(os.path.join(dirpath, name))
        else:
            # It's a directory and we're trying to turn off read
            # permission, which means we have to chmod the directories
            # in the tree bottom-up, lest disabling read permission from
            # the top down get in the way of being able to get at lower
            # parts of the tree.
            for dirpath, dirnames, filenames in os.walk(top, topdown=0):
                for name in dirnames + filenames:
                    do_chmod(os.path.join(dirpath, name))
            do_chmod(top)

    def writable(self, top, write=True):
        """Make the specified directory tree writable or unwritable.

        Tree is made writable if `write` evaluates True (the default),
        else it is made not writable.
        """

        if sys.platform == 'win32':

            if write:
                def do_chmod(fname):
                    try:
                        os.chmod(fname, stat.S_IWRITE)
                    except OSError:
                        pass
            else:
                def do_chmod(fname):
                    try:
                        os.chmod(fname, stat.S_IREAD)
                    except OSError:
                        pass

        else:

            if write:
                def do_chmod(fname):
                    try:
                        st = os.stat(fname)
                    except OSError:
                        pass
                    else:
                        os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE] | 0o200))
            else:
                def do_chmod(fname):
                    try:
                        st = os.stat(fname)
                    except OSError:
                        pass
                    else:
                        os.chmod(fname, stat.S_IMODE(
                            st[stat.ST_MODE] & ~0o200))

        if os.path.isfile(top):
            do_chmod(top)
        else:
            do_chmod(top)
            for dirpath, dirnames, filenames in os.walk(top, topdown=0):
                for name in dirnames + filenames:
                    do_chmod(os.path.join(dirpath, name))

    def executable(self, top, execute=True):
        """Make the specified directory tree executable or not executable.

        Tree is made executable if `execute` evaluates True (the default),
        else it is made not executable.

        This method has no effect on Windows systems, which use a
        completely different mechanism to control file executability.
        """

        if sys.platform == 'win32':
            return

        if execute:
            def do_chmod(fname):
                try:
                    st = os.stat(fname)
                except OSError:
                    pass
                else:
                    os.chmod(fname, stat.S_IMODE(
                        st[stat.ST_MODE] | stat.S_IEXEC))
        else:
            def do_chmod(fname):
                try:
                    st = os.stat(fname)
                except OSError:
                    pass
                else:
                    os.chmod(fname, stat.S_IMODE(
                        st[stat.ST_MODE] & ~stat.S_IEXEC))

        if os.path.isfile(top):
            # If it's a file, that's easy, just chmod it.
            do_chmod(top)
        elif execute:
            # It's a directory and we're trying to turn on execute
            # permission, so it's also pretty easy, just chmod the
            # directory and then chmod every entry on our walk down the
            # tree.
            do_chmod(top)
            for dirpath, dirnames, filenames in os.walk(top):
                for name in dirnames + filenames:
                    do_chmod(os.path.join(dirpath, name))
        else:
            # It's a directory and we're trying to turn off execute
            # permission, which means we have to chmod the directories
            # in the tree bottom-up, lest disabling execute permission from
            # the top down get in the way of being able to get at lower
            # parts of the tree.
            for dirpath, dirnames, filenames in os.walk(top, topdown=0):
                for name in dirnames + filenames:
                    do_chmod(os.path.join(dirpath, name))
            do_chmod(top)

    def write(self, file, content, mode='wb'):
        """Writes data to file.

        The file is created under the temporary working directory.
        Any subdirectories in the path must already exist. The
        write is converted to the required type rather than failing
        if there is a str/bytes mistmatch.

        :param file: name of file to write to. If a list, treated
            as components of a path and concatenated into a path.
        :type file: str or list(str)
        :param content: data to write.
        :type  content: str or bytes
        :param mode: file mode, default is binary.
        :type mode: str
        """
        file = self.canonicalize(file)
        if mode[0] != 'w':
            raise ValueError("mode must begin with 'w'")
        with open(file, mode) as f:
            try:
                f.write(content)
            except TypeError as e:
                f.write(bytes(content, 'utf-8'))

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
