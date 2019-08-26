import unittest
import Tool

class MockTool(Tool.Tool):
  def __init__(self, name, *args, **kwargs):
    super(MockTool, self).__init__(name, *args, **kwargs) # maybe need this
    self._name = name
    self._args = args
    self._kwargs = kwargs
    self.generate_called = False
    self.exists_called = False

  def exists(self, use_env=False):
    self.exists_called += 1
    return True

  def generate(self, env):
    self.generate_called += 1

  @property
  def version(self):
    return 1, 0, 0, "test"

  def __str__(self):
    return "<mock tool: %s, args=%s>"%(self._name, self._args)

class NonexistentTool(Tool.Tool):
  def __init__(self, name, *args, **kwargs):
    super(NonexistentTool, self).__init__(name, *args, **kwargs) # maybe need this
    self._name = name
    self._args = args
    self._kwargs = kwargs
    self.generate_called = False
    self.exists_called = False

  def exists(self, use_env=False):
    self.set_exists_error("Tool %s doesn't exist"%self._name)
    return False

class ToolTests(unittest.TestCase):

  def setUp(self):
    Tool.the_registry.clean()

  def test_create(self):
    """Test simple creation.  Also tests name property."""
    t1 = Tool.Tool.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    assert t1
    assert t1._name == 't1'
    assert t1.name == 't1'

  def test_lookup(self):
    t1 = Tool.Tool.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    assert t1 == Tool.Tool.lookup('t1')
    assert None == Tool.Tool.lookup('xyz')

  def test_no_name(self):
    with self.assertRaises(Tool.ToolError):
      t1 = Tool.Tool.register(None, MockTool)
    with self.assertRaises(Tool.ToolError):
      t1 = Tool.Tool.register('', MockTool)

  def test_name_mismatch(self):
    with self.assertRaises(Tool.ToolError):
      t1 = Tool.Tool.register('t1', MockTool)
      t2 = Tool.Tool.register('t2', MockTool)

  def test_generate(self):
    t1 = Tool.Tool.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    assert t1.exists()
    t1.generate(None)
    assert t1.generate_called == 1
    assert t1.exists_called == 1

  def test_generate(self):
    t1 = Tool.Tool.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    assert t1.exists()
    t1.generate(None)
    assert t1.generate_called == 1
    assert t1.exists_called == 1

  def test_nonexistent(self):
    t1 = Tool.Tool.register('non1', NonexistentTool)
    assert not t1.exists()
    assert t1.exists_error() == "Tool non1 doesn't exist"

class RegistryTests(unittest.TestCase):

  def setUp(self):
    self.registry = Tool.the_registry
    self.registry.clean()

  def test_register(self):
    t1 = self.registry.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    assert t1
    assert t1.__class__ == MockTool
    t2 = self.registry.register('t2', MockTool, ('arg2'), kwarg2='kwval2')
    assert t1 != t2
    assert t1 == self.registry.lookup_by_name('t1')

  def test_reregister(self):
    t1 = self.registry.register('t1', MockTool, ('arg1'), kwarg1='kwval1')
    t2 = self.registry.register('t1', MockTool, ('arg1'), kwarg1='kwval1') # again
    assert t1 == t2

  def test_lookup(self):
    t1 = self.registry.register('t1', MockTool)
    assert t1 == self.registry.lookup_by_name('t1')
