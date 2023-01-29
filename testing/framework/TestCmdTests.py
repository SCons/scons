#!/usr/bin/env python
"""
Unit tests for the TestCmd.py module.
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
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from io import StringIO
from contextlib import closing
from collections import UserList
from subprocess import PIPE

from SCons.Util import to_bytes, to_str


# Strip the current directory so we get the right TestCmd.py module.
sys.path = sys.path[1:]

import TestCmd
from TestCmd import _python_

def _is_readable(path):
    # XXX this doesn't take into account UID, it assumes it's our file
    return os.stat(path)[stat.ST_MODE] & stat.S_IREAD

def _is_writable(path):
    # XXX this doesn't take into account UID, it assumes it's our file
    return os.stat(path)[stat.ST_MODE] & stat.S_IWRITE

def _is_executable(path):
    # XXX this doesn't take into account UID, it assumes it's our file
    return os.stat(path)[stat.ST_MODE] & stat.S_IEXEC

def _clear_dict(dict, *keys):
    for key in keys:
        try:
            del dict[key]
        except KeyError:
            pass


class ExitError(Exception):
    pass

class TestCmdTestCase(unittest.TestCase):
    """Base class for TestCmd test cases, with fixture and utility methods."""

    def setUp(self):
        self.orig_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.orig_cwd)

    def setup_run_scripts(self):
        class T:
            pass

        t = T()

        t.script = 'script'
        t.scriptx = 'scriptx.bat'
        t.script1 = 'script_1.txt'
        t.scriptout = 'scriptout'
        t.scripterr = 'scripterr'
        fmt = "import os, sys; cwd = os.getcwd(); " + \
              "sys.stdout.write('%s:  STDOUT:  %%s:  %%s\\n' %% (cwd, sys.argv[1:])); " + \
              "sys.stderr.write('%s:  STDERR:  %%s:  %%s\\n' %% (cwd, sys.argv[1:]))"
        fmtout = "import os, sys; cwd = os.getcwd(); " + \
                 "sys.stdout.write('%s:  STDOUT:  %%s:  %%s\\n' %% (cwd, sys.argv[1:]))"
        fmterr = "import os, sys; cwd = os.getcwd(); " + \
                 "sys.stderr.write('%s:  STDERR:  %%s:  %%s\\n' %% (cwd, sys.argv[1:]))"
        text = fmt % (t.script, t.script)
        textx = fmt % (t.scriptx, t.scriptx)
        if sys.platform == 'win32':
            textx = textx.replace('%', '%%')
            textx = f"@{_python_} -c \"{textx}\" %1 %2 %3 %4 %5 %6 %7 %8 %9\n"
        else:
            textx = f"#!{_python_}\n{textx}\n"
        text1 = f"A first line to be ignored!\n{fmt % (t.script1, t.script1)}"
        textout = fmtout % t.scriptout
        texterr = fmterr % t.scripterr

        run_env = TestCmd.TestCmd(workdir = '')
        run_env.subdir('sub dir')
        t.run_env = run_env

        t.sub_dir = run_env.workpath('sub dir')
        t.script_path = run_env.workpath('sub dir', t.script)
        t.scriptx_path = run_env.workpath('sub dir', t.scriptx)
        t.script1_path = run_env.workpath('sub dir', t.script1)
        t.scriptout_path = run_env.workpath('sub dir', t.scriptout)
        t.scripterr_path = run_env.workpath('sub dir', t.scripterr)

        run_env.write(t.script_path, text)
        run_env.write(t.scriptx_path, textx)
        run_env.write(t.script1_path, text1)
        run_env.write(t.scriptout_path, textout)
        run_env.write(t.scripterr_path, texterr)

        os.chmod(t.script_path, 0o644)  # XXX UNIX-specific
        os.chmod(t.scriptx_path, 0o755)  # XXX UNIX-specific
        os.chmod(t.script1_path, 0o644)  # XXX UNIX-specific
        os.chmod(t.scriptout_path, 0o644)  # XXX UNIX-specific
        os.chmod(t.scripterr_path, 0o644)  # XXX UNIX-specific

        t.orig_cwd = os.getcwd()

        t.workdir = run_env.workpath('sub dir')
        os.chdir(t.workdir)

        return t

    def translate_newlines(self, data):
        data = data.replace("\r\n", "\n")
        return data

    def call_python(self, indata, python=None):
        if python is None:
            python = sys.executable
        cp = subprocess.run(python, input=to_bytes(indata), stderr=PIPE, stdout=PIPE)
        stdout = self.translate_newlines(to_str(cp.stdout))
        stderr = self.translate_newlines(to_str(cp.stderr))
        return stdout, stderr, cp.returncode

    def popen_python(self, indata, status=0, stdout="", stderr="", python=None):
        if python is None:
            python = sys.executable
        _stdout, _stderr, _status = self.call_python(indata, python)
        assert _status == status, (
            f"status = {_status}, expected {status}\n"
            f"STDOUT ===================\n{_stdout}"
            f"STDERR ===================\n{_stderr}"
        )
        assert _stdout == stdout, (
            f"Expected STDOUT ==========\n{stdout}"
            f"Actual STDOUT ============\n{_stdout}"
            f"STDERR ===================\n{_stderr}"
        )
        assert _stderr == stderr, (
            f"Expected STDERR ==========\n{stderr}"
            f"Actual STDERR ============\n{_stderr}"
        )

    def run_match(self, content, *args):
        expect = "%s:  %s:  %s:  %s\n" % args
        content = self.translate_newlines(to_str(content))
        assert content == expect, (
            f"Expected {args[1] + expect} ==========\n"
            f"Actual {args[1] + content} ============\n"
        )



class __init__TestCase(TestCmdTestCase):
    def test_init(self):
        """Test init()"""
        test = TestCmd.TestCmd()
        test = TestCmd.TestCmd(description = 'test')
        test = TestCmd.TestCmd(description = 'test', program = 'foo')
        test = TestCmd.TestCmd(description = 'test',
                               program = 'foo',
                               universal_newlines=None)



class basename_TestCase(TestCmdTestCase):
    def test_basename(self):
        """Test basename() [XXX TO BE WRITTEN]"""
        assert 1 == 1



class cleanup_TestCase(TestCmdTestCase):
    def test_cleanup(self):
        """Test cleanup()"""
        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        test.write('file1', "Test file #1\n")
        test.cleanup()
        assert not os.path.exists(wdir)

    def test_writable(self):
        """Test cleanup() when the directory isn't writable"""
        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        test.write('file2', "Test file #2\n")
        os.chmod(test.workpath('file2'), 0o400)
        os.chmod(wdir, 0o500)
        test.cleanup()
        assert not os.path.exists(wdir)

    def test_shutil(self):
        """Test cleanup() when used with shutil"""
        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        os.chdir(wdir)

        import shutil
        save_rmtree = shutil.rmtree
        def my_rmtree(dir, ignore_errors=0, wdir=wdir, _rmtree=save_rmtree):
            assert os.getcwd() != wdir
            return _rmtree(dir, ignore_errors=ignore_errors)
        try:
            shutil.rmtree = my_rmtree
            test.cleanup()
        finally:
            shutil.rmtree = save_rmtree

    def test_atexit(self):
        """Test cleanup when atexit is used"""
        self.popen_python(f"""\
import atexit
import sys
import TestCmd

sys.path = [r'{self.orig_cwd}'] + sys.path

@atexit.register
def cleanup():
    print("cleanup()")

result = TestCmd.TestCmd(workdir='')
sys.exit(0)
""", stdout='cleanup()\n')


class chmod_TestCase(TestCmdTestCase):
    def test_chmod(self):
        """Test chmod()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'sub')

        wdir_file1 = os.path.join(test.workdir, 'file1')
        wdir_sub_file2 = os.path.join(test.workdir, 'sub', 'file2')

        with open(wdir_file1, 'w') as f:
            f.write("")
        with open(wdir_sub_file2, 'w') as f:
            f.write("")

        if sys.platform == 'win32':

            test.chmod(wdir_file1, stat.S_IREAD)
            test.chmod(['sub', 'file2'], stat.S_IWRITE)

            file1_mode = stat.S_IMODE(os.stat(wdir_file1)[stat.ST_MODE])
            assert file1_mode == 0o444, f'0{file1_mode:o}'
            file2_mode = stat.S_IMODE(os.stat(wdir_sub_file2)[stat.ST_MODE])
            assert file2_mode == 0o666, f'0{file2_mode:o}'

            test.chmod('file1', stat.S_IWRITE)
            test.chmod(wdir_sub_file2, stat.S_IREAD)

            file1_mode = stat.S_IMODE(os.stat(wdir_file1)[stat.ST_MODE])
            assert file1_mode == 0o666, f'0{file1_mode:o}'
            file2_mode = stat.S_IMODE(os.stat(wdir_sub_file2)[stat.ST_MODE])
            assert file2_mode == 0o444, f'0{file2_mode:o}'

        else:

            test.chmod(wdir_file1, 0o700)
            test.chmod(['sub', 'file2'], 0o760)

            file1_mode = stat.S_IMODE(os.stat(wdir_file1)[stat.ST_MODE])
            assert file1_mode == 0o700, f'0{file1_mode:o}'
            file2_mode = stat.S_IMODE(os.stat(wdir_sub_file2)[stat.ST_MODE])
            assert file2_mode == 0o760, f'0{file2_mode:o}'

            test.chmod('file1', 0o765)
            test.chmod(wdir_sub_file2, 0o567)

            file1_mode = stat.S_IMODE(os.stat(wdir_file1)[stat.ST_MODE])
            assert file1_mode == 0o765, f'0{file1_mode:o}'
            file2_mode = stat.S_IMODE(os.stat(wdir_sub_file2)[stat.ST_MODE])
            assert file2_mode == 0o567, f'0{file2_mode:o}'



class combine_TestCase(TestCmdTestCase):
    def test_combine(self):
        """Test combining stdout and stderr"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run1', """import sys
sys.stdout.write("run1 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run1 STDOUT second line\\n")
sys.stderr.write("run1 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run1 STDERR second line\\n")
sys.stdout.write("run1 STDOUT third line\\n")
sys.stderr.write("run1 STDERR third line\\n")
""")
        run_env.write('run2', """import sys
sys.stdout.write("run2 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run2 STDOUT second line\\n")
sys.stderr.write("run2 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run2 STDERR second line\\n")
sys.stdout.write("run2 STDOUT third line\\n")
sys.stderr.write("run2 STDERR third line\\n")
""")
        cwd = os.getcwd()
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            test = TestCmd.TestCmd(interpreter = 'python',
                                   workdir = '',
                                   combine = 1)
            output = test.stdout()
            if output is not None:
                raise IndexError(f"got unexpected output:\n\t`{output}'\n")

            # The underlying system subprocess implementations can combine
            # stdout and stderr in different orders, so we accomodate both.

            test.program_set('run1')
            test.run(arguments = 'foo bar')
            stdout_lines = """\
run1 STDOUT ['foo', 'bar']
run1 STDOUT second line
run1 STDOUT third line
"""
            stderr_lines = """\
run1 STDERR ['foo', 'bar']
run1 STDERR second line
run1 STDERR third line
"""
            foo_bar_expect = (stdout_lines + stderr_lines,
                              stderr_lines + stdout_lines)

            test.program_set('run2')
            test.run(arguments = 'snafu')
            stdout_lines = """\
run2 STDOUT ['snafu']
run2 STDOUT second line
run2 STDOUT third line
"""
            stderr_lines = """\
