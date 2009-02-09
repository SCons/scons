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

import sys
import unittest

import SCons.Memoize



class FakeObject:

    __metaclass__ = SCons.Memoize.Memoized_Metaclass

    memoizer_counters = []

    def __init__(self):
        self._memo = {}

    def _dict_key(self, argument):
        return argument

    memoizer_counters.append(SCons.Memoize.CountDict('dict', _dict_key))

    def dict(self, argument):

        memo_key = argument
        try:
            memo_dict = self._memo['dict']
        except KeyError:
            memo_dict = {}
            self._memo['dict'] = memo_dict
        else:
            try:
                return memo_dict[memo_key]
            except KeyError:
                pass

        result = self.compute_dict(argument)

        memo_dict[memo_key] = result

        return result

    memoizer_counters.append(SCons.Memoize.CountValue('value'))

    def value(self):

        try:
            return self._memo['value']
        except KeyError:
            pass

        result = self.compute_value()

        self._memo['value'] = result

        return result

    def get_memoizer_counter(self, name):
        for mc in self.memoizer_counters:
            if mc.method_name == name:
                return mc
        return  None

class Returner:
    def __init__(self, result):
        self.result = result
        self.calls = 0
    def __call__(self, *args, **kw):
        self.calls = self.calls + 1
        return self.result


class CountDictTestCase(unittest.TestCase):

    def test___call__(self):
        """Calling a Memoized dict method
        """
        obj = FakeObject()

        called = []

        fd1 = Returner(1)
        fd2 = Returner(2)

        obj.compute_dict = fd1

        r = obj.dict(11)
        assert r == 1, r

        obj.compute_dict = fd2

        r = obj.dict(12)
        assert r == 2, r

        r = obj.dict(11)
        assert r == 1, r

        obj.compute_dict = fd1

        r = obj.dict(11)
        assert r == 1, r

        r = obj.dict(12)
        assert r == 2, r

        assert fd1.calls == 1, fd1.calls
        assert fd2.calls == 1, fd2.calls

        c = obj.get_memoizer_counter('dict')

        if SCons.Memoize.use_metaclass:
            assert c.hit == 3, c.hit
            assert c.miss == 2, c.miss
        else:
            assert c.hit == 0, c.hit
            assert c.miss == 0, c.miss


class CountValueTestCase(unittest.TestCase):

    def test___call__(self):
        """Calling a Memoized value method
        """
        obj = FakeObject()

        called = []

        fv1 = Returner(1)
        fv2 = Returner(2)

        obj.compute_value = fv1

        r = obj.value()
        assert r == 1, r
        r = obj.value()
        assert r == 1, r

        obj.compute_value = fv2

        r = obj.value()
        assert r == 1, r
        r = obj.value()
        assert r == 1, r

        assert fv1.calls == 1, fv1.calls
        assert fv2.calls == 0, fv2.calls

        c = obj.get_memoizer_counter('value')

        if SCons.Memoize.use_metaclass:
            assert c.hit == 3, c.hit
            assert c.miss == 1, c.miss
        else:
            assert c.hit == 0, c.hit
            assert c.miss == 0, c.miss


if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [
        CountDictTestCase,
        CountValueTestCase,
    ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
