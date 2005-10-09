"""
TestCmd.py:  a testing framework for commands and scripts.

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

There are a bunch of keyword arguments that you can use at instantiation
time:

    test = TestCmd.TestCmd(description = 'string',
                           program = 'program_or_script_to_test',
                           interpreter = 'script_interpreter',
                           workdir = 'prefix',
                           subdir = 'subdir',
                           verbose = Boolean,
                           match = default_match_function,
                           combine = Boolean)

There are a bunch of methods that let you do a bunch of different
things.  Here is an overview of them:

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

    test.run(program = 'program_or_script_to_run',
             interpreter = 'script_interpreter',
             arguments = 'arguments to pass to program',
             chdir = 'directory_to_chdir_to',
             stdin = 'input to feed to the program\n')

    test.pass_test()
    test.pass_test(condition)
    test.pass_test(condition, function)

    test.fail_test()
    test.fail_test(condition)
    test.fail_test(condition, function)
    test.fail_test(condition, function, skip)

    test.no_result()
    test.no_result(condition)
    test.no_result(condition, function)
    test.no_result(condition, function, skip)

    test.stdout()
    test.stdout(run)

    test.stderr()
    test.stderr(run)

    test.symlink(target, link)

    test.match(actual, expected)

    test.match_exact("actual 1\nactual 2\n", "expected 1\nexpected 2\n")
    test.match_exact(["actual 1\n", "actual 2\n"],
                     ["expected 1\n", "expected 2\n"])

    test.match_re("actual 1\nactual 2\n", regex_string)
    test.match_re(["actual 1\n", "actual 2\n"], list_of_regexes)

    test.match_re_dotall("actual 1\nactual 2\n", regex_string)
    test.match_re_dotall(["actual 1\n", "actual 2\n"], list_of_regexes)

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

    TestCmd.no_result()
    TestCmd.no_result(condition)
    TestCmd.no_result(condition, function)
    TestCmd.no_result(condition, function, skip)

The TestCmd module also provides unbound functions that handle matching
in the same way as the match_*() methods described above.

    import TestCmd

    test = TestCmd.TestCmd(match = TestCmd.match_exact)

    test = TestCmd.TestCmd(match = TestCmd.match_re)

    test = TestCmd.TestCmd(match = TestCmd.match_re_dotall)

Lastly, the where_is() method also exists in an unbound function
version.

    import TestCmd

    TestCmd.where_is('foo')
    TestCmd.where_is('foo', 'PATH1:PATH2')
    TestCmd.where_is('foo', 'PATH1;PATH2', '.suffix3;.suffix4')
"""

# Copyright 2000, 2001, 2002, 2003, 2004 Steven Knight
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
__revision__ = "TestCmd.py 0.17.D001 2005/10/08 22:58:27 knight"
__version__ = "0.17"

import os
import os.path
import popen2
import re
import shutil
import stat
import string
import sys
import tempfile
import time
import traceback
import types
import UserList

__all__ = [ 'fail_test', 'no_result', 'pass_test',
            'match_exact', 'match_re', 'match_re_dotall',
            'python_executable', 'TestCmd' ]

def is_List(e):
    return type(e) is types.ListType \
        or isinstance(e, UserList.UserList)

try:
    from UserString import UserString
except ImportError:
    class UserString:
        pass

if hasattr(types, 'UnicodeType'):
    def is_String(e):
        return type(e) is types.StringType \
            or type(e) is types.UnicodeType \
            or isinstance(e, UserString)
else:
    def is_String(e):
        return type(e) is types.StringType or isinstance(e, UserString)

tempfile.template = 'testcmd.'

re_space = re.compile('\s')

if os.name == 'posix':

    def escape(arg):
        "escape shell special characters"
        slash = '\\'
        special = '"$'

        arg = string.replace(arg, slash, slash+slash)
        for c in special:
            arg = string.replace(arg, c, slash+c)

        if re_space.search(arg):
            arg = '"' + arg + '"'
        return arg