run2 STDERR ['snafu']
run2 STDERR second line
run2 STDERR third line
"""
            snafu_expect = (stdout_lines + stderr_lines,
                            stderr_lines + stdout_lines)

            # XXX SHOULD TEST ABSOLUTE NUMBER AS WELL
            output = test.stdout()
            output = self.translate_newlines(output)
            assert output in snafu_expect, output
            error = test.stderr()
            assert error == '', error

            output = test.stdout(run = -1)
            output = self.translate_newlines(output)
            assert output in foo_bar_expect, output
            error = test.stderr(-1)
            assert error == '', error
        finally:
            os.chdir(cwd)



class description_TestCase(TestCmdTestCase):
    def test_description(self):
        """Test description()"""
        test = TestCmd.TestCmd()
        assert test.description is None, 'initialized description?'
        test = TestCmd.TestCmd(description = 'test')
        assert test.description == 'test', 'uninitialized description'
        test.description_set('foo')
        assert test.description == 'foo', 'did not set description'



class diff_TestCase(TestCmdTestCase):
    def test_diff_re(self):
        """Test diff_re()"""
        result = TestCmd.diff_re(["abcde"], ["abcde"])
        result = list(result)
        assert result == [], result
        result = TestCmd.diff_re(["a.*e"], ["abcde"])
        result = list(result)
        assert result == [], result
        result = TestCmd.diff_re(["a.*e"], ["xxx"])
        result = list(result)
        assert result == ['1c1', "< 'a.*e'", '---', "> 'xxx'"], result

    def test_diff_custom_function(self):
        """Test diff() using a custom function"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def my_diff(a, b):
    return [
        '*****',
        a,
        '*****',
        b,
        '*****',
    ]
test = TestCmd.TestCmd(diff = my_diff)
test.diff("a\\nb1\\nc\\n", "a\\nb2\\nc\\n", "STDOUT")
sys.exit(0)
""",
                          stdout = """\
STDOUT==========================================================================
*****
['a', 'b1', 'c']
*****
['a', 'b2', 'c']
*****
""")

    def test_diff_string(self):
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff = 'diff_re')
test.diff("a\\nb1\\nc\\n", "a\\nb2\\nc\\n", 'STDOUT')
sys.exit(0)
""",
                          stdout = """\
STDOUT==========================================================================
2c2
< 'b1'
---
> 'b2'
""")

    def test_error(self):
        """Test handling a compilation error in TestCmd.diff_re()"""
        script_input = f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
assert TestCmd.diff_re([r"a.*(e"], ["abcde"])
sys.exit(0)
"""
        stdout, stderr, status = self.call_python(script_input)
        assert status == 1, status
        expect1 = "Regular expression error in '^a.*(e$': missing )"
        expect2 = "Regular expression error in '^a.*(e$': unbalanced parenthesis"
        assert (stderr.find(expect1) != -1 or
                stderr.find(expect2) != -1), repr(stderr)

    def test_simple_diff_static_method(self):
        """Test calling the TestCmd.TestCmd.simple_diff() static method"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
result = TestCmd.TestCmd.simple_diff(['a', 'b', 'c', 'e', 'f1'],
                                     ['a', 'c', 'd', 'e', 'f2'])
result = list(result)
expect = ['2d1', '< b', '3a3', '> d', '5c5', '< f1', '---', '> f2']
assert result == expect, result
sys.exit(0)
""")

    def test_context_diff_static_method(self):
        """Test calling the TestCmd.TestCmd.context_diff() static method"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
result = TestCmd.TestCmd.context_diff(['a\\n', 'b\\n', 'c\\n', 'e\\n', 'f1\\n'],
                                      ['a\\n', 'c\\n', 'd\\n', 'e\\n', 'f2\\n'])
result = list(result)
expect = [
    '*** \\n',
    '--- \\n',
    '***************\\n',
    '*** 1,5 ****\\n',
    '  a\\n',
    '- b\\n',
    '  c\\n',
    '  e\\n',
    '! f1\\n',
    '--- 1,5 ----\\n',
    '  a\\n',
    '  c\\n',
    '+ d\\n',
    '  e\\n',
    '! f2\\n',
]
assert result == expect, result
sys.exit(0)
""")

    def test_unified_diff_static_method(self):
        """Test calling the TestCmd.TestCmd.unified_diff() static method"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
result = TestCmd.TestCmd.unified_diff(['a\\n', 'b\\n', 'c\\n', 'e\\n', 'f1\\n'],
                                      ['a\\n', 'c\\n', 'd\\n', 'e\\n', 'f2\\n'])
result = list(result)
expect = [
    '--- \\n',
    '+++ \\n',
    '@@ -1,5 +1,5 @@\\n',
    ' a\\n',
    '-b\\n',
    ' c\\n',
    '+d\\n',
    ' e\\n',
    '-f1\\n',
    '+f2\\n'
]
assert result == expect, result
sys.exit(0)
""")

    def test_diff_re_static_method(self):
        """Test calling the TestCmd.TestCmd.diff_re() static method"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
result = TestCmd.TestCmd.diff_re(['a', 'b', 'c', '.', 'f1'],
                                 ['a', 'c', 'd', 'e', 'f2'])
result = list(result)
expect = [
    '2c2',
    "< 'b'",
    '---',
    "> 'c'",
    '3c3',
    "< 'c'",
    '---',
    "> 'd'",
    '5c5',
    "< 'f1'",
    '---',
    "> 'f2'"
]
assert result == expect, result
sys.exit(0)
""")



class diff_stderr_TestCase(TestCmdTestCase):
    def test_diff_stderr_default(self):
        """Test diff_stderr() default behavior"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd()
test.diff_stderr('a\nb1\nc\n', 'a\nb2\nc\n')
sys.exit(0)
""",
                          stdout="""\
2c2
< b1
---
> b2
""")

    def test_diff_stderr_not_affecting_diff_stdout(self):
        """Test diff_stderr() not affecting diff_stdout() behavior"""
        self.popen_python(fr"""
import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stderr='diff_re')
print("diff_stderr:")
test.diff_stderr('a\nb.\nc\n', 'a\nbb\nc\n')
print("diff_stdout:")
test.diff_stdout('a\nb.\nc\n', 'a\nbb\nc\n')
sys.exit(0)
""",
                          stdout="""\
diff_stderr:
diff_stdout:
2c2
< b.
---
> bb
""")

    def test_diff_stderr_custom_function(self):
        """Test diff_stderr() using a custom function"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def my_diff(a, b):
    return ["a:"] + a + ["b:"] + b
test = TestCmd.TestCmd(diff_stderr=my_diff)
test.diff_stderr('abc', 'def')
sys.exit(0)
""",
                          stdout="""\
a:
abc
b:
def
""")

    def test_diff_stderr_TestCmd_function(self):
        """Test diff_stderr() using a TestCmd function"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stderr = TestCmd.diff_re)
test.diff_stderr('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")

    def test_diff_stderr_static_method(self):
        """Test diff_stderr() using a static method"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stderr=TestCmd.TestCmd.diff_re)
test.diff_stderr('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")

    def test_diff_stderr_string(self):
        """Test diff_stderr() using a string to fetch the diff method"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stderr='diff_re')
test.diff_stderr('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")



class diff_stdout_TestCase(TestCmdTestCase):
    def test_diff_stdout_default(self):
        """Test diff_stdout() default behavior"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd()
test.diff_stdout('a\nb1\nc\n', 'a\nb2\nc\n')
sys.exit(0)
""",
                          stdout="""\
2c2
< b1
---
> b2
""")

    def test_diff_stdout_not_affecting_diff_stderr(self):
        """Test diff_stdout() not affecting diff_stderr() behavior"""
        self.popen_python(fr"""
import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stdout='diff_re')
print("diff_stdout:")
test.diff_stdout('a\nb.\nc\n', 'a\nbb\nc\n')
print("diff_stderr:")
test.diff_stderr('a\nb.\nc\n', 'a\nbb\nc\n')
sys.exit(0)
""",
                          stdout="""\
diff_stdout:
diff_stderr:
2c2
< b.
---
> bb
""")

    def test_diff_stdout_custom_function(self):
        """Test diff_stdout() using a custom function"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def my_diff(a, b):
    return ["a:"] + a + ["b:"] + b
test = TestCmd.TestCmd(diff_stdout=my_diff)
test.diff_stdout('abc', 'def')
sys.exit(0)
""",
                          stdout="""\
a:
abc
b:
def
""")

    def test_diff_stdout_TestCmd_function(self):
        """Test diff_stdout() using a TestCmd function"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stdout = TestCmd.diff_re)
test.diff_stdout('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")

    def test_diff_stdout_static_method(self):
        """Test diff_stdout() using a static method"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stdout=TestCmd.TestCmd.diff_re)
test.diff_stdout('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")

    def test_diff_stdout_string(self):
        """Test diff_stdout() using a string to fetch the diff method"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(diff_stdout='diff_re')
test.diff_stdout('a\n.\n', 'b\nc\n')
sys.exit(0)
""",
                          stdout="""\
1c1
< 'a'
---
> 'b'
""")



class exit_TestCase(TestCmdTestCase):
    def test_exit(self):
        """Test exit()"""
        def _test_it(cwd, tempdir, condition, preserved):
            close_true = {'pass_test': 1, 'fail_test': 0, 'no_result': 0}
            exit_status = {'pass_test': 0, 'fail_test': 1, 'no_result': 2}
            result_string = {'pass_test': "PASSED\n",
                             'fail_test': "FAILED test at line 5 of <stdin>\n",
                             'no_result': "NO RESULT for test at line 5 of <stdin>\n"}
            global ExitError
            input = f"""import sys
sys.path = [r'{cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(workdir = '{tempdir}')
test.{condition}()
"""
            stdout, stderr, status = self.call_python(input, python="python")
            if close_true[condition]:
                unexpected = (status != 0)
            else:
                unexpected = (status == 0)
            if unexpected:
                msg = "Unexpected exit status from python:  %s\n"
                raise ExitError(msg % status + stdout + stderr)
            if status != exit_status[condition]:
                        msg = "Expected exit status %d, got %d\n"
                        raise ExitError(msg % (exit_status[condition], status))
            if stderr != result_string[condition]:
                msg = "Expected error output:\n%s\nGot error output:\n%s"
                raise ExitError(msg % (result_string[condition], stderr))
            if preserved:
                if not os.path.exists(tempdir):
                    msg = "Working directory %s was mistakenly removed\n"
                    raise ExitError(msg % tempdir + stdout)
            else:
                if os.path.exists(tempdir):
                    msg = "Working directory %s was mistakenly preserved\n"
                    raise ExitError(msg % tempdir + stdout)

        run_env = TestCmd.TestCmd(workdir = '')
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            cwd = self.orig_cwd
            _clear_dict(os.environ, 'PRESERVE', 'PRESERVE_PASS', 'PRESERVE_FAIL', 'PRESERVE_NO_RESULT')
            _test_it(cwd, 'dir01', 'pass_test', 0)
            _test_it(cwd, 'dir02', 'fail_test', 0)
            _test_it(cwd, 'dir03', 'no_result', 0)
            os.environ['PRESERVE'] = '1'
            _test_it(cwd, 'dir04', 'pass_test', 1)
            _test_it(cwd, 'dir05', 'fail_test', 1)
            _test_it(cwd, 'dir06', 'no_result', 1)
            del os.environ['PRESERVE']
            os.environ['PRESERVE_PASS'] = '1'
            _test_it(cwd, 'dir07', 'pass_test', 1)
            _test_it(cwd, 'dir08', 'fail_test', 0)
            _test_it(cwd, 'dir09', 'no_result', 0)
            del os.environ['PRESERVE_PASS']
            os.environ['PRESERVE_FAIL'] = '1'
            _test_it(cwd, 'dir10', 'pass_test', 0)
            _test_it(cwd, 'dir11', 'fail_test', 1)
            _test_it(cwd, 'dir12', 'no_result', 0)
            del os.environ['PRESERVE_FAIL']
            os.environ['PRESERVE_NO_RESULT'] = '1'
            _test_it(cwd, 'dir13', 'pass_test', 0)
            _test_it(cwd, 'dir14', 'fail_test', 0)
            _test_it(cwd, 'dir15', 'no_result', 1)
            del os.environ['PRESERVE_NO_RESULT']
        finally:
            _clear_dict(os.environ, 'PRESERVE', 'PRESERVE_PASS', 'PRESERVE_FAIL', 'PRESERVE_NO_RESULT')



class fail_test_TestCase(TestCmdTestCase):
    def test_fail_test(self):
        """Test fail_test()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run', """import sys
