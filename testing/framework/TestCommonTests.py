#!/usr/bin/env python
"""
Unit tests for the TestCommon.py module.
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

import os
import re
import signal
import sys
import unittest
from textwrap import dedent

# Strip the current directory so we get the right TestCommon.py module.
sys.path = sys.path[1:]

import TestCmd
import TestCommon

# this used to be a custom function, now use the stdlib equivalent
def lstrip(s):
    return dedent(s)

expected_newline = '\\n'


def assert_display(expect, result, error=None):
    try:
        expect = expect.pattern
    except AttributeError:
        pass
    display = [
        '\n',
        f"{'EXPECTED: ':*<80}\n",
        expect,
        f"{'GOT: ':*<80}\n",
        result,
        '' if error is None else error,
        f"{'':*<80}\n",
    ]
    return ''.join(display)


class TestCommonTestCase(unittest.TestCase):
    """Base class for TestCommon test cases, fixture and utility methods."""
    create_run_env = True

    def setUp(self):
        self.orig_cwd = os.getcwd()
        if self.create_run_env:
            self.run_env = TestCmd.TestCmd(workdir = '')

    def tearDown(self):
        os.chdir(self.orig_cwd)

    def set_up_execution_scripts(self):
        run_env = self.run_env

        run_env.subdir('sub dir')

        self.python = sys.executable

        self.pass_script = run_env.workpath('sub dir', 'pass')
        self.fail_script = run_env.workpath('sub dir', 'fail')
        self.stdout_script = run_env.workpath('sub dir', 'stdout')
        self.stderr_script = run_env.workpath('sub dir', 'stderr')
        self.signal_script = run_env.workpath('sub dir', 'signal')
        self.stdin_script = run_env.workpath('sub dir', 'stdin')

        preamble = "import sys"
        stdout = "; sys.stdout.write(r'%s:  STDOUT:  ' + repr(sys.argv[1:]) + '\\n')"
        stderr = "; sys.stderr.write(r'%s:  STDERR:  ' + repr(sys.argv[1:]) + '\\n')"
        exit0 = "; sys.exit(0)"
        exit1 = "; sys.exit(1)"
        if sys.platform == 'win32':
            wrapper = '@python -c "%s" %%1 %%2 %%3 %%4 %%5 %%6 %%7 %%8 %%9\n'
        else:
            wrapper = '#! /usr/bin/env python\n%s\n'
        wrapper = '#! /usr/bin/env python\n%s\n'

        pass_body = preamble + stdout % self.pass_script + exit0
        fail_body = preamble + stdout % self.fail_script + exit1
        stderr_body = preamble + stderr % self.stderr_script + exit0

        run_env.write(self.pass_script, wrapper % pass_body)
        run_env.write(self.fail_script, wrapper % fail_body)
        run_env.write(self.stderr_script, wrapper % stderr_body)

        signal_body = lstrip("""\
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
        """)

        run_env.write(self.signal_script, wrapper % signal_body)

        stdin_body = lstrip("""\
        import sys
        input = sys.stdin.read()[:-1]
        sys.stdout.write(r'%s:  STDOUT:  ' + repr(input) + '\\n')
        sys.stderr.write(r'%s:  STDERR:  ' + repr(input) + '\\n')
        """ % (self.stdin_script, self.stdin_script))

        run_env.write(self.stdin_script, wrapper % stdin_body)

    def run_execution_test(self, script, expect_stdout, expect_stderr):
        self.set_up_execution_scripts()

        run_env = self.run_env

        os.chdir(run_env.workpath('sub dir'))

        # Everything before this prepared our "source directory."
        # Now do the real test.
        script = script % self.__dict__
        run_env.run(program=sys.executable, stdin=script)

        stdout = run_env.stdout()
        stderr = run_env.stderr()

        expect_stdout = expect_stdout % self.__dict__
        assert stdout == expect_stdout, assert_display(expect_stdout,
                                                       stdout,
                                                       stderr)

        try:
            match = expect_stderr.match
        except AttributeError:
            expect_stderr = expect_stderr % self.__dict__
            assert stderr == expect_stderr, assert_display(expect_stderr,
                                                           stderr)
        else:
            assert expect_stderr.match(stderr), assert_display(expect_stderr,
                                                               stderr)


class __init__TestCase(TestCommonTestCase):
    def test___init__(self):
        """Test initialization"""
        run_env = self.run_env

        os.chdir(run_env.workdir)
        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        import os
        print(os.getcwd())
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()[:-1]
        assert stdout != run_env.workdir, stdout
        stderr = run_env.stderr()
        assert stderr == "", stderr


class banner_TestCase(TestCommonTestCase):
    create_run_env = False
    def test_banner(self):
        """Test banner()"""
        tc = TestCommon.TestCommon(workdir='')

        b = tc.banner('xyzzy ')
        assert b == "xyzzy ==========================================================================", b

        tc.banner_width = 10

        b = tc.banner('xyzzy ')
        assert b == "xyzzy ====", b

        b = tc.banner('xyzzy ', 20)
        assert b == "xyzzy ==============", b

        tc.banner_char = '-'

        b = tc.banner('xyzzy ')
        assert b == "xyzzy ----", b

class must_be_writable_TestCase(TestCommonTestCase):
    def test_file_does_not_exists(self):
        """Test must_be_writable():  file does not exist"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Missing files: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_writable_file_exists(self):
        """Test must_be_writable():  writable file exists"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        f1 = tc.workpath('file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode | stat.S_IWUSR)
        tc.must_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_non_writable_file_exists(self):
        """Test must_be_writable():  non-writable file exists"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        f1 = tc.workpath('file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode & ~stat.S_IWUSR)
        tc.must_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Unwritable files: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_file_specified_as_list(self):
        """Test must_be_writable():  file specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        f1 = tc.workpath('sub', 'file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode | stat.S_IWUSR)
        tc.must_be_writable(['sub', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr


class must_contain_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_contain():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 contents\\n")
        tc.must_contain('file1', "1 c")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_success_index_0(self):
        """Test must_contain():  success at index 0"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 contents\\n")
        tc.must_contain('file1', "file1 c")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_missing(self):
        """Test must_contain():  file missing"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_contain('file1', "1 c\\n")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr.find("No such file or directory:") != -1, stderr

    def test_failure(self):
        """Test must_contain():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 does not match\\n")
        tc.must_contain('file1', "1 c")
        tc.run()
        """)
        expect = lstrip("""\
        File `file1' does not contain required string.
        Required string ================================================================
        b'1 c'
        file1 contents =================================================================
        b'file1 does not match\\n'
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == expect, f"got:\n{stdout}\nexpected:\n{expect}"
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_mode(self):
        """Test must_contain():  mode"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 contents\\n", mode='w')
        tc.must_contain('file1', "1 c", mode='r')
        tc.write('file2', "file2 contents\\n", mode='wb')
        tc.must_contain('file2', "2 c", mode='rb')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr



class must_contain_all_lines_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_contain_all_lines():  success"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_contain_all_lines(output, lines)

        test.must_contain_all_lines(output, ['www\\n'])

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_contain_all_lines():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_all_lines(output, lines)

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing expected lines from output:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        output =========================================================================
        www
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr

    def test_find(self):
        """Test must_contain_all_lines():  find"""
        run_env = self.run_env

        script = lstrip("""
        import re
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'x.*',
            '.*y',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        def re_search(output, line):
            return re.compile(line, re.S).search(output)
        test.must_contain_all_lines(output, lines, find=re_search)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_title(self):
        """Test must_contain_all_lines():  title"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_all_lines(output, lines, title='STDERR')

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing expected lines from STDERR:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        STDERR =========================================================================
        www
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr



class must_contain_any_line_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_contain_any_line():  success"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'aaa\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_contain_any_line(output, lines)

        test.must_contain_any_line(output, ['www\\n'])

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_contain_any_line():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_any_line(output, lines)

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing any expected line from output:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        output =========================================================================
        www
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr

    def test_find(self):
        """Test must_contain_any_line():  find"""
        run_env = self.run_env

        script = lstrip("""
        import re
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'aaa',
            '.*y',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        def re_search(output, line):
            return re.compile(line, re.S).search(output)
        test.must_contain_any_line(output, lines, find=re_search)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_title(self):
        """Test must_contain_any_line():  title"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_any_line(output, lines, title='STDOUT')

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing any expected line from STDOUT:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        STDOUT =========================================================================
        www
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr



class must_contain_exactly_lines_TestCase(TestCommonTestCase):
    def test_success_list(self):
        """Test must_contain_exactly_lines():  success (input list)"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'yyy\\n',
            'xxx\\n',
            'zzz',
            'www\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_contain_exactly_lines(output, lines)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_success_string(self):
        """Test must_contain_exactly_lines():  success (input string)"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = '''\\
        yyy
        xxx
        zzz
        www
        '''

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_contain_exactly_lines(output, lines)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_contain_exactly_lines():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_exactly_lines(output, lines)

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing expected lines from output:
            'xxx'
            'yyy'
        Missing output =================================================================
        Extra unexpected lines from output:
            'www'
            'zzz'
        Extra output ===================================================================
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr

    def test_find(self):
        """Test must_contain_exactly_lines():  find"""
        run_env = self.run_env

        script = lstrip("""
        import re
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'zzz',
            '.*y',
            'xxx',
            'www',
        ]

        output = '''\\\
        www
        xxx
        yyy
        zzz
        '''

        def re_search(output, line):
            pattern = re.compile(line, re.S)
            index = 0
            for o in output:
                if pattern.search(o):
                    return index
                index +=1
            return None
        test.must_contain_exactly_lines(output, lines, find=re_search)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_title(self):
        """Test must_contain_exactly_lines():  title"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_exactly_lines(output, lines, title='STDOUT')

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing expected lines from STDOUT:
            'xxx'
            'yyy'
        Missing STDOUT =================================================================
        Extra unexpected lines from STDOUT:
            'www'
            'zzz'
        Extra STDOUT ===================================================================
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr



class must_contain_lines_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_contain_lines():  success"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_contain_lines(lines, output)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_contain_lines():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_contain_lines(lines, output)

        test.pass_test()
        """)

        expect = lstrip("""\
        Missing expected lines from output:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        output =========================================================================
        www
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr



class must_exist_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_exist():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_exist('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_exist():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_exist('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Missing files: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_file_specified_as_list(self):
        """Test must_exist():  file specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        tc.must_exist(['sub', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    @unittest.skipIf(sys.platform == 'win32', "Skip symlink test on win32")
    def test_broken_link(self) :
        """Test must_exist():  exists but it is a broken link"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.symlink('badtarget', "brokenlink")
        tc.must_exist('brokenlink')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

class must_exist_one_of_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_exist_one_of():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_exist_one_of(['file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_exist_one_of():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_exist_one_of(['file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Missing one of: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_files_specified_as_list(self):
        """Test must_exist_one_of():  files specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_exist_one_of(['file2', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_files_specified_with_wildcards(self):
        """Test must_exist_one_of():  files specified with wildcards"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file7', "file7\\n")
        tc.must_exist_one_of(['file?'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_given_as_list(self):
        """Test must_exist_one_of():  file given as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        tc.must_exist_one_of(['file2',
                              ['sub', 'file1']])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_given_as_sequence(self):
        """Test must_exist_one_of():  file given as sequence"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        tc.must_exist_one_of(['file2',
                              ('sub', 'file1')])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

class must_match_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_match():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_match('file1', "file1\\n")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_does_not_exists(self):
        """Test must_match():  file does not exist"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_match('file1', "file1\\n")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr.find("No such file or directory:") != -1, stderr

    def test_failure(self):
        """Test must_match():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 does not match\\n")
        tc.must_match('file1', "file1\\n")
        tc.run()
        """)

        expect = lstrip("""\
        match_re: mismatch at line 0:
          search re='^file1$'
          line='file1 does not match'
        Unexpected contents of `file1'
        contents =======================================================================
        1c1
        < file1
        ---
        > file1 does not match
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == expect, stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_mode(self):
        """Test must_match():  mode"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n", mode='w')
        tc.must_match('file1', "file1\\n", mode='r')
        tc.write('file2', "file2\\n", mode='wb')
        tc.must_match('file2', "file2\\n", mode='rb')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr



class must_not_be_writable_TestCase(TestCommonTestCase):
    def test_file_does_not_exists(self):
        """Test must_not_be_writable():  file does not exist"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Missing files: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_writable_file_exists(self):
        """Test must_not_be_writable():  writable file exists"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        f1 = tc.workpath('file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode | stat.S_IWUSR)
        tc.must_not_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Writable files: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_non_writable_file_exists(self):
        """Test must_not_be_writable():  non-writable file exists"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        f1 = tc.workpath('file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode & ~stat.S_IWUSR)
        tc.must_not_be_writable('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_specified_as_list(self):
        """Test must_not_be_writable():  file specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        import os
        import stat
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        f1 = tc.workpath('sub', 'file1')
        mode = os.stat(f1)[stat.ST_MODE]
        os.chmod(f1, mode & ~stat.S_IWUSR)
        tc.must_not_be_writable(['sub', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr



class must_not_contain_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_not_contain():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 contents\\n")
        tc.must_not_contain('file1', b"1 does not contain c")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_does_not_exist(self):
        """Test must_not_contain():  file does not exist"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_contain('file1', "1 c\\n")
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr.find("No such file or directory:") != -1, stderr

    def test_failure(self):
        """Test must_not_contain():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 does contain contents\\n")
        tc.must_not_contain('file1', b"1 does contain c")
        tc.run()
        """)
        expect = lstrip("""\
        File `file1' contains banned string.
        Banned string ==================================================================
        b'1 does contain c'
        file1 contents =================================================================
        b'file1 does contain contents\\n'
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == expect, f"\ngot:\n{stdout}\nexpected:\n{expect}"

        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_failure_index_0(self):
        """Test must_not_contain():  failure at index 0"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 does contain contents\\n")
        tc.must_not_contain('file1', b"file1 does")
        tc.run()
        """)
        expect = lstrip("""\
        File `file1' contains banned string.
        Banned string ==================================================================
        b'file1 does'
        file1 contents =================================================================
        b'file1 does contain contents\\n'
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == expect, f"\ngot:\n{stdout}\nexpected:\n{expect}"

        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_mode(self):
        """Test must_not_contain():  mode"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1 contents\\n", mode='w')
        tc.must_not_contain('file1', "1 does not contain c", mode='r')
        tc.write('file2', "file2 contents\\n", mode='wb')
        tc.must_not_contain('file2', b"2 does not contain c", mode='rb')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr



class must_not_contain_any_line_TestCase(TestCommonTestCase):
    def test_failure(self):
        """Test must_not_contain_any_line():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
            'www\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_not_contain_any_line(output, lines)

        test.pass_test()
        """)

        expect = lstrip("""\
        Unexpected lines in output:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
            'www%(expected_newline)s'
        output =========================================================================
        www
        xxx
        yyy
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr

    def test_find(self):
        """Test must_not_contain_any_line():  find"""
        run_env = self.run_env

        script = lstrip("""
        import re
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'x.*'
            '.*y'
        ]

        output = '''\\
        www
        zzz
        '''

        def re_search(output, line):
            return re.compile(line, re.S).search(output)
        test.must_not_contain_any_line(output, lines, find=re_search)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_success(self):
        """Test must_not_contain_any_line():  success"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n'
            'yyy\\n'
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_not_contain_any_line(output, lines)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_title(self):
        """Test must_not_contain_any_line():  title"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_not_contain_any_line(output, lines, title='XYZZY')

        test.pass_test()
        """)

        expect = lstrip("""\
        Unexpected lines in XYZZY:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        XYZZY ==========================================================================
        www
        xxx
        yyy
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr



class must_not_contain_lines_TestCase(TestCommonTestCase):
    def test_failure(self):
        """Test must_not_contain_lines():  failure"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n',
            'yyy\\n',
        ]

        output = '''\\
        www
        xxx
        yyy
        zzz
        '''

        test.must_not_contain_lines(lines, output)

        test.pass_test()
        """)

        expect = lstrip("""\
        Unexpected lines in output:
            'xxx%(expected_newline)s'
            'yyy%(expected_newline)s'
        output =========================================================================
        www
        xxx
        yyy
        zzz
        """ % globals())

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        stderr = run_env.stderr()
        assert stdout == expect, assert_display(expect, stdout, stderr)
        assert stderr.find("FAILED") != -1, stderr

    def test_success(self):
        """Test must_not_contain_lines():  success"""
        run_env = self.run_env

        script = lstrip("""
        import TestCommon
        test = TestCommon.TestCommon(workdir='')

        lines = [
            'xxx\\n'
            'yyy\\n'
        ]

        output = '''\\
        www
        zzz
        '''

        test.must_not_contain_lines(lines, output)

        test.pass_test()
        """)

        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr



class must_not_exist_TestCase(TestCommonTestCase):
    def test_failure(self):
        """Test must_not_exist():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_not_exist('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Unexpected files exist: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_success(self):
        """Test must_not_exist():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_exist('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_specified_as_list(self):
        """Test must_not_exist():  file specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.must_not_exist(['sub', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    @unittest.skipIf(sys.platform == 'win32', "Skip symlink test on win32")
    def test_existing_broken_link(self):
        """Test must_not_exist():  exists but it is a broken link"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.symlink('badtarget', 'brokenlink')
        tc.must_not_exist('brokenlink')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Unexpected files exist: `brokenlink'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