else:

    # Windows does not allow special characters in file names
    # anyway, so no need for an escape function, we will just quote
    # the arg.
    def escape(arg):
        if re_space.search(arg):
            arg = '"' + arg + '"'
        return arg

_Cleanup = []

def _clean():
    global _Cleanup
    cleanlist = filter(None, _Cleanup)
    del _Cleanup[:]
    cleanlist.reverse()
    for test in cleanlist:
        test.cleanup()

sys.exitfunc = _clean

class Collector:
    def __init__(self, top):
        self.entries = [top]
    def __call__(self, arg, dirname, names):
        pathjoin = lambda n, d=dirname: os.path.join(d, n)
        self.entries.extend(map(pathjoin, names))

def _caller(tblist, skip):
    string = ""
    arr = []
    for file, line, name, text in tblist:
        if file[-10:] == "TestCmd.py":
                break
        arr = [(file, line, name, text)] + arr
    atfrom = "at"
    for file, line, name, text in arr[skip:]:
        if name == "?":
            name = ""
        else:
            name = " (" + name + ")"
        string = string + ("%s line %d of %s%s\n" % (atfrom, line, file, name))
        atfrom = "\tfrom"
    return string

def fail_test(self = None, condition = 1, function = None, skip = 0):
    """Cause the test to fail.

    By default, the fail_test() method reports that the test FAILED
    and exits with a status of 1.  If a condition argument is supplied,
    the test fails only if the condition is true.
    """
    if not condition:
        return
    if not function is None:
        function()
    of = ""
    desc = ""
    sep = " "
    if not self is None:
        if self.program:
            of = " of " + self.program
            sep = "\n\t"
        if self.description:
            desc = " [" + self.description + "]"
            sep = "\n\t"

    at = _caller(traceback.extract_stack(), skip)
    sys.stderr.write("FAILED test" + of + desc + sep + at)

    sys.exit(1)

def no_result(self = None, condition = 1, function = None, skip = 0):
    """Causes a test to exit with no valid result.

    By default, the no_result() method reports NO RESULT for the test
    and exits with a status of 2.  If a condition argument is supplied,
    the test fails only if the condition is true.
    """
    if not condition:
        return
    if not function is None:
        function()
    of = ""
    desc = ""
    sep = " "
    if not self is None:
        if self.program:
            of = " of " + self.program
            sep = "\n\t"
        if self.description:
            desc = " [" + self.description + "]"
            sep = "\n\t"

    at = _caller(traceback.extract_stack(), skip)
    sys.stderr.write("NO RESULT for test" + of + desc + sep + at)

    sys.exit(2)

def pass_test(self = None, condition = 1, function = None):
    """Causes a test to pass.

    By default, the pass_test() method reports PASSED for the test
    and exits with a status of 0.  If a condition argument is supplied,
    the test passes only if the condition is true.
    """
    if not condition:
        return
    if not function is None:
        function()
    sys.stderr.write("PASSED\n")
    sys.exit(0)

def match_exact(lines = None, matches = None):
    """
    """
    if not is_List(lines):
        lines = string.split(lines, "\n")
    if not is_List(matches):
        matches = string.split(matches, "\n")
    if len(lines) != len(matches):
        return
    for i in range(len(lines)):
        if lines[i] != matches[i]:
            return
    return 1

def match_re(lines = None, res = None):
    """
    """
    if not is_List(lines):
        lines = string.split(lines, "\n")
    if not is_List(res):
        res = string.split(res, "\n")
    if len(lines) != len(res):
        return
    for i in range(len(lines)):
        if not re.compile("^" + res[i] + "$").search(lines[i]):
            return
    return 1

def match_re_dotall(lines = None, res = None):
    """
    """
    if not type(lines) is type(""):
        lines = string.join(lines, "\n")
    if not type(res) is type(""):
        res = string.join(res, "\n")
    if re.compile("^" + res + "$", re.DOTALL).match(lines):
        return 1