sys.stdout.write("run:  STDOUT\\n")
sys.stderr.write("run:  STDERR\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
TestCmd.fail_test(condition = 1)
""", status = 1, stderr = "FAILED test at line 4 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
test.fail_test(condition = (test.status == 0))
""", status = 1, stderr = f"FAILED test of {run_env.workpath('run')}\n\tat line 6 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', description = 'xyzzy', workdir = '')
test.run()
test.fail_test(condition = (test.status == 0))
""", status = 1, stderr = f"FAILED test of {run_env.workpath('run')} [xyzzy]\n\tat line 6 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
def xxx():
    sys.stderr.write("printed on failure\\n")
test.fail_test(condition = (test.status == 0), function = xxx)
""", status = 1, stderr = f"printed on failure\nFAILED test of {run_env.workpath('run')}\n\tat line 8 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def test1(self):
    self.run()
    self.fail_test(condition = (self.status == 0))
def test2(self):
    test1(self)
test2(TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = ''))
""", status = 1, stderr = f"FAILED test of {run_env.workpath('run')}\n\tat line 6 of <stdin> (test1)\n\tfrom line 8 of <stdin> (test2)\n\tfrom line 9 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def test1(self):
    self.run()
    self.fail_test(condition = (self.status == 0), skip = 1)
def test2(self):
    test1(self)
test2(TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = ''))
""", status = 1, stderr = f"FAILED test of {run_env.workpath('run')}\n\tat line 8 of <stdin> (test2)\n\tfrom line 9 of <stdin>\n")



class interpreter_TestCase(TestCmdTestCase):
    def test_interpreter(self):
        """Test interpreter()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run', """import sys