class must_not_exist_any_of_TestCase(TestCommonTestCase):
    def test_success(self):
        """Test must_not_exist_any_of():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_exist_any_of(['file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_failure(self):
        """Test must_not_exist_any_of():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_not_exist_any_of(['file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Unexpected files exist: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_files_specified_as_list(self):
        """Test must_not_exist_any_of():  files specified as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_exist_any_of(['file2', 'file1'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_files_specified_with_wildcards(self):
        """Test must_not_exist_any_of():  files specified with wildcards"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file7', "file7\\n")
        tc.must_not_exist_any_of(['files?'])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_given_as_list(self):
        """Test must_not_exist_any_of():  file given as list"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        tc.must_not_exist_any_of(['file2',
                              ['sub', 'files*']])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_given_as_sequence(self):
        """Test must_not_exist_any_of():  file given as sequence"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.subdir('sub')
        tc.write(['sub', 'file1'], "sub/file1\\n")
        tc.must_not_exist_any_of(['file2',
                              ('sub', 'files?')])
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

class must_not_be_empty_TestCase(TestCommonTestCase):
    def test_failure(self):
        """Test must_not_be_empty():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "")
        tc.must_not_be_empty('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "File is empty: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

    def test_success(self):
        """Test must_not_be_empty():  success"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.write('file1', "file1\\n")
        tc.must_not_be_empty('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "", stdout
        stderr = run_env.stderr()
        assert stderr == "PASSED\n", stderr

    def test_file_doesnt_exist(self):
        """Test must_not_be_empty():  failure"""
        run_env = self.run_env

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(workdir='')
        tc.must_not_be_empty('file1')
        tc.pass_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "File doesn't exist: `file1'\n", stdout
        stderr = run_env.stderr()
        assert stderr.find("FAILED") != -1, stderr

class run_TestCase(TestCommonTestCase):
    def test_argument_handling(self):
        """Test run():  argument handling"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        tc.run(arguments = "arg1 arg2 arg3",
               stdout = r"%(pass_script)s:  STDOUT:  ['arg1', 'arg2', 'arg3']" + "\\n")
        """)

        self.run_execution_test(script, "", "")

    def test_default_pass(self):
        """Test run():  default arguments, script passes"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run()
        """)

        self.run_execution_test(script, "", "")

    def test_default_fail(self):
        """Test run():  default arguments, script fails"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(fail_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run()
        """)

        expect_stdout = lstrip("""\
        %(fail_script)s returned 1
        STDOUT =========================================================================
        %(fail_script)s:  STDOUT:  []

        STDERR =========================================================================

        """)

        expect_stderr = lstrip("""\
        FAILED test of .*fail
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>( \\(<module>\\))?
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_default_stderr(self):
        """Test run():  default arguments, error output"""
        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(stderr_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run()
        """)

        expect_stdout = lstrip("""\
        match_re: expected 1 lines, found 2
        STDOUT =========================================================================

        STDERR =========================================================================
        0a1
        > %(stderr_script)s:  STDERR:  []
        """)

        expect_stderr = lstrip("""\
        FAILED test of .*stderr
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_exception_handling(self):
        """Test run():  exception handling"""
        script = lstrip("""\
        import TestCmd
        from TestCommon import TestCommon
        def raise_exception(*args, **kw):
            raise TypeError("forced TypeError")
        TestCmd.TestCmd.start = raise_exception
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run()
        """)

        expect_stdout = lstrip("""\
        STDOUT =========================================================================
        None
        STDERR =========================================================================
        None
        """)

        expect_stderr = lstrip(
            fr"""Exception trying to execute: \[{re.escape(repr(sys.executable))}, '[^']*pass'\]
Traceback \(most recent call last\):
  File "<stdin>", line \d+, in (\?|<module>)
  File "[^"]+TestCommon.py", line \d+, in run
    super\(\).run\(\*\*kw\)
  File "[^"]+TestCmd.py", line \d+, in run
    p = self.start\(program=program,
(?:\s*\^*\s)?  File \"[^\"]+TestCommon.py\", line \d+, in start
    raise e
  File "[^"]+TestCommon.py", line \d+, in start
    return super\(\).start\(program, interpreter, arguments,
(?:\s*\^*\s)?  File \"<stdin>\", line \d+, in raise_exception
TypeError: forced TypeError
""")
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_ignore_stderr(self):
        """Test run():  ignore stderr"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(stderr_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(stderr = None)
        """)

        self.run_execution_test(script, "", "")

    def test_match_function_stdout(self):
        """Test run():  explicit match function, stdout"""

        script = lstrip("""\
        def my_match_exact(actual, expect): return actual == expect
        from TestCommon import TestCommon, match_re_dotall
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_re_dotall)
        tc.run(arguments = "arg1 arg2 arg3",
               stdout = r"%(pass_script)s:  STDOUT:  ['arg1', 'arg2', 'arg3']" + "\\n",
               match = my_match_exact)
        """)

        self.run_execution_test(script, "", "")

    def test_match_function_stderr(self):
        """Test run():  explicit match function, stderr"""

        script = lstrip("""\
        def my_match_exact(actual, expect): return actual == expect
        from TestCommon import TestCommon, match_re_dotall
        tc = TestCommon(program=r'%(stderr_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_re_dotall)
        tc.run(arguments = "arg1 arg2 arg3",
               stderr = r"%(stderr_script)s:  STDERR:  ['arg1', 'arg2', 'arg3']" + "\\n",
               match = my_match_exact)
        """)

        self.run_execution_test(script, "", "")

    def test_matched_status_fails(self):
        """Test run():  matched status, script fails"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(fail_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(status = 1)
        """)

        self.run_execution_test(script, "", "")

    def test_matched_stdout(self):
        """Test run():  matched stdout"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        tc.run(stdout = r"%(pass_script)s:  STDOUT:  []" + "\\n")
        """)

        self.run_execution_test(script, "", "")

    def test_matched_stderr(self):
        """Test run():  matched stderr"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(stderr_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        tc.run(stderr = r"%(stderr_script)s:  STDERR:  []" + "\\n")
        """)

        self.run_execution_test(script, "", "")

    def test_mismatched_status_pass(self):
        """Test run():  mismatched status, script passes"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(status = 1)
        """)

        expect_stdout = lstrip("""\
        %(pass_script)s returned 0 (expected 1)
        STDOUT =========================================================================
        %(pass_script)s:  STDOUT:  []

        STDERR =========================================================================

        """)

        expect_stderr = lstrip("""\
        FAILED test of .*pass
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>( \\(<module>\\))?
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_mismatched_status_fail(self):
        """Test run():  mismatched status, script fails"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(fail_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(status = 2)
        """)

        expect_stdout = lstrip("""\
        %(fail_script)s returned 1 (expected 2)
        STDOUT =========================================================================
        %(fail_script)s:  STDOUT:  []

        STDERR =========================================================================

        """)

        expect_stderr = lstrip("""\
        FAILED test of .*fail
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>( \\(<module>\\))?
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_mismatched_stdout(self):
        """Test run():  mismatched stdout"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(stdout = "Not found\\n")
        """)

        expect_stdout = lstrip("""\
        match_re: mismatch at line 0:
          search re='^Not found$'
          line='%(pass_script)s:  STDOUT:  []'
        STDOUT =========================================================================
        1c1
        < Not found
        ---
        > %(pass_script)s:  STDOUT:  []
        """)

        expect_stderr = lstrip("""\
        FAILED test of .*pass
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>( \\(<module>\\))?
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_mismatched_stderr(self):
        """Test run():  mismatched stderr"""

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(stderr_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run(stderr = "Not found\\n")
        """)

        expect_stdout = lstrip("""\
        match_re: mismatch at line 0:
          search re='^Not found$'
          line='%(stderr_script)s:  STDERR:  []'
        STDOUT =========================================================================

        STDERR =========================================================================
        1c1
        < Not found
        ---
        > %(stderr_script)s:  STDERR:  []
        """)

        expect_stderr = lstrip("""\
        FAILED test of .*stderr
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>( \\(<module>\\))?
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_option_handling(self):
        """Test run():  option handling"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        tc.run(options = "opt1 opt2 opt3",
               stdout = r"%(pass_script)s:  STDOUT:  ['opt1', 'opt2', 'opt3']" + "\\n")
        """)

        self.run_execution_test(script, "", "")

    def test_options_plus_arguments(self):
        """Test run():  option handling with arguments"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        tc.run(options = "opt1 opt2 opt3",
               arguments = "arg1 arg2 arg3",
               stdout = r"%(pass_script)s:  STDOUT:  ['opt1', 'opt2', 'opt3', 'arg1', 'arg2', 'arg3']" + "\\n")
        """)

        self.run_execution_test(script, "", "")

    def test_signal_handling(self):
        """Test run():  signal handling"""

        try:
            os.kill
        except AttributeError:
            sys.stderr.write('can not test, no os.kill ... ')
            return

        script = lstrip("""\
        from TestCommon import TestCommon
        tc = TestCommon(program=r'%(signal_script)s',
                        interpreter=r'%(python)s',
                        workdir='')
        tc.run()
        """)

        self.SIGTERM = f"{'' if sys.platform == 'win32' else '-'}{signal.SIGTERM}"

        # Script returns the signal value as a negative number.
        expect_stdout = lstrip("""\
        %(signal_script)s returned %(SIGTERM)s
        STDOUT =========================================================================

        STDERR =========================================================================

        """)

        expect_stderr = lstrip("""\
        FAILED test of .*signal
        \\tat line \\d+ of .*TestCommon\\.py \\(_complete\\)
        \\tfrom line \\d+ of .*TestCommon\\.py \\(run\\)
        \\tfrom line \\d+ of <stdin>
        """)
        expect_stderr = re.compile(expect_stderr, re.M)

        self.run_execution_test(script, expect_stdout, expect_stderr)

    def test_stdin(self):
        """Test run():  stdin handling"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(stdin_script)s',
                        interpreter=r'%(python)s',
                        workdir='',
                        match=match_exact)
        expect_stdout = r"%(stdin_script)s:  STDOUT:  'input'" + "\\n"
        expect_stderr = r"%(stdin_script)s:  STDERR:  'input'" + "\\n"
        tc.run(stdin="input\\n", stdout = expect_stdout, stderr = expect_stderr)
        """)

        expect_stdout = lstrip("""\
        %(pass_script)s returned 0 (expected 1)
        STDOUT =========================================================================
        %(pass_script)s:  STDOUT:  []

        STDERR =========================================================================

        """)

        self.run_execution_test(script, "", "")



