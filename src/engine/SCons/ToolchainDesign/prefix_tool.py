# An example of a new-style Tool as a module.

from SCons.Script import *
import Tool

class PrefixTool(Tool.Tool):
  """A simple Tool to copy a file, prepending $PREFIX to each line."""
  def __init__(self, name):
    super(PrefixTool, self).__init__(name)
    self.program = 'sed'

  def exists(self, path=None):
      return True

  def generate(self, env):
    env['PREFIXCMD'] = self.program
    env['PREFIX'] = ''
    env['PREFIXCOM'] = """$PREFIXCMD 's/^/$PREFIX/' < $SOURCE > $TARGET"""
    bld = Builder(action='$PREFIXCOM')
    env.Append(BUILDERS = {'Prefix': bld})

  # XXX: document, test and use these
  def vars_set(self):
    return ['PREFIX', 'PREFIXCMD', 'PREFIXCOM']

  def vars_used(self):
    return []

  def builders_created(self):
    return ['Prefix']

  @property
  def version(self):
    return 1, 0, 0, "test"

  def __str__(self):
    return "<Prefix tool: %s, args=%s>"%(self._name, self._args)

Tool.Tool.register('prefix-tool', PrefixTool)