sys.stdout.write("run:  STDOUT\\n")
sys.stderr.write("run:  STDERR\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd(program = 'run', workdir = '')
        test.interpreter_set('foo')
        assert test.interpreter == 'foo', 'did not set interpreter'
        test.interpreter_set('python')
        assert test.interpreter == 'python', 'did not set interpreter'
        test.run()



class match_TestCase(TestCmdTestCase):
    def test_match_default(self):
        """Test match() default behavior"""
        test = TestCmd.TestCmd()
        assert test.match("abcde\n", "a.*e\n")
        assert test.match("12345\nabcde\n", "1\\d+5\na.*e\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = ["v[^a-u]*z\n", "6[^ ]+0\n"]
        assert test.match(lines, regexes)

    def test_match_custom_function(self):
        """Test match() using a custom function"""
        def match_length(lines, matches):
            return len(lines) == len(matches)
        test = TestCmd.TestCmd(match=match_length)
        assert not test.match("123\n", "1\n")
        assert test.match("123\n", "111\n")
        assert not test.match("123\n123\n", "1\n1\n")
        assert test.match("123\n123\n", "111\n111\n")
        lines = ["123\n", "123\n"]
        regexes = ["1\n", "1\n"]
        assert test.match(lines, regexes)       # due to equal numbers of lines

    def test_match_TestCmd_function(self):
        """Test match() using a TestCmd function"""
        test = TestCmd.TestCmd(match = TestCmd.match_exact)
        assert not test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert not test.match("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match(lines, regexes)
        assert test.match(lines, lines)

    def test_match_static_method(self):
        """Test match() using a static method"""
        test = TestCmd.TestCmd(match=TestCmd.TestCmd.match_exact)
        assert not test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert not test.match("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match(lines, regexes)
        assert test.match(lines, lines)

    def test_match_string(self):
        """Test match() using a string to fetch the match method"""
        test = TestCmd.TestCmd(match='match_exact')
        assert not test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert not test.match("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match(lines, regexes)
        assert test.match(lines, lines)



class match_exact_TestCase(TestCmdTestCase):
    def test_match_exact_function(self):
        """Test calling the TestCmd.match_exact() function"""
        assert not TestCmd.match_exact("abcde\\n", "a.*e\\n")
        assert TestCmd.match_exact("abcde\\n", "abcde\\n")

    def test_match_exact_instance_method(self):
        """Test calling the TestCmd.TestCmd().match_exact() instance method"""
        test = TestCmd.TestCmd()
        assert not test.match_exact("abcde\\n", "a.*e\\n")
        assert test.match_exact("abcde\\n", "abcde\\n")

    def test_match_exact_static_method(self):
        """Test calling the TestCmd.TestCmd.match_exact() static method"""
        assert not TestCmd.TestCmd.match_exact("abcde\\n", "a.*e\\n")
        assert TestCmd.TestCmd.match_exact("abcde\\n", "abcde\\n")

    def test_evaluation(self):
        """Test match_exact() evaluation"""
        test = TestCmd.TestCmd()
        assert not test.match_exact("abcde\n", "a.*e\n")
        assert test.match_exact("abcde\n", "abcde\n")
        assert not test.match_exact(["12345\n", "abcde\n"], ["1[0-9]*5\n", "a.*e\n"])
        assert test.match_exact(["12345\n", "abcde\n"], ["12345\n", "abcde\n"])
        assert not test.match_exact(UserList(["12345\n", "abcde\n"]),
                                    ["1[0-9]*5\n", "a.*e\n"])
        assert test.match_exact(UserList(["12345\n", "abcde\n"]),
                                ["12345\n", "abcde\n"])
        assert not test.match_exact(["12345\n", "abcde\n"],
                                    UserList(["1[0-9]*5\n", "a.*e\n"]))
        assert test.match_exact(["12345\n", "abcde\n"],
                                UserList(["12345\n", "abcde\n"]))
        assert not test.match_exact("12345\nabcde\n", "1[0-9]*5\na.*e\n")
        assert test.match_exact("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = ["v[^a-u]*z\n", "6[^ ]+0\n"]
        assert not test.match_exact(lines, regexes)
        assert test.match_exact(lines, lines)



class match_re_dotall_TestCase(TestCmdTestCase):
    def test_match_re_dotall_function(self):
        """Test calling the TestCmd.match_re_dotall() function"""
        assert TestCmd.match_re_dotall("abcde\nfghij\n", r"a.*j\n")

    def test_match_re_dotall_instance_method(self):
        """Test calling the TestCmd.TestCmd().match_re_dotall() instance method"""
        test = TestCmd.TestCmd()
        test.match_re_dotall("abcde\\nfghij\\n", r"a.*j\\n")

    def test_match_re_dotall_static_method(self):
        """Test calling the TestCmd.TestCmd.match_re_dotall() static method"""
        assert TestCmd.TestCmd.match_re_dotall("abcde\nfghij\n", r"a.*j\n")

    def test_error(self):
        """Test handling a compilation error in TestCmd.match_re_dotall()"""
        run_env = TestCmd.TestCmd(workdir = '')
        cwd = os.getcwd()
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            script_input = f"""import sys
sys.path = [r'{cwd}'] + sys.path
import TestCmd
assert TestCmd.match_re_dotall("abcde", r"a.*(e")
sys.exit(0)
"""
            stdout, stderr, status = self.call_python(script_input)
            assert status == 1, status
            expect1 = "Regular expression error in '^a.*(e$': missing )"
            expect2 = "Regular expression error in '^a.*(e$': unbalanced parenthesis"
            assert (stderr.find(expect1) != -1 or
                    stderr.find(expect2) != -1), repr(stderr)
        finally:
            os.chdir(cwd)

    def test_evaluation(self):
        """Test match_re_dotall() evaluation"""
        test = TestCmd.TestCmd()
        assert test.match_re_dotall("abcde\nfghij\n", r"a.*e\nf.*j\n")
        assert test.match_re_dotall("abcde\nfghij\n", r"a[^j]*j\n")
        assert test.match_re_dotall("abcde\nfghij\n", r"abcde\nfghij\n")
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    [r"1[0-9]*5\n", r"a.*e\n", r"f.*j\n"])
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    [r"1.*j\n"])
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    [r"12345\n", r"abcde\n", r"fghij\n"])
        assert test.match_re_dotall(UserList(["12345\n", "abcde\n", "fghij\n"]),
                                    [r"1[0-9]*5\n", r"a.*e\n", r"f.*j\n"])
        assert test.match_re_dotall(UserList(["12345\n", "abcde\n", "fghij\n"]),
                                    [r"1.*j\n"])
        assert test.match_re_dotall(UserList(["12345\n", "abcde\n", "fghij\n"]),
                                    [r"12345\n", r"abcde\n", r"fghij\n"])
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    UserList([r"1[0-9]*5\n", r"a.*e\n", r"f.*j\n"]))
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    UserList([r"1.*j\n"]))
        assert test.match_re_dotall(["12345\n", "abcde\n", "fghij\n"],
                                    UserList([r"12345\n", r"abcde\n", r"fghij\n"]))
        assert test.match_re_dotall("12345\nabcde\nfghij\n",
                                    r"1[0-9]*5\na.*e\nf.*j\n")
        assert test.match_re_dotall("12345\nabcde\nfghij\n", r"1.*j\n")
        assert test.match_re_dotall("12345\nabcde\nfghij\n",
                                    r"12345\nabcde\nfghij\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_re_dotall(lines, regexes)
        assert test.match_re_dotall(lines, lines)



class match_re_TestCase(TestCmdTestCase):
    def test_match_re_function(self):
        """Test calling the TestCmd.match_re() function"""
        assert TestCmd.match_re("abcde\n", "a.*e\n")

    def test_match_re_instance_method(self):
        """Test calling the TestCmd.TestCmd().match_re() instance method"""
        test = TestCmd.TestCmd()
        assert test.match_re("abcde\n", "a.*e\n")

    def test_match_re_static_method(self):
        """Test calling the TestCmd.TestCmd.match_re() static method"""
        assert TestCmd.TestCmd.match_re("abcde\n", "a.*e\n")

    def test_error(self):
        """Test handling a compilation error in TestCmd.match_re()"""
        run_env = TestCmd.TestCmd(workdir = '')
        cwd = os.getcwd()
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            script_input = f"""import sys
sys.path = [r'{cwd}'] + sys.path
import TestCmd
assert TestCmd.match_re("abcde\
", "a.*(e\
")
sys.exit(0)
"""
            stdout, stderr, status = self.call_python(script_input)
            assert status == 1, status
            expect1 = "Regular expression error in '^a.*(e$': missing )"
            expect2 = "Regular expression error in '^a.*(e$': unbalanced parenthesis"
            assert (stderr.find(expect1) != -1 or
                    stderr.find(expect2) != -1), repr(stderr)
        finally:
            os.chdir(cwd)

    def test_evaluation(self):
        """Test match_re() evaluation"""
        test = TestCmd.TestCmd()
        assert test.match_re("abcde\n", "a.*e\n")
        assert test.match_re("abcde\n", "abcde\n")
        assert test.match_re(["12345\n", "abcde\n"], ["1[0-9]*5\n", "a.*e\n"])
        assert test.match_re(["12345\n", "abcde\n"], ["12345\n", "abcde\n"])
        assert test.match_re(UserList(["12345\n", "abcde\n"]),
                             ["1[0-9]*5\n", "a.*e\n"])
        assert test.match_re(UserList(["12345\n", "abcde\n"]),
                             ["12345\n", "abcde\n"])
        assert test.match_re(["12345\n", "abcde\n"],
                             UserList(["1[0-9]*5\n", "a.*e\n"]))
        assert test.match_re(["12345\n", "abcde\n"],
                             UserList(["12345\n", "abcde\n"]))
        assert test.match_re("12345\nabcde\n", "1[0-9]*5\na.*e\n")
        assert test.match_re("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_re(lines, regexes)
        assert test.match_re(lines, lines)



class match_stderr_TestCase(TestCmdTestCase):
    def test_match_stderr_default(self):
        """Test match_stderr() default behavior"""
        test = TestCmd.TestCmd()
        assert test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_stderr(lines, regexes)

    def test_match_stderr_not_affecting_match_stdout(self):
        """Test match_stderr() not affecting match_stdout() behavior"""
        test = TestCmd.TestCmd(match_stderr=TestCmd.TestCmd.match_exact)

        assert not test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")
        assert not test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stderr("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stderr(lines, regexes)
        assert test.match_stderr(lines, lines)

        assert test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_stdout(lines, regexes)

    def test_match_stderr_custom_function(self):
        """Test match_stderr() using a custom function"""
        def match_length(lines, matches):
            return len(lines) == len(matches)
        test = TestCmd.TestCmd(match_stderr=match_length)
        assert not test.match_stderr("123\n", "1\n")
        assert test.match_stderr("123\n", "111\n")
        assert not test.match_stderr("123\n123\n", "1\n1\n")
        assert test.match_stderr("123\n123\n", "111\n111\n")
        lines = ["123\n", "123\n"]
        regexes = [r"1\n", r"1\n"]
        assert test.match_stderr(lines, regexes)    # equal numbers of lines

    def test_match_stderr_TestCmd_function(self):
        """Test match_stderr() using a TestCmd function"""
        test = TestCmd.TestCmd(match_stderr = TestCmd.match_exact)
        assert not test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")
        assert not test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stderr("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stderr(lines, regexes)
        assert test.match_stderr(lines, lines)

    def test_match_stderr_static_method(self):
        """Test match_stderr() using a static method"""
        test = TestCmd.TestCmd(match_stderr=TestCmd.TestCmd.match_exact)
        assert not test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")
        assert not test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stderr("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stderr(lines, regexes)
        assert test.match_stderr(lines, lines)

    def test_match_stderr_string(self):
        """Test match_stderr() using a string to fetch the match method"""
        test = TestCmd.TestCmd(match_stderr='match_exact')
        assert not test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")
        assert not test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stderr("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stderr(lines, regexes)
        assert test.match_stderr(lines, lines)



class match_stdout_TestCase(TestCmdTestCase):
    def test_match_stdout_default(self):
        """Test match_stdout() default behavior"""
        test = TestCmd.TestCmd()
        assert test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_stdout(lines, regexes)

    def test_match_stdout_not_affecting_match_stderr(self):
        """Test match_stdout() not affecting match_stderr() behavior"""
        test = TestCmd.TestCmd(match_stdout=TestCmd.TestCmd.match_exact)

        assert not test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")
        assert not test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stdout("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stdout(lines, regexes)
        assert test.match_stdout(lines, lines)

        assert test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("12345\nabcde\n", "1\\d+5\na.*e\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert test.match_stderr(lines, regexes)

    def test_match_stdout_custom_function(self):
        """Test match_stdout() using a custom function"""
        def match_length(lines, matches):
            return len(lines) == len(matches)
        test = TestCmd.TestCmd(match_stdout=match_length)
        assert not test.match_stdout("123\n", "1\n")
        assert test.match_stdout("123\n", "111\n")
        assert not test.match_stdout("123\n123\n", "1\n1\n")
        assert test.match_stdout("123\n123\n", "111\n111\n")
        lines = ["123\n", "123\n"]
        regexes = [r"1\n", r"1\n"]
        assert test.match_stdout(lines, regexes)    # equal numbers of lines

    def test_match_stdout_TestCmd_function(self):
        """Test match_stdout() using a TestCmd function"""
        test = TestCmd.TestCmd(match_stdout = TestCmd.match_exact)
        assert not test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")
        assert not test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stdout("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stdout(lines, regexes)
        assert test.match_stdout(lines, lines)

    def test_match_stdout_static_method(self):
        """Test match_stdout() using a static method"""
        test = TestCmd.TestCmd(match_stdout=TestCmd.TestCmd.match_exact)
        assert not test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")
        assert not test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stdout("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stdout(lines, regexes)
        assert test.match_stdout(lines, lines)

    def test_match_stdout_string(self):
        """Test match_stdout() using a string to fetch the match method"""
        test = TestCmd.TestCmd(match_stdout='match_exact')
        assert not test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")
        assert not test.match_stdout("12345\nabcde\n", "1\\d+5\na.*e\n")
        assert test.match_stdout("12345\nabcde\n", "12345\nabcde\n")
        lines = ["vwxyz\n", "67890\n"]
        regexes = [r"v[^a-u]*z\n", r"6[^ ]+0\n"]
        assert not test.match_stdout(lines, regexes)
        assert test.match_stdout(lines, lines)



class no_result_TestCase(TestCmdTestCase):
    def test_no_result(self):
        """Test no_result()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run', """import sys
sys.stdout.write("run:  STDOUT\\n")
sys.stderr.write("run:  STDERR\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
TestCmd.no_result(condition = 1)
""", status = 2, stderr = "NO RESULT for test at line 4 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
test.no_result(condition = (test.status == 0))
""", status = 2, stderr = f"NO RESULT for test of {run_env.workpath('run')}\n\tat line 6 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', description = 'xyzzy', workdir = '')
test.run()
test.no_result(condition = (test.status == 0))
""", status = 2, stderr = f"NO RESULT for test of {run_env.workpath('run')} [xyzzy]\n\tat line 6 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
def xxx():
    sys.stderr.write("printed on no result\\n")
test.no_result(condition = (test.status == 0), function = xxx)
""", status = 2, stderr = f"printed on no result\nNO RESULT for test of {run_env.workpath('run')}\n\tat line 8 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def test1(self):
    self.run()
    self.no_result(condition = (self.status == 0))
def test2(self):
    test1(self)
test2(TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = ''))
""", status = 2, stderr = f"NO RESULT for test of {run_env.workpath('run')}\n\tat line 6 of <stdin> (test1)\n\tfrom line 8 of <stdin> (test2)\n\tfrom line 9 of <stdin>\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
def test1(self):
    self.run()
    self.no_result(condition = (self.status == 0), skip = 1)
def test2(self):
    test1(self)
test2(TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = ''))
""", status = 2, stderr = f"NO RESULT for test of {run_env.workpath('run')}\n\tat line 8 of <stdin> (test2)\n\tfrom line 9 of <stdin>\n")



class pass_test_TestCase(TestCmdTestCase):
    def test_pass_test(self):
        """Test pass_test()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run', """import sys
sys.stdout.write("run:  STDOUT\\n")
sys.stderr.write("run:  STDERR\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
TestCmd.pass_test(condition = 1)
""", stderr = "PASSED\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
test.pass_test(condition = (test.status == 0))
""", stderr = "PASSED\n")

        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
test.run()
def brag():
    sys.stderr.write("printed on success\\n")
test.pass_test(condition = (test.status == 0), function = brag)
""", stderr = "printed on success\nPASSED\n")

        # TODO(sgk): SHOULD ALSO TEST FAILURE CONDITIONS



class preserve_TestCase(TestCmdTestCase):
    def test_preserve(self):
        """Test preserve()"""
        def cleanup_test(test, cond=None, stdout=""):
            save = sys.stdout
            with closing(StringIO()) as io:
                sys.stdout = io
                try:
                    if cond:
                        test.cleanup(cond)
                    else:
                        test.cleanup()
                    o = io.getvalue()
                    assert o == stdout, f"o = `{o}', stdout = `{stdout}'"
                finally:
                    sys.stdout = save

        test = TestCmd.TestCmd(workdir='')
        wdir = test.workdir
        try:
            test.write('file1', "Test file #1\n")
            #test.cleanup()
            cleanup_test(test, )
            assert not os.path.exists(wdir)
        finally:
            if os.path.exists(wdir):
                shutil.rmtree(wdir, ignore_errors=1)
                test._dirlist.remove(wdir)

        test = TestCmd.TestCmd(workdir='')
        wdir = test.workdir
        try:
            test.write('file2', "Test file #2\n")
            test.preserve('pass_test')
            cleanup_test(test, 'pass_test', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'fail_test')
            assert not os.path.exists(wdir)
        finally:
            if os.path.exists(wdir):
                shutil.rmtree(wdir, ignore_errors = 1)
                test._dirlist.remove(wdir)

        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        try:
            test.write('file3', "Test file #3\n")
            test.preserve('fail_test')
            cleanup_test(test, 'fail_test', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'pass_test')
            assert not os.path.exists(wdir)
        finally:
            if os.path.exists(wdir):
                shutil.rmtree(wdir, ignore_errors = 1)
                test._dirlist.remove(wdir)

        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        try:
            test.write('file4', "Test file #4\n")
            test.preserve('fail_test', 'no_result')
            cleanup_test(test, 'fail_test', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'no_result', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'pass_test')
            assert not os.path.exists(wdir)
        finally:
            if os.path.exists(wdir):
                shutil.rmtree(wdir, ignore_errors = 1)
                test._dirlist.remove(wdir)

        test = TestCmd.TestCmd(workdir = '')
        wdir = test.workdir
        try:
            test.preserve()
            cleanup_test(test, 'pass_test', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'fail_test', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
            cleanup_test(test, 'no_result', f"Preserved directory {wdir}\n")
            assert os.path.isdir(wdir)
        finally:
            if os.path.exists(wdir):
                shutil.rmtree(wdir, ignore_errors = 1)
                test._dirlist.remove(wdir)



class program_TestCase(TestCmdTestCase):
    def test_program(self):
        """Test program()"""
        test = TestCmd.TestCmd()
        assert test.program is None, 'initialized program?'
        test = TestCmd.TestCmd(program = 'test')
        assert test.program == os.path.join(os.getcwd(), 'test'), 'uninitialized program'
        test.program_set('foo')
        assert test.program == os.path.join(os.getcwd(), 'foo'), 'did not set program'



class read_TestCase(TestCmdTestCase):
    def test_read(self):
        """Test read()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        wdir_file1 = os.path.join(test.workdir, 'file1')
        wdir_file2 = os.path.join(test.workdir, 'file2')
        wdir_foo_file3 = os.path.join(test.workdir, 'foo', 'file3')
        wdir_file4 = os.path.join(test.workdir, 'file4')
        wdir_file5 = os.path.join(test.workdir, 'file5')

        with open(wdir_file1, 'wb') as f:
            f.write(to_bytes(""))
        with open(wdir_file2, 'wb') as f:
            f.write(to_bytes("Test\nfile\n#2.\n"))
        with open(wdir_foo_file3, 'wb') as f:
            f.write(to_bytes("Test\nfile\n#3.\n"))
        with open(wdir_file4, 'wb') as f:
            f.write(to_bytes("Test\nfile\n#4.\n"))
        with open(wdir_file5, 'wb') as f:
            f.write(to_bytes("Test\r\nfile\r\n#5.\r\n"))

        try:
            contents = test.read('no_file')
        except IOError:  # expect "No such file or directory"
            pass
        except:
            raise

        try:
            test.read(test.workpath('file_x'), mode = 'w')
        except ValueError:  # expect "mode must begin with 'r'
            pass
        except:
            raise

        def _file_matches(file, contents, expected):
            contents = to_str(contents)
            assert contents == expected, \
                "Expected contents of " + str(file) + "==========\n" + \
                expected + \
                "Actual contents of " + str(file) + "============\n" + \
                contents

        _file_matches(wdir_file1, test.read('file1'), "")
        _file_matches(wdir_file2, test.read('file2'), "Test\nfile\n#2.\n")
        _file_matches(wdir_foo_file3, test.read(['foo', 'file3']),
                        "Test\nfile\n#3.\n")
        _file_matches(wdir_foo_file3,
                      test.read(UserList(['foo', 'file3'])),
                        "Test\nfile\n#3.\n")
        _file_matches(wdir_file4, test.read('file4', mode = 'r'),
                        "Test\nfile\n#4.\n")
        _file_matches(wdir_file5, test.read('file5', mode = 'rb'),
                        "Test\r\nfile\r\n#5.\r\n")



class rmdir_TestCase(TestCmdTestCase):
    def test_rmdir(self):
        """Test rmdir()"""
        test = TestCmd.TestCmd(workdir = '')

        try:
            test.rmdir(['no', 'such', 'dir'])
        except EnvironmentError:
            pass
        else:
            raise Exception("did not catch expected SConsEnvironmentError")

        test.subdir(['sub'],
                    ['sub', 'dir'],
                    ['sub', 'dir', 'one'])

        s = test.workpath('sub')
        s_d = test.workpath('sub', 'dir')
        s_d_o = test.workpath('sub', 'dir', 'one')

        try:
            test.rmdir(['sub'])
        except EnvironmentError:
            pass
        else:
            raise Exception("did not catch expected SConsEnvironmentError")

        assert os.path.isdir(s_d_o), f"{s_d_o} is gone?"

        try:
            test.rmdir(['sub'])
        except EnvironmentError:
            pass
        else:
            raise Exception("did not catch expected SConsEnvironmentError")

        assert os.path.isdir(s_d_o), f"{s_d_o} is gone?"

        test.rmdir(['sub', 'dir', 'one'])

        assert not os.path.exists(s_d_o), f"{s_d_o} exists?"
        assert os.path.isdir(s_d), f"{s_d} is gone?"

        test.rmdir(['sub', 'dir'])

        assert not os.path.exists(s_d), f"{s_d} exists?"
        assert os.path.isdir(s), f"{s} is gone?"

        test.rmdir('sub')

        assert not os.path.exists(s), f"{s} exists?"



class run_TestCase(TestCmdTestCase):
    def test_run(self):
        """Test run()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            test.run()
            self.run_match(test.stdout(), t.script, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(test.stderr(), t.script, "STDERR", t.workdir,
                           repr([]))

            test.run(arguments = 'arg1 arg2 arg3')
            self.run_match(test.stdout(), t.script, "STDOUT", t.workdir,
                           repr(['arg1', 'arg2', 'arg3']))
            self.run_match(test.stderr(), t.script, "STDERR", t.workdir,
                           repr(['arg1', 'arg2', 'arg3']))

            test.run(program = t.scriptx, arguments = 'foo')
            self.run_match(test.stdout(), t.scriptx, "STDOUT", t.workdir,
                           repr(['foo']))
            self.run_match(test.stderr(), t.scriptx, "STDERR", t.workdir,
                           repr(['foo']))

            test.run(chdir = os.curdir, arguments = 'x y z')
            self.run_match(test.stdout(), t.script, "STDOUT", test.workdir,
                           repr(['x', 'y', 'z']))
            self.run_match(test.stderr(), t.script, "STDERR", test.workdir,
                           repr(['x', 'y', 'z']))

            test.run(chdir = 'script_subdir')
            script_subdir = test.workpath('script_subdir')
            self.run_match(test.stdout(), t.script, "STDOUT", script_subdir,
                           repr([]))
            self.run_match(test.stderr(), t.script, "STDERR", script_subdir,
                           repr([]))

            test.run(program = t.script1, interpreter = ['python', '-x'])
            self.run_match(test.stdout(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(test.stderr(), t.script1, "STDERR", t.workdir,
                           repr([]))

            try:
                test.run(chdir = 'no_subdir')
            except OSError:
                pass

            test.run(program = 'no_script', interpreter = 'python')
            assert test.status is not None, test.status

            try:
                test.run(program = 'no_script', interpreter = 'no_interpreter')
            except OSError:
                # Python versions that use subprocess throw an OSError
                # exception when they try to execute something that
                # isn't there.
                pass
            else:
                # Python versions that use os.popen3() or the Popen3
                # class run things through the shell, which just returns
                # a non-zero exit status.
                assert test.status is not None, test.status

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '',
                                    subdir = 't.scriptx_subdir')

            testx.run()
            self.run_match(testx.stdout(), t.scriptx, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(testx.stderr(), t.scriptx, "STDERR", t.workdir,
                           repr([]))

            testx.run(arguments = 'foo bar')
            self.run_match(testx.stdout(), t.scriptx, "STDOUT", t.workdir,
                           repr(['foo', 'bar']))
            self.run_match(testx.stderr(), t.scriptx, "STDERR", t.workdir,
                           repr(['foo', 'bar']))

            testx.run(program = t.script, interpreter = 'python', arguments = 'bar')
            self.run_match(testx.stdout(), t.script, "STDOUT", t.workdir,
                           repr(['bar']))
            self.run_match(testx.stderr(), t.script, "STDERR", t.workdir,
                           repr(['bar']))

            testx.run(chdir = os.curdir, arguments = 'baz')
            self.run_match(testx.stdout(), t.scriptx, "STDOUT", testx.workdir,
                           repr(['baz']))
            self.run_match(testx.stderr(), t.scriptx, "STDERR", testx.workdir,
                           repr(['baz']))

            testx.run(chdir = 't.scriptx_subdir')
            t.scriptx_subdir = testx.workpath('t.scriptx_subdir')
            self.run_match(testx.stdout(), t.scriptx, "STDOUT", t.scriptx_subdir,
                           repr([]))
            self.run_match(testx.stderr(), t.scriptx, "STDERR", t.scriptx_subdir,
                           repr([]))

            testx.run(program = t.script1, interpreter = ('python', '-x'))
            self.run_match(testx.stdout(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(testx.stderr(), t.script1, "STDERR", t.workdir,
                           repr([]))

            s = os.path.join('.', t.scriptx)
            testx.run(program = [s])
            self.run_match(testx.stdout(), t.scriptx, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(testx.stderr(), t.scriptx, "STDERR", t.workdir,
                           repr([]))

            try:
                testx.run(chdir = 'no_subdir')
            except OSError:
                pass

            try:
                testx.run(program = 'no_program')
            except OSError:
                # Python versions that use subprocess throw an OSError
                # exception when they try to execute something that
                # isn't there.
                pass
            else:
                # Python versions that use os.popen3() or the Popen3
                # class run things through the shell, which just returns
                # a non-zero exit status.
                assert test.status is not None

            test1 = TestCmd.TestCmd(program = t.script1,
                                    interpreter = ['python', '-x'],
                                    workdir = '')

            test1.run()
            self.run_match(test1.stdout(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(test1.stderr(), t.script1, "STDERR", t.workdir,
                           repr([]))

        finally:
            os.chdir(t.orig_cwd)

    def test_run_subclass(self):
        """Test run() through a subclass with different signatures"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.

        class MyTestCmdSubclass(TestCmd.TestCmd):
            def start(self, additional_argument=None, **kw):
                return TestCmd.TestCmd.start(self, **kw)

        try:
            test = MyTestCmdSubclass(program = t.script,
                                     interpreter = 'python',
                                     workdir = '',
                                     subdir = 'script_subdir')

            test.run()
            self.run_match(test.stdout(), t.script, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(test.stderr(), t.script, "STDERR", t.workdir,
                           repr([]))
        finally:
            os.chdir(t.orig_cwd)


class run_verbose_TestCase(TestCmdTestCase):
    def test_run_verbose(self):
        """Test the run() method's verbose attribute"""

        # Prepare our "source directory."
        t = self.setup_run_scripts()

        save_stdout = sys.stderr
        save_stderr = sys.stderr

        try:
            # Test calling TestCmd() with an explicit verbose = 1.

            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   verbose = 1)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])
                o = sys.stdout.getvalue()
                assert o == '', o
                e = sys.stderr.getvalue()
                expect = f'python "{t.script_path}" "arg1 arg2\"\n'
                assert expect == e, (expect, e)

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '',
                                    verbose = 1)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                testx.run(arguments = ['arg1 arg2'])
                expect = f'"{t.scriptx_path}" "arg1 arg2\"\n'
                o = sys.stdout.getvalue()
                assert o == '', o
                e = sys.stderr.getvalue()
                assert expect == e, (expect, e)

            # Test calling TestCmd() with an explicit verbose = 2.

            outerr_fmt = """\
============ STATUS: 0
============ BEGIN STDOUT (len=%s):
%s============ END STDOUT
============ BEGIN STDERR (len=%s)
%s============ END STDERR
"""

            out_fmt = """\
============ STATUS: 0
============ BEGIN STDOUT (len=%s):
%s============ END STDOUT
"""

            err_fmt = """\
============ STATUS: 0
============ BEGIN STDERR (len=%s)
%s============ END STDERR
"""

            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   verbose = 2)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])

                line_fmt = "script:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                stderr_line = line_fmt % ('STDERR', t.sub_dir)
                expect = outerr_fmt % (len(stdout_line), stdout_line,
                                       len(stderr_line), stderr_line)
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                expect = f'python "{t.script_path}" "arg1 arg2\"\n'
                e = sys.stderr.getvalue()
                assert e == expect, (e, expect)

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '',
                                    verbose = 2)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                testx.run(arguments = ['arg1 arg2'])

                line_fmt = "scriptx.bat:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                stderr_line = line_fmt % ('STDERR', t.sub_dir)
                expect = outerr_fmt % (len(stdout_line), stdout_line,
                                       len(stderr_line), stderr_line)
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                expect = f'"{t.scriptx_path}" "arg1 arg2\"\n'
                e = sys.stderr.getvalue()
                assert e == expect, (e, expect)

            # Test calling TestCmd() with an explicit verbose = 3.

            test = TestCmd.TestCmd(program = t.scriptout,
                                   interpreter = 'python',
                                   workdir = '',
                                   verbose = 2)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])

                line_fmt = "scriptout:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                expect = out_fmt % (len(stdout_line), stdout_line)
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                e = sys.stderr.getvalue()
                expect = f'python "{t.scriptout_path}" "arg1 arg2\"\n'
                assert e == expect, (e, expect)

            test = TestCmd.TestCmd(program = t.scriptout,
                                   interpreter = 'python',
                                   workdir = '',
                                   verbose = 3)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])

                line_fmt = "scriptout:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                expect = outerr_fmt % (len(stdout_line), stdout_line,
                                       '0', '')
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                e = sys.stderr.getvalue()
                expect = f'python "{t.scriptout_path}" "arg1 arg2\"\n'
                assert e == expect, (e, expect)

            # Test letting TestCmd() pick up verbose = 2 from the environment.

            os.environ['TESTCMD_VERBOSE'] = '2'

            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '')

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])

                line_fmt = "script:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                stderr_line = line_fmt % ('STDERR', t.sub_dir)
                expect = outerr_fmt % (len(stdout_line), stdout_line,
                                       len(stderr_line), stderr_line)
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                expect = f'python "{t.script_path}" "arg1 arg2\"\n'
                e = sys.stderr.getvalue()
                assert e == expect, (e, expect)

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '')

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                testx.run(arguments = ['arg1 arg2'])

                line_fmt = "scriptx.bat:  %s:  %s:  ['arg1 arg2']\n"
                stdout_line = line_fmt % ('STDOUT', t.sub_dir)
                stderr_line = line_fmt % ('STDERR', t.sub_dir)
                expect = outerr_fmt % (len(stdout_line), stdout_line,
                                       len(stderr_line), stderr_line)
                o = sys.stdout.getvalue()
                assert expect == o, (expect, o)

                expect = f'"{t.scriptx_path}" "arg1 arg2\"\n'
                e = sys.stderr.getvalue()
                assert e == expect, (e, expect)

            # Test letting TestCmd() pick up verbose = 1 from the environment.

            os.environ['TESTCMD_VERBOSE'] = '1'

            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   verbose = 1)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                test.run(arguments = ['arg1 arg2'])
                o = sys.stdout.getvalue()
                assert o == '', o
                e = sys.stderr.getvalue()
                expect = f'python "{t.script_path}" "arg1 arg2\"\n'
                assert expect == e, (expect, e)

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '',
                                    verbose = 1)

            with closing(StringIO()) as sys.stdout, closing(StringIO()) as sys.stderr:
                testx.run(arguments = ['arg1 arg2'])
                expect = f'"{t.scriptx_path}" "arg1 arg2\"\n'
                o = sys.stdout.getvalue()
                assert o == '', o
                e = sys.stderr.getvalue()
                assert expect == e, (expect, e)

        finally:
            sys.stdout = save_stdout
            sys.stderr = save_stderr
            os.chdir(t.orig_cwd)
            os.environ['TESTCMD_VERBOSE'] = ''



