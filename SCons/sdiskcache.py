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

"""SConsign support for diskcache. """

import os
from collections.abc import KeysView, ValuesView, ItemsView
import diskcache

DISKCACHE_SUFFIX = '.sqlite'
DEBUG = False


class _Diskcache:
    """Processing of sconsign databases using diskcache.

    Derived from the SCons dblite module, but much simpler, because
    there's no exit processing needed - diskcache keeps a consistent
    sqlite database under the covers.  We don't map prefectly,
    since the dblite implementation leaks through into the model:
    plenty of code expects the in-memory sconsign DB to not
    be backed to disk _except_ on close.

    Most of this is a thin wrapper around a diskcache.Cache,
    which is stored in the _dict attribute - the "in-memory" copy.

    We do want to add a few behaviors: some instances can be
    read-only (e.g. if they are found in a repository we don't update);
    to mirror the dbm/dblite behavior of open flags, "r" and "w"
    expect the DB file to actually exist while "n" means it should
    be emptied (that is, "new"); and we want to make sure there's
    a keys method at least.

    The optional *flag* argument is as for :meth:`dbm.open`.

    +---------+---------------------------------------------------+
    | Value   | Meaning                                           |
    +=========+===================================================+
    | ``'r'`` | Open existing database for reading only (default) |
    +---------+---------------------------------------------------+
    | ``'w'`` | Open existing database for reading and  writing   |
    +---------+---------------------------------------------------+
    | ``'c'`` | Open database for reading and writing, creating   |
    |         | it if it doesn't exist                            |
    +---------+---------------------------------------------------+
    | ``'n'`` | Always create a new, empty database, open for     |
    |         | reading and writing                               |
    +---------+---------------------------------------------------+

    Arguments:
        file_base_name: name of db, will get DISKCACHE_SUFFIX if not present
        flag: opening mode
        mode: UNIX-style mode of DB files (see dbm.open), unused here.
    """

    def __init__(self, file_base_name: str, flag: str = 'r', _: int = 0x000) -> None:
        assert flag in ("r", "w", "c", "n")

        if file_base_name.endswith(DISKCACHE_SUFFIX):
            # There's already a suffix on the file name, don't add one.
            self._dir_name = file_base_name
        else:
            self._dir_name = file_base_name + DISKCACHE_SUFFIX

        if not os.path.isdir(self._dir_name) and flag in ('r', 'w'):
            raise FileNotFoundError(f"No such sconsign database: {self._dir_name}")
        self._dict = diskcache.Cache(self._dir_name)
        self._writable: bool = flag not in ("r",)
        if DEBUG:
            print(
                f"DEBUG: opened a Cache file {self._dir_name} (writable={self._writable})"
            )
        if flag == "n":
            self.clear()

    def check(self, fix=False, retry=False):
        """Call disckache 'check' routine to verify cache."""
        self._dict.check(fix, retry)

    @staticmethod
    def close() -> None:
        """Close the Cache file.

        This exists in the SCons model because other sconsigns are
        plain file backed, here it's a no-op.
        """
        return

    def __getitem__(self, key):
        """Return corresponding value for *key* from cache."""
        return self._dict[key]

    def __setitem__(self, key, value) -> None:
        """Set correspoding *value* for *key* in cache.

        Cache can be in a read-only state, just skip if so.
        TODO: raise error instead?
        """
        if self._writable:
            self._dict[key] = value

    def keys(self):
        return KeysView(self._dict)

    def items(self):
        return ItemsView(self._dict)

    def values(self):
        return ValuesView(self._dict)

    def has_key(self, key) -> bool:
        return key in self._dict

    def __contains__(self, key) -> bool:
        """Return ``True`` if *key* is found in cache."""
        return key in self._dict

    __iter__ = keys

    def __len__(self) -> int:
        """Count of items in cache including expired."""
        return len(self._dict)

    def clear(self):
        """Remove all items from cache."""
        return self._dict.clear()

    def volume(self):
        """Return estimated total size of cache on disk."""
        return self._dict.volume()

    def stats(self):
        """Return cache statistics hits and misses."""
        return self._dict.stats()

    def expire(self, now=None, retry=False):
        """Remove expired items from cache."""
        return self._dict.expire(now, retry)

    def cull(self, retry=False):
        """Cull items from cache until volume is less than size limit."""
        return self._dict.cull(retry)

    def evict(self, tag, retry=False):
        """Remove items with matching *tag* from cache."""
        return self._dict.evict(tag, retry)


def open(  # pylint: disable=redefined-builtin
    file: str, flags: str = "r", mode: int = 0o666
) -> _Diskcache:
    return _Diskcache(file, flags, mode)


def _exercise():
    import tempfile  # pylint: disable=import-outside-toplevel

    with tempfile.TemporaryDirectory() as tmp:
        # reading a nonexistent file with mode 'r' should fail
        try:
            test_cache = open(tmp + "_", "r")
        except FileNotFoundError:
            pass
        else:
            raise RuntimeError("FileNotFoundError exception expected")

        # create mode creates test_cache
        test_cache = open(tmp, "c")
        assert len(test_cache) == 0, len(test_cache)
        test_cache["bar"] = "foo"
        assert test_cache["bar"] == "foo"
        assert len(test_cache) == 1, len(test_cache)
        test_cache.close()

        # new database should be empty
        test_cache = open(tmp, "n")
        assert len(test_cache) == 0, len(test_cache)
        test_cache["foo"] = "bar"
        assert test_cache["foo"] == "bar"
        assert len(test_cache) == 1, len(test_cache)
        test_cache.close()

        # write mode is just normal
        test_cache = open(tmp, "w")
        assert len(test_cache) == 1, len(test_cache)
        assert test_cache["foo"] == "bar"
        test_cache["bar"] = "foo"
        assert len(test_cache) == 2, len(test_cache)
        assert test_cache["bar"] == "foo"
        test_cache.close()

        # read-only database should silently fail to add
        test_cache = open(tmp, "r")
        assert len(test_cache) == 2, len(test_cache)
        assert test_cache["foo"] == "bar"
        assert test_cache["bar"] == "foo"
        test_cache["ping"] = "pong"
        assert len(test_cache) == 2, len(test_cache)
        try:
            test_cache["ping"]
        except KeyError:
            pass
        else:
            raise RuntimeError("KeyError exception expected")
        test_cache.close()

        # test iterators
        test_cache = open(tmp, 'w')
        test_cache["foobar"] = "foobar"
        assert len(test_cache) == 3, len(test_cache)
        expected = {"foo": "bar", "bar": "foo", "foobar": "foobar"}
        assert dict(test_cache) == expected, f"{test_cache} != {expected}"
        key = sorted(test_cache.keys())
        exp = sorted(expected.keys())
        assert key == exp, f"{key} != {exp}"
        key = sorted(test_cache.values())
        exp = sorted(expected.values())
        assert key == exp, f"{key} != {exp}"
        key = sorted(test_cache.items())
        exp = sorted(expected.items())
        assert key == exp, f"{key} != {exp}"
        test_cache.close()

    print("Completed _exercise()")


if __name__ == "__main__":
    _exercise()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
