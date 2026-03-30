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

"""File locking tests.

TODO: Unlocking an unlocked file ("works" - no exception raised)
TODO: Test reader locks
TODO: Create another process to better simulate lock contention
"""

from __future__ import annotations

import os
import unittest
from contextlib import suppress

import TestCmd

from SCons.Util import filelock


class TestFileLock(unittest.TestCase):
    def setUp(self):
        self.test = TestCmd.TestCmd(workdir='')
        self.file = self.test.workpath('test.txt')
        self.lockfile = self.test.workpath('test.txt.lock')
        self.lock = None

    def tearDown(self):
        self.lock.release_lock()
        # in case we made phony lock, clean that up too
        with suppress(FileNotFoundError):
            os.unlink(self.lockfile)

    def _fakelock(self) -> int:
        """Create a fake lockfile to simulate a busy lock."""
        return os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)

    def test_context_manager_lock(self):
        """Test acquiring a file lock, context manager."""
        self.lock = filelock.FileLock(self.file, writer=True)
        self.assertFalse(os.path.exists(self.lockfile))
        with self.lock:
            self.assertTrue(os.path.exists(self.lockfile))
        self.assertFalse(os.path.exists(self.lockfile))

    def test_acquire_release_lock(self):
        """Test acquiring a file lock, method."""
        self.lock = filelock.FileLock(self.file, writer=True)
        self.lock.acquire_lock()
        self.assertTrue(os.path.exists(self.lockfile))
        self.lock.release_lock()
        self.assertFalse(os.path.exists(self.lockfile))

    # Implementation does not raise on release when not holding lock: skip
    # def test_exception_raised_when_lock_not_held(self):
    #     self.lock = filelock.FileLock(self.file, writer=True)
    #     with self.assertRaises(filelock.SConsLockFailure):
    #         self.lock.release_lock()

    def test_nonblocking_lockfail(self):
        """Test non-blocking acquiring a busy file lock."""
        self.lock = filelock.FileLock(self.file, writer=True)
        fd = self._fakelock()
        with self.lock and self.assertRaises(filelock.AlreadyLockedError):
            self.lock.acquire_lock()
        os.close(fd)

    def test_timeout_lockfail(self):
        """Test blocking acquiring a busy file lock with timeout."""
        self.lock = filelock.FileLock(self.file, writer=True, timeout=1)
        fd = self._fakelock()
        with self.lock and self.assertRaises(filelock.LockTimeoutError):
            self.lock.acquire_lock()
        os.close(fd)

if __name__ == "__main__":
    unittest.main()