class set_diff_function_TestCase(TestCmdTestCase):
    def test_set_diff_function(self):
        """Test set_diff_function()"""
        self.popen_python(fr"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd()
test.diff("a\n", "a\n")
test.set_diff_function('diff_re')
test.diff(".\n", "a\n")
sys.exit(0)
""")

    def test_set_diff_function_stdout(self):
        """Test set_diff_function():  stdout"""
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd()
print("diff:")
test.diff("a\\n", "a\\n")
print("diff_stdout:")
test.diff_stdout("a\\n", "a\\n")
test.set_diff_function(stdout='diff_re')
print("diff:")
test.diff(".\\n", "a\\n")
print("diff_stdout:")
test.diff_stdout(".\\n", "a\\n")
sys.exit(0)
""",
                          stdout="""\
diff:
diff_stdout:
diff:
1c1
< .
---
> a
diff_stdout:
""")

    def test_set_diff_function_stderr(self):
        """Test set_diff_function():  stderr """
        self.popen_python(f"""import sys
sys.path = [r'{self.orig_cwd}'] + sys.path
import TestCmd
test = TestCmd.TestCmd()
print("diff:")
test.diff("a\\n", "a\\n")
print("diff_stderr:")
test.diff_stderr("a\\n", "a\\n")
test.set_diff_function(stderr='diff_re')
print("diff:")
test.diff(".\\n", "a\\n")
print("diff_stderr:")
test.diff_stderr(".\\n", "a\\n")
sys.exit(0)
""",
                          stdout="""\
diff:
diff_stderr:
diff:
1c1
< .
---
> a
diff_stderr:
""")