if os.name == 'java':

    python_executable = os.path.join(sys.prefix, 'jython')

else:

    python_executable = sys.executable

if sys.platform == 'win32':

    default_sleep_seconds = 2

    def where_is(file, path=None, pathext=None):
        if path is None:
            path = os.environ['PATH']
        if is_String(path):
            path = string.split(path, os.pathsep)
        if pathext is None:
            pathext = os.environ['PATHEXT']
        if is_String(pathext):
            pathext = string.split(pathext, os.pathsep)
        for ext in pathext:
            if string.lower(ext) == string.lower(file[-len(ext):]):
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
            path = string.split(path, os.pathsep)
        for dir in path:
            f = os.path.join(dir, file)
            if os.path.isfile(f):
                try:
                    st = os.stat(f)
                except OSError:
                    continue
                if stat.S_IMODE(st[stat.ST_MODE]) & 0111:
                    return f
        return None

    default_sleep_seconds = 1

class TestCmd:
    """Class TestCmd
    """

    def __init__(self, description = None,
                       program = None,
                       interpreter = None,
                       workdir = None,
                       subdir = None,
                       verbose = 0,
                       match = None,
                       combine = 0):
        self._cwd = os.getcwd()
        self.description_set(description)
        self.program_set(program)
        self.interpreter_set(interpreter)
        self.verbose_set(verbose)
        self.combine = combine
        if not match is None:
            self.match_func = match
        else:
            self.match_func = match_re
        self._dirlist = []
        self._preserve = {'pass_test': 0, 'fail_test': 0, 'no_result': 0}
        if os.environ.has_key('PRESERVE') and not os.environ['PRESERVE'] is '':
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

    def __del__(self):
        self.cleanup()

    def __repr__(self):
        return "%x" % id(self)

    def cleanup(self, condition = None):
        """Removes any temporary working directories for the specified
        TestCmd environment.  If the environment variable PRESERVE was
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
                print "Preserved directory", dir
        else:
            list = self._dirlist[:]
            list.reverse()
            for dir in list:
                self.writable(dir, 1)
                shutil.rmtree(dir, ignore_errors = 1)
            self._dirlist = []

        try:
            global _Cleanup
            _Cleanup.remove(self)
        except (AttributeError, ValueError):
            pass

    def description_set(self, description):
        """Set the description of the functionality being tested.
        """
        self.description = description

#    def diff(self):
#        """Diff two arrays.
#        """

    def fail_test(self, condition = 1, function = None, skip = 0):
        """Cause the test to fail.
        """
        if not condition:
            return
        self.condition = 'fail_test'
        fail_test(self = self,
                  condition = condition,
                  function = function,
                  skip = skip)

    def interpreter_set(self, interpreter):
        """Set the program to be used to interpret the program
        under test as a script.
        """
        self.interpreter = interpreter

    def match(self, lines, matches):
        """Compare actual and expected file contents.
        """
        return self.match_func(lines, matches)

    def match_exact(self, lines, matches):
        """Compare actual and expected file contents.
        """
        return match_exact(lines, matches)

    def match_re(self, lines, res):
        """Compare actual and expected file contents.
        """
        return match_re(lines, res)

    def match_re_dotall(self, lines, res):
        """Compare actual and expected file contents.
        """
        return match_re_dotall(lines, res)

    def no_result(self, condition = 1, function = None, skip = 0):
        """Report that the test could not be run.
        """
        if not condition:
            return
        self.condition = 'no_result'
        no_result(self = self,
                  condition = condition,
                  function = function,
                  skip = skip)

    def pass_test(self, condition = 1, function = None):
        """Cause the test to pass.
        """
        if not condition:
            return
        self.condition = 'pass_test'
        pass_test(self = self, condition = condition, function = function)

    def preserve(self, *conditions):
        """Arrange for the temporary working directories for the
        specified TestCmd environment to be preserved for one or more
        conditions.  If no conditions are specified, arranges for
        the temporary working directories to be preserved for all
        conditions.
        """
        if conditions is ():
            conditions = ('pass_test', 'fail_test', 'no_result')
        for cond in conditions:
            self._preserve[cond] = 1

    def program_set(self, program):
        """Set the executable program or script to be tested.
        """
        if program and not os.path.isabs(program):
            program = os.path.join(self._cwd, program)
        self.program = program

    def read(self, file, mode = 'rb'):
        """Reads and returns the contents of the specified file name.
        The file name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The file is
        assumed to be under the temporary working directory unless it
        is an absolute path name.  The I/O mode for the file may
        be specified; it must begin with an 'r'.  The default is
        'rb' (binary read).
        """
        if is_List(file):
            file = apply(os.path.join, tuple(file))
        if not os.path.isabs(file):
            file = os.path.join(self.workdir, file)
        if mode[0] != 'r':
            raise ValueError, "mode must begin with 'r'"
        return open(file, mode).read()

    def run(self, program = None,
                  interpreter = None,
                  arguments = None,
                  chdir = None,
                  stdin = None):
        """Runs a test of the program or script for the test
        environment.  Standard output and error output are saved for
        future retrieval via the stdout() and stderr() methods.

        The specified program will have the original directory
        prepending unless it is enclosed in a [list].
        """
        if chdir:
            oldcwd = os.getcwd()
            if not os.path.isabs(chdir):
                chdir = os.path.join(self.workpath(chdir))
            if self.verbose:
                sys.stderr.write("chdir(" + chdir + ")\n")
            os.chdir(chdir)
        if program:
            if type(program) == type('') and not os.path.isabs(program):
                program = os.path.join(self._cwd, program)
        else:
            program = self.program
            if not interpreter:
                interpreter = self.interpreter
        if not type(program) in [type([]), type(())]:
            program = [program]
        cmd = list(program)
        if interpreter:
            if not type(interpreter) in [type([]), type(())]:
                interpreter = [interpreter]
            cmd = list(interpreter) + cmd
        if arguments:
            if type(arguments) == type(''):
                arguments = string.split(arguments)
            cmd.extend(arguments)
        cmd_string = string.join(map(escape, cmd), ' ')
        if self.verbose:
            sys.stderr.write(cmd_string + "\n")
        try:
            p = popen2.Popen3(cmd, 1)
        except AttributeError:
            (tochild, fromchild, childerr) = os.popen3(' ' + cmd_string)
            if stdin:
                if is_List(stdin):
                    for line in stdin:
                        tochild.write(line)
                else:
                    tochild.write(stdin)
            tochild.close()
            out = fromchild.read()
            err = childerr.read()
            if self.combine:
                self._stdout.append(out + err)
            else:
                self._stdout.append(out)
                self._stderr.append(err)
            fromchild.close()
            self.status = childerr.close()
            if not self.status:
                self.status = 0
        except:
            raise
        else:
            if stdin:
                if is_List(stdin):
                    for line in stdin:
                        p.tochild.write(line)
                else:
                    p.tochild.write(stdin)
            p.tochild.close()
            out = p.fromchild.read()
            err = p.childerr.read()
            if self.combine:
                self._stdout.append(out + err)
            else:
                self._stdout.append(out)
                self._stderr.append(err)
            self.status = p.wait()
        if chdir:
            os.chdir(oldcwd)

    def sleep(self, seconds = default_sleep_seconds):
        """Sleeps at least the specified number of seconds.  If no
        number is specified, sleeps at least the minimum number of
        seconds necessary to advance file time stamps on the current
        system.  Sleeping more seconds is all right.
        """
        time.sleep(seconds)

    def stderr(self, run = None):
        """Returns the error output from the specified run number.
        If there is no specified run number, then returns the error
        output of the last run.  If the run number is less than zero,
        then returns the error output from that many runs back from the
        current run.
        """
        if not run:
            run = len(self._stderr)
        elif run < 0:
            run = len(self._stderr) + run
        run = run - 1
        return self._stderr[run]

    def stdout(self, run = None):
        """Returns the standard output from the specified run number.
        If there is no specified run number, then returns the standard
        output of the last run.  If the run number is less than zero,
        then returns the standard output from that many runs back from
        the current run.
        """
        if not run:
            run = len(self._stdout)
        elif run < 0:
            run = len(self._stdout) + run
        run = run - 1
        return self._stdout[run]

    def subdir(self, *subdirs):
        """Create new subdirectories under the temporary working
        directory, one for each argument.  An argument may be a list,
        in which case the list elements are concatenated using the
        os.path.join() method.  Subdirectories multiple levels deep
        must be created using a separate argument for each level:

                test.subdir('sub', ['sub', 'dir'], ['sub', 'dir', 'ectory'])

        Returns the number of subdirectories actually created.
        """
        count = 0
        for sub in subdirs:
            if sub is None:
                continue
            if is_List(sub):
                sub = apply(os.path.join, tuple(sub))
            new = os.path.join(self.workdir, sub)
            try:
                os.mkdir(new)
            except OSError:
                pass
            else:
                count = count + 1
        return count

    def symlink(self, target, link):
        """Creates a symlink to the specified target.
        The link name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The link is
        assumed to be under the temporary working directory unless it
        is an absolute path name. The target is *not* assumed to be
        under the temporary working directory.
        """
        if is_List(link):
            link = apply(os.path.join, tuple(link))
        if not os.path.isabs(link):
            link = os.path.join(self.workdir, link)
        os.symlink(target, link)

    def unlink(self, file):
        """Unlinks the specified file name.
        The file name may be a list, in which case the elements are
        concatenated with the os.path.join() method.  The file is
        assumed to be under the temporary working directory unless it
        is an absolute path name.
        """
        if is_List(file):
            file = apply(os.path.join, tuple(file))
        if not os.path.isabs(file):
            file = os.path.join(self.workdir, file)
        os.unlink(file)

    def verbose_set(self, verbose):
        """Set the verbose level.
        """
        self.verbose = verbose

    def where_is(self, file, path=None, pathext=None):
        """Find an executable file.
        """
        if is_List(file):
            file = apply(os.path.join, tuple(file))
        if not os.path.isabs(file):
            file = where_is(file, path, pathext)
        return file

    def workdir_set(self, path):
        """Creates a temporary working directory with the specified
        path name.  If the path is a null string (''), a unique
        directory name is created.
        """
        if (path != None):
            if path == '':
                path = tempfile.mktemp()
            if path != None:
                os.mkdir(path)
            # We'd like to set self.workdir like this:
            #     self.workdir = path
            # But symlinks in the path will report things
            # differently from os.getcwd(), so chdir there
            # and back to fetch the canonical path.
            cwd = os.getcwd()
            os.chdir(path)
            self.workdir = os.getcwd()
            os.chdir(cwd)
            # Uppercase the drive letter since the case of drive
            # letters is pretty much random on win32:
            drive,rest = os.path.splitdrive(self.workdir)
            if drive:
                self.workdir = string.upper(drive) + rest
            #
            self._dirlist.append(self.workdir)
            global _Cleanup
            try:
                _Cleanup.index(self)
            except ValueError:
                _Cleanup.append(self)
        else:
            self.workdir = None

    def workpath(self, *args):
        """Returns the absolute path name to a subdirectory or file
        within the current temporary working directory.  Concatenates
        the temporary working directory name with the specified
        arguments using the os.path.join() method.
        """
        return apply(os.path.join, (self.workdir,) + tuple(args))

    def readable(self, top, read=1):
        """Make the specified directory tree readable (read == 1)
        or not (read == None).
        """

        if read:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]|0400))
        else:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]&~0400))

        if os.path.isfile(top):
            # If it's a file, that's easy, just chmod it.
            do_chmod(top)
        elif read:
            # It's a directory and we're trying to turn on read
            # permission, so it's also pretty easy, just chmod the
            # directory and then chmod every entry on our walk down the
            # tree.  Because os.path.walk() is top-down, we'll enable
            # read permission on any directories that have it disabled
            # before os.path.walk() tries to list their contents.
            do_chmod(top)

            def chmod_entries(arg, dirname, names, do_chmod=do_chmod):
                pathnames = map(lambda n, d=dirname: os.path.join(d, n),
                                names)
                map(lambda p, do=do_chmod: do(p), pathnames)

            os.path.walk(top, chmod_entries, None)
        else:
            # It's a directory and we're trying to turn off read
            # permission, which means we have to chmod the directoreis
            # in the tree bottom-up, lest disabling read permission from
            # the top down get in the way of being able to get at lower
            # parts of the tree.  But os.path.walk() visits things top
            # down, so we just use an object to collect a list of all
            # of the entries in the tree, reverse the list, and then
            # chmod the reversed (bottom-up) list.
            col = Collector(top)
            os.path.walk(top, col, None)
            col.entries.reverse()
            map(lambda d, do=do_chmod: do(d), col.entries)

    def writable(self, top, write=1):
        """Make the specified directory tree writable (write == 1)
        or not (write == None).
        """

        if write:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]|0200))
        else:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]&~0200))

        if os.path.isfile(top):
            do_chmod(top)
        else:
            col = Collector(top)
            os.path.walk(top, col, None)
            map(lambda d, do=do_chmod: do(d), col.entries)

    def executable(self, top, execute=1):
        """Make the specified directory tree executable (execute == 1)
        or not (execute == None).
        """

        if execute:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]|0100))
        else:
            def do_chmod(fname):
                try: st = os.stat(fname)
                except OSError: pass
                else: os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]&~0100))

        if os.path.isfile(top):
            # If it's a file, that's easy, just chmod it.
            do_chmod(top)
        elif execute:
            # It's a directory and we're trying to turn on execute
            # permission, so it's also pretty easy, just chmod the
            # directory and then chmod every entry on our walk down the
            # tree.  Because os.path.walk() is top-down, we'll enable
            # execute permission on any directories that have it disabled
            # before os.path.walk() tries to list their contents.
            do_chmod(top)

            def chmod_entries(arg, dirname, names, do_chmod=do_chmod):
                pathnames = map(lambda n, d=dirname: os.path.join(d, n),
                                names)
                map(lambda p, do=do_chmod: do(p), pathnames)

            os.path.walk(top, chmod_entries, None)
        else:
            # It's a directory and we're trying to turn off execute
            # permission, which means we have to chmod the directories
            # in the tree bottom-up, lest disabling execute permission from
            # the top down get in the way of being able to get at lower
            # parts of the tree.  But os.path.walk() visits things top
            # down, so we just use an object to collect a list of all
            # of the entries in the tree, reverse the list, and then
            # chmod the reversed (bottom-up) list.
            col = Collector(top)
            os.path.walk(top, col, None)
            col.entries.reverse()
            map(lambda d, do=do_chmod: do(d), col.entries)

    def write(self, file, content, mode = 'wb'):
        """Writes the specified content text (second argument) to the
        specified file name (first argument).  The file name may be
        a list, in which case the elements are concatenated with the
        os.path.join() method.  The file is created under the temporary
        working directory.  Any subdirectories in the path must already
        exist.  The I/O mode for the file may be specified; it must
        begin with a 'w'.  The default is 'wb' (binary write).
        """
        if is_List(file):
            file = apply(os.path.join, tuple(file))
        if not os.path.isabs(file):
            file = os.path.join(self.workdir, file)
        if mode[0] != 'w':
            raise ValueError, "mode must begin with 'w'"
        open(file, mode).write(content)
