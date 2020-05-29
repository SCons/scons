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

import unittest

import SCons.Errors
import SCons.Node.Python


class ValueTestCase(unittest.TestCase):
    def test_Value(self):
        """Test creating a Value() object
        """
        v1 = SCons.Node.Python.Value('a')
        assert v1.value == 'a', v1.value

        value2 = 'a'
        v2 = SCons.Node.Python.Value(value2)
        assert v2.value == value2, v2.value
        assert v2.value is value2, v2.value

        assert v1 is not v2
        assert v1.value == v2.value

        v3 = SCons.Node.Python.Value('c', 'cb')
        assert v3.built_value == 'cb'

    def test_build(self):
        """Test "building" a Value Node
        """
        class fake_executor:
            def __call__(self, node):
                node.write('faked')

        v1 = SCons.Node.Python.Value('b', 'built')
        v1.executor = fake_executor()
        v1.build()
        assert v1.built_value == 'built', v1.built_value

        v2 = SCons.Node.Python.Value('b')
        v2.executor = fake_executor()
        v2.build()
        assert v2.built_value == 'faked', v2.built_value

        v3 = SCons.Node.Python.Value(b'\x00\x0F', name='name')
        v3.executor = fake_executor()
        v3.build()
        assert v3.name == 'name', v3.name
        assert v3.built_value == 'faked', v3.built_value

    def test_read(self):
        """Test the Value.read() method
        """
        v1 = SCons.Node.Python.Value('a')
        x = v1.read()
        assert x == 'a', x

    def test_write(self):
        """Test the Value.write() method
        """
        v1 = SCons.Node.Python.Value('a')
        assert v1.value == 'a', v1.value
        assert not hasattr(v1, 'built_value')

        v1.write('new')
        assert v1.value == 'a', v1.value
        assert v1.built_value == 'new', v1.built_value

    def test_get_csig(self):
        """Test calculating the content signature of a Value() object
        """
        v1 = SCons.Node.Python.Value('aaa')
        csig = v1.get_csig(None)
        assert csig == 'aaa', csig

        v2 = SCons.Node.Python.Value(7)
        csig = v2.get_csig(None)
        assert csig == '7', csig

        v3 = SCons.Node.Python.Value(None)
        csig = v3.get_csig(None)
        assert csig == 'None', csig





class ValueNodeInfoTestCase(unittest.TestCase):
    def test___init__(self):
        """Test ValueNodeInfo initialization"""
        vvv = SCons.Node.Python.Value('vvv')
        ni = SCons.Node.Python.ValueNodeInfo()


class ValueBuildInfoTestCase(unittest.TestCase):
    def test___init__(self):
        """Test ValueBuildInfo initialization"""
        vvv = SCons.Node.Python.Value('vvv')
        bi = SCons.Node.Python.ValueBuildInfo()


class ValueChildTestCase(unittest.TestCase):
    def test___init__(self):
        """Test support for a Value() being an implicit dependency of a Node"""
        value = SCons.Node.Python.Value('v')
        node = SCons.Node.Node()
        node._func_get_contents = 2  # Pretend to be a Dir.
        node.add_to_implicit([value])
        contents = node.get_contents()
        expected_contents = '%s %s\n' % (value.get_csig(), value.name)
        assert contents == expected_contents


class ValueMemoTestCase(unittest.TestCase):
    def test_memo(self):
        """Test memoization"""
        # First confirm that ValueWithMemo does memoization.
        value1 = SCons.Node.Python.ValueWithMemo('vvv')
        value2 = SCons.Node.Python.ValueWithMemo('vvv')
        assert value1 is value2

        # Next confirm that ValueNodeInfo.str_to_node does memoization using
        # the same cache as ValueWithMemo.
        ni = SCons.Node.Python.ValueNodeInfo()
        value3 = ni.str_to_node('vvv')
        assert value1 is value3

    def test_built_value(self):
        """Confirm that built values are not memoized."""
        v1 = SCons.Node.Python.ValueWithMemo('c', 'ca')
        v2 = SCons.Node.Python.ValueWithMemo('c', 'ca')
        assert v1 is not v2

    def test_non_primitive_values(self):
        """Confirm that non-primitive values are not memoized."""
        d = {'a': 1}
        v1 = SCons.Node.Python.ValueWithMemo(d)
        v2 = SCons.Node.Python.ValueWithMemo(d)
        assert v1 is not v2

        a = [1]
        v3 = SCons.Node.Python.ValueWithMemo(a)
        v4 = SCons.Node.Python.ValueWithMemo(a)
        assert v3 is not v4

    def test_value_set_name(self):
        """ Confirm setting name and caching takes the name into account """

        v1 = SCons.Node.Python.ValueWithMemo(b'\x00\x0F', name='name')
        v2 = SCons.Node.Python.ValueWithMemo(b'\x00\x0F', name='name2')
        v3 = SCons.Node.Python.ValueWithMemo('Jibberish')

        self.assertEqual(v1.name,'name', msg=v1.name)
        self.assertEqual(v2.name,'name2', msg=v2.name)
        self.assertEqual(v3.name,'Jibberish', msg=v3.name)
        self.assertTrue(v1 is not v2, msg="v1 and v2 should be different as they have different names but same values")


if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