class set_match_function_TestCase(TestCmdTestCase):
    def test_set_match_function(self):
        """Test set_match_function()"""
        test = TestCmd.TestCmd()
        assert test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")

        test.set_match_function('match_exact')

        assert not test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")

    def test_set_match_function_stdout(self):
        """Test set_match_function():  stdout """
        test = TestCmd.TestCmd()
        assert test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")

        test.set_match_function(stdout='match_exact')

        assert test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert not test.match_stdout("abcde\n", "a.*e\n")
        assert test.match_stdout("abcde\n", "abcde\n")

    def test_set_match_function_stderr(self):
        """Test set_match_function():  stderr """
        test = TestCmd.TestCmd()
        assert test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")

        test.set_match_function(stderr='match_exact')

        assert test.match("abcde\n", "a.*e\n")
        assert test.match("abcde\n", "abcde\n")
        assert not test.match_stderr("abcde\n", "a.*e\n")
        assert test.match_stderr("abcde\n", "abcde\n")



class sleep_TestCase(TestCmdTestCase):
    def test_sleep(self):
        """Test sleep()"""
        test = TestCmd.TestCmd()

        start = time.perf_counter()
        test.sleep()
        end = time.perf_counter()
        diff = end - start
        assert diff > 0.9, f"only slept {diff:f} seconds (start {start:f}, end {end:f}), not default"

        start = time.perf_counter()
        test.sleep(3)
        end = time.perf_counter()
        diff = end - start
        assert diff > 2.9, f"only slept {diff:f} seconds (start {start:f}, end {end:f}), not 3"



class stderr_TestCase(TestCmdTestCase):
    def test_stderr(self):
        """Test stderr()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run1', """import sys
sys.stdout.write("run1 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run1 STDOUT second line\\n")
sys.stderr.write("run1 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run1 STDERR second line\\n")
""")
        run_env.write('run2', """import sys