class start_TestCase(TestCommonTestCase):
    def test_option_handling(self):
        """Test start():  option handling"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        p = tc.start(options = "opt1 opt2 opt3")
        expect = r"%(pass_script)s:  STDOUT:  ['opt1', 'opt2', 'opt3']" + "\\n"
        tc.finish(p, stdout = expect)
        """)

        self.run_execution_test(script, "", "")

    def test_options_plus_arguments(self):
        """Test start():  option handling with arguments"""

        script = lstrip("""\
        from TestCommon import TestCommon, match_exact
        tc = TestCommon(program=r'%(pass_script)s',
                        interpreter=r'%(python)s',
                        workdir="",
                        match=match_exact)
        p = tc.start(options = "opt1 opt2 opt3",
                     arguments = "arg1 arg2 arg3")
        expect = r"%(pass_script)s:  STDOUT:  ['opt1', 'opt2', 'opt3', 'arg1', 'arg2', 'arg3']" + "\\n"
        tc.finish(p, stdout = expect)
        """)

        self.run_execution_test(script, "", "")



class skip_test_TestCase(TestCommonTestCase):
    def test_skip_test(self):
        """Test skip_test()"""
        run_env = self.run_env

        script = lstrip("""\
        import TestCommon
        test = TestCommon.TestCommon(workdir='')
        test.skip_test()
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "Skipping test.\n", stdout
        stderr = run_env.stderr()
        expect = [
            "NO RESULT for test at line 3 of <stdin>\n",
            "NO RESULT for test at line 3 of <stdin> (<module>)\n",
        ]
        assert stderr in expect, repr(stderr)

        script = lstrip("""\
        import TestCommon
        test = TestCommon.TestCommon(workdir='')
        test.skip_test("skipping test because I said so\\n")
        """)
        run_env.run(program=sys.executable, stdin=script)
        stdout = run_env.stdout()
        assert stdout == "skipping test because I said so\n", stdout
        stderr = run_env.stderr()
        expect = [
            "NO RESULT for test at line 3 of <stdin>\n",
            "NO RESULT for test at line 3 of <stdin> (<module>)\n",
        ]
        assert stderr in expect, repr(stderr)

        import os
        os.environ['TESTCOMMON_PASS_SKIPS'] = '1'

        try:
            script = lstrip("""\
            import TestCommon
            test = TestCommon.TestCommon(workdir='')
            test.skip_test()
            """)
            run_env.run(program=sys.executable, stdin=script)
            stdout = run_env.stdout()
            assert stdout == "Skipping test.\n", stdout
            stderr = run_env.stderr()
            assert stderr == "PASSED\n", stderr

        finally:
            del os.environ['TESTCOMMON_PASS_SKIPS']



class variables_TestCase(TestCommonTestCase):
    def test_variables(self):
        """Test global variables"""
        run_env = self.run_env

        variables = [
            'fail_test',
            'no_result',
            'pass_test',
            'match_exact',
            'match_re',
            'match_re_dotall',
            'python',
            '_python_',
            'TestCmd',

            'TestCommon',
            'exe_suffix',
            'obj_suffix',
            'shobj_prefix',
            'shobj_suffix',
            'lib_prefix',
            'lib_suffix',
            'dll_prefix',
            'dll_suffix',
        ]

        script = "import TestCommon\n" + \
                 '\n'.join([f"print(TestCommon.{v})\n" for v in variables])
        run_env.run(program=sys.executable, stdin=script)
        stderr = run_env.stderr()
        assert stderr == "", stderr

        script = "from TestCommon import *\n" + \
                 '\n'.join([f"print({v})" for v in variables])
        run_env.run(program=sys.executable, stdin=script)
        stderr = run_env.stderr()
        assert stderr == "", stderr



if __name__ == "__main__":
    unittest.main()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
