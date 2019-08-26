import unittest
from Toolchain import Toolchain, AndToolchain, OrToolchain, OptionalElement

class MockTool(object):
  """Mock tool that exists or not based on init arg"""
  def __init__(self, exists):
    self._exists = exists
    self.generate_called = 0
  def exists(self):
    return self._exists
  def generate(self, env):
    self.generate_called += 1
    self.generate_called_with = env
  def __repr__(self):
    return "<MockTool(exists=%s) at %x>"%(self._exists, id(self))


class OptionalElementTests(unittest.TestCase):
  def opt_test(self):
    m1 = MockTool(True)
    oe1 = OptionalElement(m1)
    assert oe1.exists()
    assert Toolchain.is_element_optional(oe1) == (True, m1)

    m2 = MockTool(False)
    oe2 = OptionalElement(m2)
    assert not oe2.exists()
    assert Toolchain.is_element_optional(oe2) == (True, m2)

    m3 = MockTool(False)
    assert Toolchain.is_element_optional(m3) == (False, m3)

class ToolchainTests(unittest.TestCase):

  def setUp(self):
    pass

  def test_basic(self):
    m1 = MockTool(True)
    t = AndToolchain([m1])
    assert t.exists()
    assert t.tool_list() == [m1]

  def test_AND(self):
    m1 = MockTool(True)
    m2 = MockTool(True)
    t = AndToolchain([m1, m2])
    assert t.exists()
    print "TEST: ", repr(t.tool_list())
    assert t.tool_list() == [m1, m2]

  def test_AND_nonexist(self):
    m1 = MockTool(True)
    m2 = MockTool(False)
    t = AndToolchain([m1, m2])
    assert not t.exists()
    assert t.tool_list() == []

  def test_AND_recursive(self):
    m1 = MockTool(True)
    m2 = MockTool(True)
    t = AndToolchain([m1, m2])
    m3 = MockTool(True)
    m4 = MockTool(True)
    t2 = AndToolchain([t, m3, m4])
    assert t2.exists()
    assert t2.tool_list() == [m1, m2, m3, m4]
    t3 = AndToolchain([m3, t, m4])
    assert t3.exists()
    assert t3.tool_list() == [m3, m1, m2, m4]
    t4 = AndToolchain([m3, m4, t])
    assert t4.exists()
    assert t4.tool_list() == [m3, m4, m1, m2]

  def test_OR(self):
    m1 = MockTool(True)
    m2 = MockTool(False)
    t = OrToolchain([m1, m2])
    assert t.exists()
    assert t.tool_list() == [m1]

    t = OrToolchain([m2, m1])
    assert t.exists()
    assert t.tool_list() == [m1]

  def test_OR_of_ANDs(self):
    m1 = MockTool(True)
    m2 = MockTool(True)
    t1 = AndToolchain([m1, m2])
    m3 = MockTool(True)
    m4 = MockTool(True)
    t2 = AndToolchain([m3, m4])
    t3 = OrToolchain([t1, t2])
    assert t3.exists()
    assert t3.tool_list() == [m1, m2]

    # also test that generate() works
    env = 'foo'     # doesn't really matter what this is for this test
    t3.generate(env)
    assert m1.generate_called == 1
    assert m2.generate_called == 1
    assert m3.generate_called == 0
    assert m4.generate_called == 0
    assert m1.generate_called_with == env

  def test_AND_of_ORs(self):
    m1 = MockTool(False)
    m2 = MockTool(True)
    t1 = OrToolchain([m1, m2])
    m3 = MockTool(True)
    m4 = MockTool(False)
    t2 = OrToolchain([m3, m4])
    t3 = AndToolchain([t1, t2])
    assert t3.exists()
    assert t3.tool_list() == [m2, m3]

    # also test that generate() works
    env = 'hi there'
    t3.generate(env)
    assert m1.generate_called == 0
    assert m2.generate_called == 1
    assert m3.generate_called == 1
    assert m4.generate_called == 0
    assert m2.generate_called_with == env

  def test_optional_AND(self):
    m1 = MockTool(True)
    m2 = MockTool(True)
    m3 = MockTool(False)
    t1 = AndToolchain([m1, m2, OptionalElement(m3)])
    assert t1.exists()
    assert t1.tool_list() == [m1, m2]