sys.stdout.write("run2 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run2 STDOUT second line\\n")
sys.stderr.write("run2 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run2 STDERR second line\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd(interpreter = 'python', workdir = '')
        try:
            output = test.stderr()
        except IndexError:
            pass
        else:
            if output is not None:
                raise IndexError(f"got unexpected output:\n{output}")
        test.program_set('run1')
        test.run(arguments = 'foo bar')
        test.program_set('run2')
        test.run(arguments = 'snafu')
        # XXX SHOULD TEST ABSOLUTE NUMBER AS WELL
        output = test.stderr()
        assert output == "run2 STDERR ['snafu']\nrun2 STDERR second line\n", output
        output = test.stderr(run = -1)
        assert output == "run1 STDERR ['foo', 'bar']\nrun1 STDERR second line\n", output



class command_args_TestCase(TestCmdTestCase):
    def test_command_args(self):
        """Test command_args()"""
        run_env = TestCmd.TestCmd(workdir = '')
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd(workdir = '')

        r = test.command_args('prog')
        expect = [run_env.workpath('prog')]
        assert r == expect, (expect, r)

        r = test.command_args(test.workpath('new_prog'))
        expect = [test.workpath('new_prog')]
        assert r == expect, (expect, r)

        r = test.command_args('prog', 'python')
        expect = ['python', run_env.workpath('prog')]
        assert r == expect, (expect, r)

        r = test.command_args('prog', 'python', 'arg1 arg2')
        expect = ['python', run_env.workpath('prog'), 'arg1', 'arg2']
        assert r == expect, (expect, r)

        test.program_set('default_prog')
        default_prog = run_env.workpath('default_prog')

        r = test.command_args()
        expect = [default_prog]
        assert r == expect, (expect, r)

        r = test.command_args(interpreter='PYTHON')
        expect = ['PYTHON', default_prog]
        assert r == expect, (expect, r)

        r = test.command_args(interpreter='PYTHON', arguments='arg3 arg4')
        expect = ['PYTHON', default_prog, 'arg3', 'arg4']
        assert r == expect, (expect, r)

        # Test arguments = dict
        r = test.command_args(interpreter='PYTHON', arguments={'VAR1':'1'})
        expect = ['PYTHON', default_prog, 'VAR1=1']
        assert r == expect, (expect, r)


        test.interpreter_set('default_python')

        r = test.command_args()
        expect = ['default_python', default_prog]
        assert r == expect, (expect, r)

        r = test.command_args(arguments='arg5 arg6')
        expect = ['default_python', default_prog, 'arg5', 'arg6']
        assert r == expect, (expect, r)

        r = test.command_args('new_prog_1')
        expect = [run_env.workpath('new_prog_1')]
        assert r == expect, (expect, r)

        r = test.command_args(program='new_prog_2')
        expect = [run_env.workpath('new_prog_2')]
        assert r == expect, (expect, r)



class start_TestCase(TestCmdTestCase):
    def setup_run_scripts(self):
        t = TestCmdTestCase.setup_run_scripts(self)
        t.recv_script = 'script_recv'
        t.recv_script_path = t.run_env.workpath(t.sub_dir, t.recv_script)
        t.recv_out_path = t.run_env.workpath('script_recv.out')
        text = f"""import os
import sys

class Unbuffered:
    def __init__(self, file):
        self.file = file
    def write(self, arg):
        self.file.write(arg)
        self.file.flush()
    def __getattr__(self, attr):
        return getattr(self.file, attr)

sys.stdout = Unbuffered(sys.stdout)
sys.stderr = Unbuffered(sys.stderr)

sys.stdout.write('script_recv:  STDOUT\\n')
sys.stderr.write('script_recv:  STDERR\\n')
with open(r'{t.recv_out_path}', 'w') as logfp:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        logfp.write('script_recv:  ' + line)
        sys.stdout.write('script_recv:  STDOUT:  ' + line)
        sys.stderr.write('script_recv:  STDERR:  ' + line)
"""
        t.run_env.write(t.recv_script_path, text)
        os.chmod(t.recv_script_path, 0o644)  # XXX UNIX-specific
        return t

    def _cleanup(self, popen):
        """Quiet Python ResourceWarning after wait()"""
        if popen.stdout:
            popen.stdout.close()
        if popen.stderr:
            popen.stderr.close()

    def test_start(self):
        """Test start()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            p = test.start()
            self.run_match(p.stdout.read(), t.script, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.script, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

            p = test.start(arguments='arg1 arg2 arg3')
            self.run_match(p.stdout.read(), t.script, "STDOUT", t.workdir,
                           repr(['arg1', 'arg2', 'arg3']))
            self.run_match(p.stderr.read(), t.script, "STDERR", t.workdir,
                           repr(['arg1', 'arg2', 'arg3']))
            p.wait()
            self._cleanup(p)

            p = test.start(program=t.scriptx, arguments='foo')
            self.run_match(p.stdout.read(), t.scriptx, "STDOUT", t.workdir,
                           repr(['foo']))
            self.run_match(p.stderr.read(), t.scriptx, "STDERR", t.workdir,
                           repr(['foo']))
            p.wait()
            self._cleanup(p)

            p = test.start(program=t.script1, interpreter=['python', '-x'])
            self.run_match(p.stdout.read(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.script1, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

            p = test.start(program='no_script', interpreter='python')
            status = p.wait()
            self._cleanup(p)
            assert status is not None, status

            try:
                p = test.start(program='no_script', interpreter='no_interpreter')
            except OSError:
                # Python versions that use subprocess throw an OSError
                # exception when they try to execute something that
                # isn't there.
                pass
            else:
                status = p.wait()
                self._cleanup(p)
                # Python versions that use os.popen3() or the Popen3
                # class run things through the shell, which just returns
                # a non-zero exit status.
                assert status is not None, status

            testx = TestCmd.TestCmd(program = t.scriptx,
                                    workdir = '',
                                    subdir = 't.scriptx_subdir')

            p = testx.start()
            self.run_match(p.stdout.read(), t.scriptx, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.scriptx, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

            p = testx.start(arguments='foo bar')
            self.run_match(p.stdout.read(), t.scriptx, "STDOUT", t.workdir,
                           repr(['foo', 'bar']))
            self.run_match(p.stderr.read(), t.scriptx, "STDERR", t.workdir,
                           repr(['foo', 'bar']))
            p.wait()
            self._cleanup(p)

            p = testx.start(program=t.script, interpreter='python', arguments='bar')
            self.run_match(p.stdout.read(), t.script, "STDOUT", t.workdir,
                           repr(['bar']))
            self.run_match(p.stderr.read(), t.script, "STDERR", t.workdir,
                           repr(['bar']))
            p.wait()
            self._cleanup(p)

            p = testx.start(program=t.script1, interpreter=('python', '-x'))
            self.run_match(p.stdout.read(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.script1, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

            s = os.path.join('.', t.scriptx)
            p = testx.start(program=[s])
            self.run_match(p.stdout.read(), t.scriptx, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.scriptx, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

            try:
                testx.start(program='no_program')
            except OSError:
                # Python versions that use subprocess throw an OSError
                # exception when they try to execute something that
                # isn't there.
                pass
            else:
                # Python versions that use os.popen3() or the Popen3
                # class run things through the shell, which just dies
                # trying to execute the non-existent program before
                # we can wait() for it.
                try:
                    p = p.wait()
                    self._cleanup(p)
                except OSError:
                    pass

            test1 = TestCmd.TestCmd(program = t.script1,
                                    interpreter = ['python', '-x'],
                                    workdir = '')

            p = test1.start()
            self.run_match(p.stdout.read(), t.script1, "STDOUT", t.workdir,
                           repr([]))
            self.run_match(p.stderr.read(), t.script1, "STDERR", t.workdir,
                           repr([]))
            p.wait()
            self._cleanup(p)

        finally:
            os.chdir(t.orig_cwd)

    def test_finish(self):
        """Test finish()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:

            test = TestCmd.TestCmd(program = t.recv_script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            test.start(stdin=1)
            test.finish()
            expect_stdout = """\
script_recv:  STDOUT
"""
            expect_stderr = """\
script_recv:  STDERR
"""
            stdout = test.stdout()
            assert stdout == expect_stdout, stdout
            stderr = test.stderr()
            assert stderr == expect_stderr, stderr

            p = test.start(stdin=1)
            p.send('input\n')
            test.finish(p)
            expect_stdout = """\
script_recv:  STDOUT
script_recv:  STDOUT:  input
"""
            expect_stderr = """\
script_recv:  STDERR
script_recv:  STDERR:  input
"""
            stdout = test.stdout()
            assert stdout == expect_stdout, stdout
            stderr = test.stderr()
            assert stderr == expect_stderr, stderr

            p = test.start(combine=True, stdin=1)
            p.send('input\n')
            test.finish(p)
            expect_stdout = """\
script_recv:  STDOUT
script_recv:  STDERR
script_recv:  STDOUT:  input
script_recv:  STDERR:  input
"""
            expect_stderr = ""
            stdout = test.stdout()
            assert stdout == expect_stdout, stdout
            stderr = test.stderr()
            assert stderr == expect_stderr, stderr

        finally:
            os.chdir(t.orig_cwd)

    def test_recv(self):
        """Test the recv() method of objects returned by start()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:
            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            p = test.start()
            stdout = p.recv()
            while stdout == '':
                import time
                time.sleep(1)
                stdout = p.recv()
            self.run_match(stdout, t.script, "STDOUT", t.workdir,
                           repr([]))
            p.wait()

        finally:
            os.chdir(t.orig_cwd)

    def test_recv_err(self):
        """Test the recv_err() method of objects returned by start()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:

            test = TestCmd.TestCmd(program = t.script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            p = test.start()
            stderr = p.recv_err()
            while stderr == '':
                import time
                time.sleep(1)
                stderr = p.recv_err()
            self.run_match(stderr, t.script, "STDERR", t.workdir,
                           repr([]))
            p.wait()


        finally:
            os.chdir(t.orig_cwd)

    def test_send(self):
        """Test the send() method of objects returned by start()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:

            test = TestCmd.TestCmd(program = t.recv_script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            p = test.start(stdin=1)
            input = 'stdin.write() input to the receive script\n'
            p.stdin.write(to_bytes(input))
            p.stdin.close()
            p.wait()
            with open(t.recv_out_path, 'r') as f:
                result = to_str(f.read())
            expect = f"script_recv:  {input}"
            assert result == expect, f"Result:[{result}] should match\nExpected:[{expect}]"

            p = test.start(stdin=1)
            input = 'send() input to the receive script\n'
            p.send(input)
            p.stdin.close()
            p.wait()
            with open(t.recv_out_path, 'r') as f:
                result = to_str(f.read())
            expect = f"script_recv:  {input}"
            assert result == expect, repr(result)

        finally:
            os.chdir(t.orig_cwd)

    # TODO(sgk):  figure out how to eliminate the race conditions here.
    def __FLAKY__test_send_recv(self):
        """Test the send_recv() method of objects returned by start()"""

        t = self.setup_run_scripts()

        # Everything before this prepared our "source directory."
        # Now do the real test.
        try:

            test = TestCmd.TestCmd(program = t.recv_script,
                                   interpreter = 'python',
                                   workdir = '',
                                   subdir = 'script_subdir')

            def do_send_recv(p, input):
                send, stdout, stderr = p.send_recv(input)
                stdout = self.translate_newlines(stdout)
                stderr = self.translate_newlines(stderr)
                return send, stdout, stderr

            p = test.start(stdin=1)
            input = 'input to the receive script\n'
            send, stdout, stderr = do_send_recv(p, input)
            # Buffering issues and a race condition prevent this from
            # being completely deterministic, so check for both null
            # output and the first write() on each stream.
            assert stdout in ("", "script_recv:  STDOUT\n"), stdout
            assert stderr in ("", "script_recv:  STDERR\n"), stderr
            send, stdout, stderr = do_send_recv(p, input)
            assert stdout in ("", "script_recv:  STDOUT\n"), stdout
            assert stderr in ("", "script_recv:  STDERR\n"), stderr
            p.stdin.close()
            stdout = self.translate_newlines(p.recv())
            stderr = self.translate_newlines(p.recv_err())
            assert stdout in ("", "script_recv:  STDOUT\n"), stdout
            assert stderr in ("", "script_recv:  STDERR\n"), stderr
            p.wait()
            stdout = self.translate_newlines(p.recv())
            stderr = self.translate_newlines(p.recv_err())
            expect_stdout = """\
script_recv:  STDOUT
script_recv:  STDOUT:  input to the receive script
script_recv:  STDOUT:  input to the receive script
"""
            expect_stderr = """\
script_recv:  STDERR
script_recv:  STDERR:  input to the receive script
script_recv:  STDERR:  input to the receive script
"""
            assert stdout == expect_stdout, stdout
            assert stderr == expect_stderr, stderr
            with open(t.recv_out_path, 'rb') as f:
                result = f.read()
            expect = f"script_recv:  {input}" * 2
            assert result == expect, (result, stdout, stderr)

        finally:
            os.chdir(t.orig_cwd)



class stdin_TestCase(TestCmdTestCase):
    def test_stdin(self):
        """Test stdin()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run', """\
import fileinput
for line in fileinput.input():
    print('Y'.join(line[:-1].split('X')))
""")
        run_env.write('input', "X on X this X line X\n")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd(program = 'run', interpreter = 'python', workdir = '')
        test.run(arguments = 'input')
        assert test.stdout() == "Y on Y this Y line Y\n"
        test.run(stdin = "X is X here X tooX\n")
        assert test.stdout() == "Y is Y here Y tooY\n"
        test.run(stdin = """X here X
X there X
""")
        assert test.stdout() == "Y here Y\nY there Y\n"
        test.run(stdin = ["X line X\n", "X another X\n"])
        assert test.stdout() == "Y line Y\nY another Y\n"



class stdout_TestCase(TestCmdTestCase):
    def test_stdout(self):
        """Test stdout()"""
        run_env = TestCmd.TestCmd(workdir = '')
        run_env.write('run1', """\
import sys
sys.stdout.write("run1 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run1 STDOUT second line\\n")
sys.stderr.write("run1 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run1 STDERR second line\\n")
""")
        run_env.write('run2', """\
import sys
sys.stdout.write("run2 STDOUT %s\\n" % sys.argv[1:])
sys.stdout.write("run2 STDOUT second line\\n")
sys.stderr.write("run2 STDERR %s\\n" % sys.argv[1:])
sys.stderr.write("run2 STDERR second line\\n")
""")
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd(interpreter = 'python', workdir = '')
        output = test.stdout()
        if output is not None:
            raise IndexError(f"got unexpected output:\n\t`{output}'\n")
        test.program_set('run1')
        test.run(arguments = 'foo bar')
        test.program_set('run2')
        test.run(arguments = 'snafu')
        # XXX SHOULD TEST ABSOLUTE NUMBER AS WELL
        output = test.stdout()
        assert output == "run2 STDOUT ['snafu']\nrun2 STDOUT second line\n", output
        output = test.stdout(run = -1)
        assert output == "run1 STDOUT ['foo', 'bar']\nrun1 STDOUT second line\n", output


class subdir_TestCase(TestCmdTestCase):
    def test_subdir(self):
        """Test subdir()"""
        # intermediate directories are created
        test = TestCmd.TestCmd(workdir='', subdir=['no', 'such', 'subdir'])
        assert os.path.exists(test.workpath('no'))

        test = TestCmd.TestCmd(workdir='', subdir='foo')
        assert os.path.isdir(test.workpath('foo'))

        # single subdir
        assert test.subdir('bar')
        assert os.path.isdir(test.workpath('bar'))

        # subdir "works" even if existing
        assert test.subdir('bar')

        # single subdir as a list
        assert test.subdir(['foo', 'succeed'])
        assert os.path.isdir(test.workpath('foo', 'succeed'))

        if os.name != "nt":
            assert not os.path.exists(test.workpath('foo', 'fail'))

        # subdir creation without write permissions fails
        if os.name != "nt":
            os.chmod(test.workpath('foo'), 0o500)
            assert not test.subdir(['foo', 'fail'])

        # create descended path
        assert test.subdir(['sub', 'dir', 'ectory'])
        assert os.path.isdir(test.workpath('sub'))
        assert os.path.exists(test.workpath('sub', 'dir'))
        assert os.path.exists(test.workpath('sub', 'dir', 'ectory'))

        # test multiple subdirs in one call, each should "succeed"
        assert (
            test.subdir('one', UserList(['one', 'two']), ['one', 'two', 'three']) == 3
        )
        assert os.path.isdir(test.workpath('one', 'two', 'three'))


class symlink_TestCase(TestCmdTestCase):
    @unittest.skipIf(sys.platform == 'win32', "Skip symlink test on win32")
    def test_symlink(self):
        """Test symlink()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        wdir_file1 = os.path.join(test.workdir, 'file1')
        wdir_target1 = os.path.join(test.workdir, 'target1')
        wdir_foo_file2 = os.path.join(test.workdir, 'foo', 'file2')
        wdir_target2 = os.path.join(test.workdir, 'target2')
        wdir_foo_target2 = os.path.join(test.workdir, 'foo', 'target2')

        test.symlink('target1', 'file1')
        assert os.path.islink(wdir_file1)
        assert not os.path.exists(wdir_file1)
        with open(wdir_target1, 'w') as f:
            f.write("")
        assert os.path.exists(wdir_file1)

        test.symlink('target2', ['foo', 'file2'])
        assert os.path.islink(wdir_foo_file2)
        assert not os.path.exists(wdir_foo_file2)
        with open(wdir_target2, 'w') as f:
            f.write("")
        assert not os.path.exists(wdir_foo_file2)
        with open(wdir_foo_target2, 'w') as f:
            f.write("")
        assert os.path.exists(wdir_foo_file2)



class tempdir_TestCase(TestCmdTestCase):
    def setUp(self):
        TestCmdTestCase.setUp(self)
        self._tempdir = tempfile.mkdtemp()
        os.chdir(self._tempdir)

    def tearDown(self):
        TestCmdTestCase.tearDown(self)
        os.rmdir(self._tempdir)

    def test_tempdir(self):
        """Test tempdir()"""
        test = TestCmd.TestCmd()
        tdir1 = test.tempdir()
        assert os.path.isdir(tdir1)
        test.workdir_set(None)
        test.cleanup()
        assert not os.path.exists(tdir1)

        test = TestCmd.TestCmd()
        tdir2 = test.tempdir('temp')
        assert os.path.isdir(tdir2)
        tdir3 = test.tempdir()
        assert os.path.isdir(tdir3)
        test.workdir_set(None)
        test.cleanup()
        assert not os.path.exists(tdir2)
        assert not os.path.exists(tdir3)


timeout_script = """\
import sys
import time
seconds = int(sys.argv[1])
sys.stdout.write('sleeping %s\\n' % seconds)
sys.stdout.flush()
time.sleep(seconds)
sys.stdout.write('slept %s\\n' % seconds)
sys.stdout.flush()
sys.exit(0)
"""

class timeout_TestCase(TestCmdTestCase):
    def test_initialization(self):
        """Test initializating a TestCmd with a timeout"""
        test = TestCmd.TestCmd(workdir='', timeout=2)
        test.write('sleep.py', timeout_script)

        test.run([sys.executable, test.workpath('sleep.py'), '4'])
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 4\n', test.stdout()

        test.run([sys.executable, test.workpath('sleep.py'), '4'])
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 4\n', test.stdout()

    def test_cancellation(self):
        """Test timer cancellation after firing"""
        test = TestCmd.TestCmd(workdir='', timeout=4)
        test.write('sleep.py', timeout_script)

        test.run([sys.executable, test.workpath('sleep.py'), '6'])
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 6\n', test.stdout()

        test.run([sys.executable, test.workpath('sleep.py'), '2'])
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 2\nslept 2\n', test.stdout()

        test.run([sys.executable, test.workpath('sleep.py'), '6'])
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 6\n', test.stdout()

    def test_run(self):
        """Test run() timeout"""
        test = TestCmd.TestCmd(workdir='', timeout=8)
        test.write('sleep.py', timeout_script)

        test.run([sys.executable, test.workpath('sleep.py'), '2'], timeout=4)
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 2\nslept 2\n', test.stdout()

        test.run([sys.executable, test.workpath('sleep.py'), '6'], timeout=4)
        assert test.stderr() == '', test.stderr()
        assert test.stdout() == 'sleeping 6\n', test.stdout()

    # This method has been removed
    #def test_set_timeout(self):
    #    """Test set_timeout()"""
    #    test = TestCmd.TestCmd(workdir='', timeout=2)
    #    test.write('sleep.py', timeout_script)
    #
    #    test.run([sys.executable, test.workpath('sleep.py'), '4'])
    #    assert test.stderr() == '', test.stderr()
    #    assert test.stdout() == 'sleeping 4\n', test.stdout()
    #
    #    test.set_timeout(None)
    #
    #    test.run([sys.executable, test.workpath('sleep.py'), '4'])
    #    assert test.stderr() == '', test.stderr()
    #    assert test.stdout() == 'sleeping 4\nslept 4\n', test.stdout()
    #
    #    test.set_timeout(6)
    #
    #    test.run([sys.executable, test.workpath('sleep.py'), '4'])
    #    assert test.stderr() == '', test.stderr()
    #    assert test.stdout() == 'sleeping 4\nslept 4\n', test.stdout()
    #
    #    test.run([sys.executable, test.workpath('sleep.py'), '8'])
    #    assert test.stderr() == '', test.stderr()
    #    assert test.stdout() == 'sleeping 8\n', test.stdout()



class unlink_TestCase(TestCmdTestCase):
    def test_unlink(self):
        """Test unlink()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        wdir_file1 = os.path.join(test.workdir, 'file1')
        wdir_file2 = os.path.join(test.workdir, 'file2')
        wdir_foo_file3a = os.path.join(test.workdir, 'foo', 'file3a')
        wdir_foo_file3b = os.path.join(test.workdir, 'foo', 'file3b')
        wdir_foo_file4 = os.path.join(test.workdir, 'foo', 'file4')
        wdir_file5 = os.path.join(test.workdir, 'file5')

        with open(wdir_file1, 'w') as f:
            f.write("")
        with open(wdir_file2, 'w') as f:
            f.write("")
        with open(wdir_foo_file3a, 'w') as f:
            f.write("")
        with open(wdir_foo_file3b, 'w') as f:
            f.write("")
        with open(wdir_foo_file4, 'w') as f:
            f.write("")
        with open(wdir_file5, 'w') as f:
            f.write("")

        try:
            contents = test.unlink('no_file')
        except OSError: # expect "No such file or directory"
            pass
        except:
            raise

        test.unlink("file1")
        assert not os.path.exists(wdir_file1)

        test.unlink(wdir_file2)
        assert not os.path.exists(wdir_file2)

        test.unlink(['foo', 'file3a'])
        assert not os.path.exists(wdir_foo_file3a)

        test.unlink(UserList(['foo', 'file3b']))
        assert not os.path.exists(wdir_foo_file3b)

        test.unlink([test.workdir, 'foo', 'file4'])
        assert not os.path.exists(wdir_foo_file4)

        # Make it so we can't unlink file5.
        # For UNIX, remove write permission from the dir and the file.
        # For Windows, open the file.
        os.chmod(test.workdir, 0o500)
        os.chmod(wdir_file5, 0o400)
        with open(wdir_file5, 'r'):
            try:
                try:
                    test.unlink('file5')
                except OSError: # expect "Permission denied"
                    pass
                except:
                    raise
            finally:
                os.chmod(test.workdir, 0o700)
                os.chmod(wdir_file5, 0o600)


class touch_TestCase(TestCmdTestCase):
    def test_touch(self):
        """Test touch()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'sub')

        wdir_file1 = os.path.join(test.workdir, 'file1')
        wdir_sub_file2 = os.path.join(test.workdir, 'sub', 'file2')

        with open(wdir_file1, 'w') as f:
            f.write("")
        with open(wdir_sub_file2, 'w') as f:
            f.write("")

        file1_old_time = os.path.getmtime(wdir_file1)
        file2_old_time = os.path.getmtime(wdir_sub_file2)

        test.sleep()

        test.touch(wdir_file1)

        file1_new_time = os.path.getmtime(wdir_file1)
        assert file1_new_time > file1_old_time

        test.touch('file1', file1_old_time)

        result = os.path.getmtime(wdir_file1)
        # Sub-second granularity of file systems may still vary.
        # On Windows, the two times may be off by a microsecond.
        assert int(result) == int(file1_old_time), (result, file1_old_time)

        test.touch(['sub', 'file2'])

        file2_new_time = os.path.getmtime(wdir_sub_file2)
        assert file2_new_time > file2_old_time



class verbose_TestCase(TestCmdTestCase):
    def test_verbose(self):
        """Test verbose()"""
        test = TestCmd.TestCmd()
        assert test.verbose == 0, 'verbose already initialized?'
        test = TestCmd.TestCmd(verbose = 1)
        assert test.verbose == 1, 'did not initialize verbose'
        test.verbose = 2
        assert test.verbose == 2, 'did not set verbose'



class workdir_TestCase(TestCmdTestCase):
    def test_workdir(self):
        """Test workdir()"""
        run_env = TestCmd.TestCmd(workdir = '')
        os.chdir(run_env.workdir)
        # Everything before this prepared our "source directory."
        # Now do the real test.
        test = TestCmd.TestCmd()
        assert test.workdir is None

        test = TestCmd.TestCmd(workdir = None)
        assert test.workdir is None

        test = TestCmd.TestCmd(workdir = '')
        assert test.workdir is not None
        assert os.path.isdir(test.workdir)

        test = TestCmd.TestCmd(workdir = 'dir')
        assert test.workdir is not None
        assert os.path.isdir(test.workdir)

        no_such_subdir = os.path.join('no', 'such', 'subdir')
        try:
            test = TestCmd.TestCmd(workdir = no_such_subdir)
        except OSError:  # expect "No such file or directory"
            pass
        except:
            raise

        test = TestCmd.TestCmd(workdir = 'foo')
        workdir_foo = test.workdir
        assert workdir_foo is not None

        test.workdir_set('bar')
        workdir_bar = test.workdir
        assert workdir_bar is not None

        try:
            test.workdir_set(no_such_subdir)
        except OSError:
            pass  # expect "No such file or directory"
        except:
            raise
        assert workdir_bar == test.workdir

        assert os.path.isdir(workdir_foo)
        assert os.path.isdir(workdir_bar)



class workdirs_TestCase(TestCmdTestCase):
    def test_workdirs(self):
        """Test workdirs()"""
        test = TestCmd.TestCmd()
        assert test.workdir is None
        test.workdir_set('')
        wdir1 = test.workdir
        test.workdir_set('')
        wdir2 = test.workdir
        assert os.path.isdir(wdir1)
        assert os.path.isdir(wdir2)
        test.cleanup()
        assert not os.path.exists(wdir1)
        assert not os.path.exists(wdir2)



class workpath_TestCase(TestCmdTestCase):
    def test_workpath(self):
        """Test workpath()"""
        test = TestCmd.TestCmd()
        assert test.workdir is None

        test = TestCmd.TestCmd(workdir = '')
        wpath = test.workpath('foo', 'bar')
        assert wpath == os.path.join(test.workdir, 'foo', 'bar')


class readable_TestCase(TestCmdTestCase):
    @unittest.skipIf(sys.platform == 'win32', "Skip permission fiddling on win32")
    def test_readable(self):
        """Test readable()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        test.write('file1', "Test file #1\n")
        test.write(['foo', 'file2'], "Test file #2\n")
        os.symlink('no_such_file', test.workpath('dangling_symlink'))

        test.readable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_readable(test.workdir)
        assert not _is_readable(test.workpath('file1'))
        assert not _is_readable(test.workpath('foo'))
        assert not _is_readable(test.workpath('foo', 'file2'))

        test.readable(test.workdir, 1)
        assert _is_readable(test.workdir)
        assert _is_readable(test.workpath('file1'))
        assert _is_readable(test.workpath('foo'))
        assert _is_readable(test.workpath('foo', 'file2'))

        test.readable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_readable(test.workdir)
        assert not _is_readable(test.workpath('file1'))
        assert not _is_readable(test.workpath('foo'))
        assert not _is_readable(test.workpath('foo', 'file2'))

        test.readable(test.workpath('file1'), 1)
        assert _is_readable(test.workpath('file1'))

        test.readable(test.workpath('file1'), 0)
        assert not _is_readable(test.workpath('file1'))

        test.readable(test.workdir, 1)



class writable_TestCase(TestCmdTestCase):
    @unittest.skipIf(sys.platform == 'win32', "Skip permission fiddling on win32")
    def test_writable(self):
        """Test writable()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        test.write('file1', "Test file #1\n")
        test.write(['foo', 'file2'], "Test file #2\n")
        os.symlink('no_such_file', test.workpath('dangling_symlink'))

        test.writable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_writable(test.workdir)
        assert not _is_writable(test.workpath('file1'))
        assert not _is_writable(test.workpath('foo'))
        assert not _is_writable(test.workpath('foo', 'file2'))

        test.writable(test.workdir, 1)
        assert _is_writable(test.workdir)
        assert _is_writable(test.workpath('file1'))
        assert _is_writable(test.workpath('foo'))
        assert _is_writable(test.workpath('foo', 'file2'))

        test.writable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_writable(test.workdir)
        assert not _is_writable(test.workpath('file1'))
        assert not _is_writable(test.workpath('foo'))
        assert not _is_writable(test.workpath('foo', 'file2'))

        test.writable(test.workpath('file1'), 1)
        assert _is_writable(test.workpath('file1'))

        test.writable(test.workpath('file1'), 0)
        assert not _is_writable(test.workpath('file1'))


class executable_TestCase(TestCmdTestCase):
    @unittest.skipIf(sys.platform == 'win32', "Skip permission fiddling on win32")
    def test_executable(self):
        """Test executable()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        test.write('file1', "Test file #1\n")
        test.write(['foo', 'file2'], "Test file #2\n")
        os.symlink('no_such_file', test.workpath('dangling_symlink'))

        def make_executable(fname):
            st = os.stat(fname)
            os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]|0o100))

        def make_non_executable(fname):
            st = os.stat(fname)
            os.chmod(fname, stat.S_IMODE(st[stat.ST_MODE]&~0o100))

        test.executable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_executable(test.workdir)
        make_executable(test.workdir)
        assert not _is_executable(test.workpath('file1'))
        assert not _is_executable(test.workpath('foo'))
        make_executable(test.workpath('foo'))
        assert not _is_executable(test.workpath('foo', 'file2'))
        make_non_executable(test.workpath('foo'))
        make_non_executable(test.workdir)

        test.executable(test.workdir, 1)
        assert _is_executable(test.workdir)
        assert _is_executable(test.workpath('file1'))
        assert _is_executable(test.workpath('foo'))
        assert _is_executable(test.workpath('foo', 'file2'))

        test.executable(test.workdir, 0)
        # XXX skip these tests if euid == 0?
        assert not _is_executable(test.workdir)
        make_executable(test.workdir)
        assert not _is_executable(test.workpath('file1'))
        assert not _is_executable(test.workpath('foo'))
        make_executable(test.workpath('foo'))
        assert not _is_executable(test.workpath('foo', 'file2'))

        test.executable(test.workpath('file1'), 1)
        assert _is_executable(test.workpath('file1'))

        test.executable(test.workpath('file1'), 0)
        assert not _is_executable(test.workpath('file1'))

        test.executable(test.workdir, 1)



class write_TestCase(TestCmdTestCase):
    def test_write(self):
        """Test write()"""
        test = TestCmd.TestCmd(workdir = '', subdir = 'foo')
        test.write('file1', "Test file #1\n")
        test.write(['foo', 'file2'], "Test file #2\n")
        try:
            test.write(['bar', 'file3'], "Test file #3 (should not get created)\n")
        except IOError:  # expect "No such file or directory"
            pass
        except:
            raise
        test.write(test.workpath('file4'), "Test file #4.\n")
        test.write(test.workpath('foo', 'file5'), "Test file #5.\n")
        try:
            test.write(test.workpath('bar', 'file6'), "Test file #6 (should not get created)\n")
        except IOError:  # expect "No such file or directory"
            pass
        except:
            raise

        try:
            test.write('file7', "Test file #8.\n", mode = 'r')
        except ValueError: # expect "mode must begin with 'w'
            pass
        except:
            raise

        test.write('file8', "Test file #8.\n", mode = 'w')
        test.write('file9', "Test file #9.\r\n", mode = 'wb')

        if os.name != "nt":
            os.chmod(test.workdir, 0o500)
            try:
                test.write('file10', "Test file #10 (should not get created).\n")
            except IOError:  # expect "Permission denied"
                pass
            except:
                raise

        assert os.path.isdir(test.workpath('foo'))
        assert not os.path.exists(test.workpath('bar'))
        assert os.path.isfile(test.workpath('file1'))
        assert os.path.isfile(test.workpath('foo', 'file2'))
        assert not os.path.exists(test.workpath('bar', 'file3'))
        assert os.path.isfile(test.workpath('file4'))
        assert os.path.isfile(test.workpath('foo', 'file5'))
        assert not os.path.exists(test.workpath('bar', 'file6'))
        assert not os.path.exists(test.workpath('file7'))
        assert os.path.isfile(test.workpath('file8'))
        assert os.path.isfile(test.workpath('file9'))
        if os.name != "nt":
            assert not os.path.exists(test.workpath('file10'))

        with open(test.workpath('file8'), 'r') as f:
            res = f.read()
            assert res == "Test file #8.\n", res
        with open(test.workpath('file9'), 'rb') as f:
            res = to_str(f.read())
            assert res == "Test file #9.\r\n", res


class variables_TestCase(TestCmdTestCase):
    def test_variables(self):
        """Test global variables"""
        run_env = TestCmd.TestCmd(workdir = '')

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
        ]

        script = "import TestCmd\n" + \
                 '\n'.join([ "print(TestCmd.%s\n)" % v for v in variables ])
        run_env.run(program=sys.executable, stdin=script)
        stderr = run_env.stderr()
        assert stderr == "", stderr

        script = "from TestCmd import *\n" + \
                 '\n'.join([ "print(%s)" % v for v in variables ])
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
