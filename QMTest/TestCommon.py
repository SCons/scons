"""
TestCommon.py:  a testing framework for commands and scripts
                with commonly useful error handling

The TestCommon module provides a simple, high-level interface for writing
tests of executable commands and scripts, especially commands and scripts
that interact with the file system.  All methods throw exceptions and
exit on failure, with useful error messages.  This makes a number of
explicit checks unnecessary, making the test scripts themselves simpler
to write and easier to read.

The TestCommon class is a subclass of the TestCmd class.  In essence,
TestCommon is a wrapper that handles common TestCmd error conditions in
useful ways.  You can use TestCommon directly, or subclass it for your
program and add additional (or override) methods to tailor it to your
program's specific needs.  Alternatively, the TestCommon class serves
as a useful example of how to define your own TestCmd subclass.

As a subclass of TestCmd, TestCommon provides access to all of the
variables and methods from the TestCmd module.  Consequently, you can
use any variable or method documented in the TestCmd module without
having to explicitly import TestCmd.

A TestCommon environment object is created via the usual invocation:

    import TestCommon
    test = TestCommon.TestCommon()

You can use all of the TestCmd keyword arguments when instantiating a
TestCommon object; see the TestCmd documentation for details.

Here is an overview of the methods and keyword arguments that are
provided by the TestCommon class:

    test.must_be_writable('file1', ['file2', ...])

    test.must_contain('file', 'required text\n')

    test.must_contain_lines(lines, output)

    test.must_exist('file1', ['file2', ...])

    test.must_match('file', "expected contents\n")

    test.must_not_be_writable('file1', ['file2', ...])

    test.must_not_contain_lines(lines, output)

    test.must_not_exist('file1', ['file2', ...])

    test.run(options = "options to be prepended to arguments",
             stdout = "expected standard output from the program",
             stderr = "expected error output from the program",
             status = expected_status,
             match = match_function)

The TestCommon module also provides the following variables

    TestCommon.python_executable
    TestCommon.exe_suffix
    TestCommon.obj_suffix
    TestCommon.shobj_suffix
    TestCommon.lib_prefix
    TestCommon.lib_suffix
    TestCommon.dll_prefix
    TestCommon.dll_suffix

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
__revision__ = "TestCommon.py 0.31.D001 2008/01/01 09:05:59 knight"
__version__ = "0.31"

import copy
import os
import os.path
import stat
import string
import sys
import types
import UserList

from TestCmd import *
from TestCmd import __all__

__all__.extend([ 'TestCommon',
                 'exe_suffix',
                 'obj_suffix',
                 'shobj_suffix',
                 'lib_prefix',
                 'lib_suffix',
                 'dll_prefix',
                 'dll_suffix',
               ])

# Variables that describe the prefixes and suffixes on this system.
if sys.platform == 'win32':
    exe_suffix   = '.exe'
    obj_suffix   = '.obj'
    shobj_suffix = '.obj'
    lib_prefix   = ''
    lib_suffix   = '.lib'
    dll_prefix   = ''
    dll_suffix   = '.dll'
elif sys.platform == 'cygwin':
    exe_suffix   = '.exe'
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = ''
    dll_suffix   = '.dll'
elif string.find(sys.platform, 'irix') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.o'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'
elif string.find(sys.platform, 'darwin') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.dylib'
else:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'

try:
    import difflib
except ImportError:
    pass
else:
    def simple_diff(a, b, fromfile='', tofile='',
                    fromfiledate='', tofiledate='', n=3, lineterm='\n'):
        """
        A function with the same calling signature as difflib.context_diff
        (diff -c) and difflib.unified_diff (diff -u) but which prints
        output like the simple, unadorned 'diff" command.
        """
        sm = difflib.SequenceMatcher(None, a, b)
        def comma(x1, x2):
            return x1+1 == x2 and str(x2) or '%s,%s' % (x1+1, x2)
        result = []
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == 'delete':
                result.append("%sd%d" % (comma(a1, a2), b1))
                result.extend(map(lambda l: '< ' + l, a[a1:a2]))
            elif op == 'insert':
                result.append("%da%s" % (a1, comma(b1, b2)))
                result.extend(map(lambda l: '> ' + l, b[b1:b2]))
            elif op == 'replace':
                result.append("%sc%s" % (comma(a1, a2), comma(b1, b2)))
                result.extend(map(lambda l: '< ' + l, a[a1:a2]))
                result.append('---')
                result.extend(map(lambda l: '> ' + l, b[b1:b2]))
        return result

def is_List(e):
    return type(e) is types.ListType \
        or isinstance(e, UserList.UserList)

def is_writable(f):
    mode = os.stat(f)[stat.ST_MODE]
    return mode & stat.S_IWUSR

def separate_files(flist):
    existing = []
    missing = []
    for f in flist:
        if os.path.exists(f):
            existing.append(f)
        else:
            missing.append(f)
    return existing, missing

if os.name == 'posix':
    def _failed(self, status = 0):
        if self.status is None or status is None:
            return None
        return _status(self) != status
    def _status(self):
        if os.WIFEXITED(self.status):
            return os.WEXITSTATUS(self.status)
        elif os.WIFSIGNALED(self.status):
            return os.WTERMSIG(self.status)
        else:
            return None
elif os.name == 'nt':
    def _failed(self, status = 0):
        return not (self.status is None or status is None) and \
               self.status != status
    def _status(self):
        return self.status

class TestCommon(TestCmd):

    # Additional methods from the Perl Test::Cmd::Common module
    # that we may wish to add in the future:
    #
    #  $test->subdir('subdir', ...);
    #
    #  $test->copy('src_file', 'dst_file');

    def __init__(self, **kw):
        """Initialize a new TestCommon instance.  This involves just
        calling the base class initialization, and then changing directory
        to the workdir.
        """
        apply(TestCmd.__init__, [self], kw)
        os.chdir(self.workdir)
        try:
            difflib
        except NameError:
            pass
        else:
            self.diff_function = simple_diff
            #self.diff_function = difflib.context_diff
            #self.diff_function = difflib.unified_diff

    banner_char = '='
    banner_width = 80

    def banner(self, s, width=None):
        if width is None:
            width = self.banner_width
        return s + self.banner_char * (width - len(s))

    try:
        difflib
    except NameError:
        def diff(self, a, b, name, *args, **kw):
            print self.banner('Expected %s' % name)
            print a
            print self.banner('Actual %s' % name)
            print b
    else:
        def diff(self, a, b, name, *args, **kw):
            print self.banner(name)
            args = (a.splitlines(), b.splitlines()) + args
            lines = apply(self.diff_function, args, kw)
            for l in lines:
                print l

    def must_be_writable(self, *files):
        """Ensures that the specified file(s) exist and are writable.
        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        not writable.
        """
        files = map(lambda x: is_List(x) and apply(os.path.join, x) or x, files)
        existing, missing = separate_files(files)
        unwritable = filter(lambda x, iw=is_writable: not iw(x), existing)
        if missing:
            print "Missing files: `%s'" % string.join(missing, "', `")
        if unwritable:
            print "Unwritable files: `%s'" % string.join(unwritable, "', `")
        self.fail_test(missing + unwritable)

    def must_contain(self, file, required, mode = 'rb'):
        """Ensures that the specified file contains the required text.
        """
        file_contents = self.read(file, mode)
        contains = (string.find(file_contents, required) != -1)
        if not contains:
            print "File `%s' does not contain required string." % file
            print self.banner('Required string ')
            print required
            print self.banner('%s contents ' % file)
            print file_contents
            self.fail_test(not contains)

    def must_contain_lines(self, lines, output, title=None):
        if title is None:
            title = 'output'

        missing = filter(lambda l, o=output: string.find(o, l) == -1, lines)

        if missing:
            print "Missing lines from %s:" % title
            print string.join(missing, '\n')
            print "%s ============================================================" % title
            print output
            self.fail_test()

    def must_exist(self, *files):
        """Ensures that the specified file(s) must exist.  An individual
        file be specified as a list of directory names, in which case the
        pathname will be constructed by concatenating them.  Exits FAILED
        if any of the files does not exist.
        """
        files = map(lambda x: is_List(x) and apply(os.path.join, x) or x, files)
        missing = filter(lambda x: not os.path.exists(x), files)
        if missing:
            print "Missing files: `%s'" % string.join(missing, "', `")
            self.fail_test(missing)

    def must_match(self, file, expect, mode = 'rb'):
        """Matches the contents of the specified file (first argument)
        against the expected contents (second argument).  The expected
        contents are a list of lines or a string which will be split
        on newlines.
        """
        file_contents = self.read(file, mode)
        try:
            self.fail_test(not self.match(file_contents, expect))
        except KeyboardInterrupt:
            raise
        except:
            print "Unexpected contents of `%s'" % file
            self.diff(expect, file_contents, 'contents ')
            raise

    def must_not_contain_lines(self, lines, output=None, title=None):
        if title is None:
            title = 'output'

        unexpected = filter(lambda l, o=output: string.find(o, l) != -1, lines)

        if unexpected:
            print "Unexpected lines in %s:" % title
            print string.join(unexpected, '\n')
            print "%s ============================================================" % title
            print output
            self.fail_test()

    def must_not_exist(self, *files):
        """Ensures that the specified file(s) must not exist.
        An individual file be specified as a list of directory names, in
        which case the pathname will be constructed by concatenating them.
        Exits FAILED if any of the files exists.
        """
        files = map(lambda x: is_List(x) and apply(os.path.join, x) or x, files)
        existing = filter(os.path.exists, files)
        if existing:
            print "Unexpected files exist: `%s'" % string.join(existing, "', `")
            self.fail_test(existing)


    def must_not_be_writable(self, *files):
        """Ensures that the specified file(s) exist and are not writable.
        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        writable.
        """
        files = map(lambda x: is_List(x) and apply(os.path.join, x) or x, files)
        existing, missing = separate_files(files)
        writable = filter(is_writable, existing)
        if missing:
            print "Missing files: `%s'" % string.join(missing, "', `")
        if writable:
            print "Writable files: `%s'" % string.join(writable, "', `")
        self.fail_test(missing + writable)

    def _complete(self, actual_stdout, expected_stdout,
                        actual_stderr, expected_stderr, status, match):
        """
        Post-processes running a subcommand, checking for failure
        status and displaying output appropriately.
        """
        if _failed(self, status):
            expect = ''
            if status != 0:
                expect = " (expected %s)" % str(status)
            print "%s returned %s%s" % (self.program, str(_status(self)), expect)
            print self.banner('STDOUT ')
            print actual_stdout
            print self.banner('STDERR ')
            print actual_stderr
            self.fail_test()
        if not expected_stdout is None and not match(actual_stdout, expected_stdout):
            self.diff(expected_stdout, actual_stdout, 'STDOUT ')
            if actual_stderr:
                print self.banner('STDERR ')
                print actual_stderr
            self.fail_test()
        if not expected_stderr is None and not match(actual_stderr, expected_stderr):
            print self.banner('STDOUT ')
            print actual_stdout
            self.diff(expected_stderr, actual_stderr, 'STDERR ')
            self.fail_test()

    def start(self, program = None,
                    interpreter = None,
                    arguments = None,
                    universal_newlines = None,
                    **kw):
        """
        Starts a program or script for the test environment.

        This handles the "options" keyword argument and exceptions.
        """
        try:
            options = kw['options']
            del kw['options']
        except KeyError:
            pass
        else:
            if options:
                if arguments is None:
                    arguments = options
                else:
                    arguments = options + " " + arguments
        try:
            return apply(TestCmd.start,
                         (self, program, interpreter, arguments, universal_newlines),
                         kw)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            print self.banner('STDOUT ')
            try:
                print self.stdout()
            except IndexError:
                pass
            print self.banner('STDERR ')
            try:
                print self.stderr()
            except IndexError:
                pass
            raise e

    def finish(self, popen, stdout = None, stderr = '', status = 0, **kw):
        """
        Finishes and waits for the process being run under control of
        the specified popen argument.  Additional arguments are similar
        to those of the run() method:

                stdout  The expected standard output from
                        the command.  A value of None means
                        don't test standard output.

                stderr  The expected error output from
                        the command.  A value of None means
                        don't test error output.

                status  The expected exit status from the
                        command.  A value of None means don't
                        test exit status.
        """
        apply(TestCmd.finish, (self, popen,), kw)
        match = kw.get('match', self.match)
        self._complete(self.stdout(), stdout,
                       self.stderr(), stderr, status, match)

    def run(self, options = None, arguments = None,
                  stdout = None, stderr = '', status = 0, **kw):
        """Runs the program under test, checking that the test succeeded.

        The arguments are the same as the base TestCmd.run() method,
        with the addition of:

                options Extra options that get appended to the beginning
                        of the arguments.

                stdout  The expected standard output from
                        the command.  A value of None means
                        don't test standard output.

                stderr  The expected error output from
                        the command.  A value of None means
                        don't test error output.

                status  The expected exit status from the
                        command.  A value of None means don't
                        test exit status.

        By default, this expects a successful exit (status = 0), does
        not test standard output (stdout = None), and expects that error
        output is empty (stderr = "").
        """
        if options:
            if arguments is None:
                arguments = options
            else:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
        try:
            match = kw['match']
            del kw['match']
        except KeyError:
            match = self.match
        apply(TestCmd.run, [self], kw)
        self._complete(self.stdout(), stdout,
                       self.stderr(), stderr, status, match)

    def skip_test(self, message="Skipping test.\n"):
        """Skips a test.

        Proper test-skipping behavior is dependent on the external
        TESTCOMMON_PASS_SKIPS environment variable.  If set, we treat
        the skip as a PASS (exit 0), and otherwise treat it as NO RESULT.
        In either case, we print the specified message as an indication
        that the substance of the test was skipped.

        (This was originally added to support development under Aegis.
        Technically, skipping a test is a NO RESULT, but Aegis would
        treat that as a test failure and prevent the change from going to
        the next step.  Since we ddn't want to force anyone using Aegis
        to have to install absolutely every tool used by the tests, we
        would actually report to Aegis that a skipped test has PASSED
        so that the workflow isn't held up.)
        """
        if message:
            sys.stdout.write(message)
            sys.stdout.flush()
        pass_skips = os.environ.get('TESTCOMMON_PASS_SKIPS')
        if pass_skips in [None, 0, '0']:
            # skip=1 means skip this function when showing where this
            # result came from.  They only care about the line where the
            # script called test.skip_test(), not the line number where
            # we call test.no_result().
            self.no_result(skip=1)
        else:
            # We're under the development directory for this change,
            # so this is an Aegis invocation; pass the test (exit 0).
            self.pass_test()
