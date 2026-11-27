# MIT License
#
# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

import errno
import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from SCons.Platform import win32


@unittest.skipUnless(sys.platform == "win32", "Windows-specific tests")
class Win32SpawnTestCase(unittest.TestCase):
    """Tests for the win32 spawn functions, which use subprocess directly."""

    def test_spawn_returns_exit_status(self) -> None:
        proc: subprocess.CompletedProcess[bytes] = subprocess.CompletedProcess("cmd", 7)
        with patch.object(win32.subprocess, "run", return_value=proc) as run:
            status = win32.spawn("sh", win32.escape, "mycmd", ["arg"], {})

        self.assertEqual(status, 7)
        run.assert_called_once_with(
            f'sh /C {win32.escape("arg")}', env={}, close_fds=True, check=False
        )

    def test_spawn_reports_creation_error(self) -> None:
        error = FileNotFoundError(
            errno.ENOENT, "The system cannot find the file specified"
        )
        err = io.StringIO()
        with (
            patch.object(win32.subprocess, "run", side_effect=error),
            redirect_stderr(err),
        ):
            status = win32.spawn("sh", win32.escape, "mycmd", ["arg"], {})

        self.assertEqual(status, 127)
        self.assertEqual(
            err.getvalue(),
            "scons: mycmd: The system cannot find the file specified\n",
        )

    def test_spawn_maps_permission_error(self) -> None:
        error = PermissionError(errno.EACCES, "Permission denied")
        with (
            patch.object(win32.subprocess, "run", side_effect=error),
            redirect_stderr(io.StringIO()),
        ):
            status = win32.spawn("sh", win32.escape, "mycmd", ["arg"], {})

        self.assertEqual(status, 126)

    def test_spawn_unknown_errno(self) -> None:
        error = OSError(999, "Something odd happened")
        err = io.StringIO()
        with (
            patch.object(win32.subprocess, "run", side_effect=error),
            redirect_stderr(err),
        ):
            status = win32.spawn("sh", win32.escape, "mycmd", ["arg"], {})

        self.assertEqual(status, 127)
        self.assertEqual(err.getvalue(), "scons: mycmd: Something odd happened\n")

    def test_piped_spawn_captures_output(self) -> None:
        proc = subprocess.CompletedProcess(
            "cmd", 3, stdout=b"hello\r\n", stderr=b"oops\r\n"
        )
        out, err = io.StringIO(), io.StringIO()
        with patch.object(win32.subprocess, "run", return_value=proc) as run:
            status = win32.piped_spawn(
                "sh", win32.escape, "mycmd", ["arg"], {}, out, err
            )

        self.assertEqual(status, 3)
        self.assertEqual(out.getvalue(), "hello\n")
        self.assertEqual(err.getvalue(), "oops\n")
        run.assert_called_once_with(
            f'sh /C {win32.escape("arg")}',
            env={},
            close_fds=True,
            capture_output=True,
            check=False,
        )

    def test_piped_spawn_reports_creation_error_to_stderr_stream(self) -> None:
        error = FileNotFoundError(
            errno.ENOENT, "The system cannot find the file specified"
        )
        out, err = io.StringIO(), io.StringIO()
        proc_err = io.StringIO()
        with (
            patch.object(win32.subprocess, "run", side_effect=error),
            redirect_stderr(proc_err),
        ):
            status = win32.piped_spawn(
                "sh", win32.escape, "mycmd", ["arg"], {}, out, err
            )

        self.assertEqual(status, 127)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(
            err.getvalue(),
            "scons: mycmd: The system cannot find the file specified\n",
        )
        self.assertEqual(proc_err.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
