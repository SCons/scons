"""SCons.UserTuple

A more or less complete user-defined wrapper around tuple objects.

This is basically cut-and-pasted from UserList, but it wraps an immutable
tuple instead of a mutable list, primarily so that the wrapper object can
be used as the hash of a dictionary.  The time it takes to compute the
hash value of a builtin tuple grows as the length of the tuple grows, but
the time it takes to compute hash value of an object can stay constant.

"""

#
# __COPYRIGHT__
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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

class UserTuple:
    def __init__(self, inittuple=None):
        self.data = ()
        if inittuple is not None:
            # XXX should this accept an arbitrary sequence?
            if type(inittuple) == type(self.data):
                self.data = inittuple[:]
            elif isinstance(inittuple, UserTuple):
                self.data = tuple(inittuple.data[:])
            else:
                self.data = tuple(inittuple)
    def __str__(self): return str(self.data)
    def __lt__(self, other): return self.data <  self.__cast(other)
    def __le__(self, other): return self.data <= self.__cast(other)
    def __eq__(self, other): return self.data == self.__cast(other)
    def __ne__(self, other): return self.data != self.__cast(other)
    def __gt__(self, other): return self.data >  self.__cast(other)
    def __ge__(self, other): return self.data >= self.__cast(other)
    def __cast(self, other):
        if isinstance(other, UserTuple): return other.data
        else: return other
    def __cmp__(self, other):
        return cmp(self.data, self.__cast(other))
    def __contains__(self, item): return item in self.data
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]
    def __setitem__(self, i, item):
        raise TypeError, "object doesn't support item assignment"
    def __delitem__(self, i):
        raise TypeError, "object doesn't support item deletion"
    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        return self.__class__(self.data[i:j])
    def __setslice__(self, i, j, other):
        raise TypeError, "object doesn't support slice assignment"
    def __delslice__(self, i, j):
        raise TypeError, "object doesn't support slice deletion"
    def __add__(self, other):
        if isinstance(other, UserTuple):
            return self.__class__(self.data + other.data)
        elif isinstance(other, type(self.data)):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + tuple(other))
    def __radd__(self, other):
        if isinstance(other, UserTuple):
            return self.__class__(other.data + self.data)
        elif isinstance(other, type(self.data)):
            return self.__class__(other + self.data)
        else:
            return self.__class__(tuple(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __iter__(self):
        return iter(self.data)
    def __hash__(self):
        return hash(self.data)

if (__name__ == "__main__"):
    t = UserTuple((1, 2, 3))
    assert isinstance(t, UserTuple)
    t2 = UserTuple(t)
    assert isinstance(t2, UserTuple)
    t3 = UserTuple([1, 2, 3])
    assert isinstance(t3, UserTuple)
    assert t == t2
    assert t == t3
    assert str(t) == '(1, 2, 3)', str(t)
    assert t < UserTuple((2, 2, 3))
    assert t <= UserTuple((2, 2, 3))
    assert t == UserTuple((1, 2, 3))
    assert t != UserTuple((3, 2, 1))
    assert t > UserTuple((0, 2, 3))
    assert t >= UserTuple((0, 2, 3))
    assert cmp(t, UserTuple((0,))) == 1
    assert cmp(t, UserTuple((1, 2, 3))) == 0
    assert cmp(t, UserTuple((2,))) == -1
    assert t < (2, 2, 3)
    assert t <= (2, 2, 3)
    assert t == (1, 2, 3)
    assert t != (3, 2, 1)
    assert t > (0, 2, 3)
    assert t >= (0, 2, 3)
    assert cmp(t, (0,)) == 1
    assert cmp(t, (1, 2, 3)) == 0
    assert cmp(t, (2,)) == -1
    assert 3 in t
    assert len(t) == 3
    assert t[0] == 1
    assert t[1] == 2
    assert t[2] == 3
    try:
        t[0] = 4
    except TypeError, e:
        assert str(e) == "object doesn't support item assignment"
    else:
        raise "Did not catch expected TypeError"
    try:
        del t[0]
    except TypeError, e:
        assert str(e) == "object doesn't support item deletion"
    else:
        raise "Did not catch expected TypeError"
    assert t[1:2] == (2,)
    try:
        t[0:2] = (4, 5)
    except TypeError, e:
        assert str(e) == "object doesn't support slice assignment", e
    else:
        raise "Did not catch expected TypeError"
    try:
        del t[0:2]
    except TypeError, e:
        assert str(e) == "object doesn't support slice deletion"
    else:
        raise "Did not catch expected TypeError"
    assert t + UserTuple((4, 5)) == (1, 2, 3, 4, 5)
    assert t + (4, 5) == (1, 2, 3, 4, 5)
    assert t + [4, 5] == (1, 2, 3, 4, 5)
    assert UserTuple((-1, 0)) + t == (-1, 0, 1, 2, 3)
    assert (-1, 0) + t == (-1, 0, 1, 2, 3)
    assert [-1, 0] + t == (-1, 0, 1, 2, 3)
    assert t * 2 == (1, 2, 3, 1, 2, 3)
    assert 2 * t == (1, 2, 3, 1, 2, 3)

    t1 = UserTuple((1,))
    t1a = UserTuple((1,))
    t1b = UserTuple((1,))
    t2 = UserTuple((2,))
    t3 = UserTuple((3,))
    d = {}
    d[t1] = 't1'
    d[t2] = 't2'
    d[t3] = 't3'
    assert d[t1] == 't1'
    assert d[t1a] == 't1'
    assert d[t1b] == 't1'
    assert d[t2] == 't2'
    assert d[t3] == 't3'
    d[t1a] = 't1a'
    assert d[t1] == 't1a'
    assert d[t1a] == 't1a'
    assert d[t1b] == 't1a'
    d[t1b] = 't1b'
    assert d[t1] == 't1b'
    assert d[t1a] == 't1b'
    assert d[t1b] == 't1b'
