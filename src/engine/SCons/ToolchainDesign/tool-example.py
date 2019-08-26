"""Full example of defining, registering and using a tool and
toolchain.  The purpose of this example is to explore new usage models
and see what's possible and what's missing.

This is "sort of" a SConstruct.  Run it as scons -f <thisfile>
"""

import os, os.path
import Tool
import Toolchain

#########
# Utilities
#########

# These should be included in the base Tool logic or elsewhere in SCons,
# but for the purpose of this example I want to minimize dependencies.
def which(program, lookup_path):
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in lookup_path:
      path = path.strip('"')
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return exe_file
  # else
  return None

###########
# Define a Tool class
###########

class CopyTool(Tool.Tool):
  """A simple Tool to copy a file, with optional line-numbering."""
  def __init__(self, name, number_lines = False, path = None, use_full_path = False):
    super(CopyTool, self).__init__(name, number_lines=number_lines,
                                   path=path, use_full_path=use_full_path)
    if number_lines:
      self.program = 'nl'
    else:
      self.program = 'cat'
    self.number_lines = number_lines
    self.path = path
    self.use_full_path = use_full_path

  def exists(self, path=None):
    # XXX: should this take an Environment to use for hints on where
    # to look?  That would change the whole model, since Tools right
    # now are independent of the env where they're used.
    if not path:
      path = os.environ["PATH"].split(os.pathsep)
    prog = which(self.program, path)
    if prog is None:
      # save error for user to get later
      self.set_exists_error("Can't find %s in path %s"%(self.program, repr(path)))
      return False
    else:
      self._full_path = prog    # full path to prog
      return True

  def generate(self, env):
    if self.use_full_path:
      env['MYCOPY'] = self._full_path
    else:
      env['MYCOPY'] = self.program
    env['MYCOPYCOM'] = '$MYCOPY $MYCOPYARGS $SOURCES > $TARGET'
    bld = Builder(action='$MYCOPYCOM')
    env.Append(BUILDERS = {'MyCopy': bld})

  # XXX: document, test and use these
  def vars_set(self):
    return ['MYCOPY', 'MYCOPYCOM']

  def vars_used(self):
    return []

  def builders_created(self):
    return ['MyCopy', 'MyNumLines']

  @property
  def version(self):
    return 1, 0, 0, "test"

  def __str__(self):
    return "<Copy tool: %s, args=%s>"%(self._name, self._args)

####################
# Register some instances of the tool
####################

Tool.Tool.register('cat', CopyTool)
Tool.Tool.register('number-lines', CopyTool, number_lines=True)
Tool.Tool.register('cat-with-full-path', CopyTool, number_lines=False, use_full_path=True)

####################
# Use the tool (this part is almost like a normal SConstruct)
####################

env=Environment()
env2=Environment()

copy_tool = Tool.Tool.lookup('cat-with-full-path') # creates MyCopy builder
# XXX: have to call exists() before generate for this tool
# (because it sets a needed member var)
# should generate() always call exists() perhaps?
if not copy_tool.exists():
  print "NO COPY TOOL: %s"%copy_tool.exists_error()
copy_tool.generate(env)

nl_tool = Tool.Tool.lookup('number-lines') # creates MyNumLines builder
if not nl_tool.exists():
  print "NO NL TOOL: %s"%nl_tool.exists_error()
nl_tool.generate(env2)

env.MyCopy(target='tgt', source='src.txt')
env.MyCopy(target='tgt-with-tabs', source='src.txt', MYCOPYARGS='-t')
env2.MyCopy(target='tgt2', source='src.txt')
