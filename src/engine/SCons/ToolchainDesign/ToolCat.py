import Tool

class ToolCat(Tool.Tool):
  """A trivial tool that calls Un*x 'cat' or 'nl' (number lines)
  depending on the number_lines tool arg."""
  def __init__(self, name, number_lines=False, *args, **kwargs):
    super(Tool, self).__init__(name, *args, **kwargs) # maybe need this
    self._number_lines = number_lines
    pass

  def exists(self, use_env):
    # check if 'cat' is found in standard places, or
    # if use_env is True, use user's env vars e.g. $PATH
    # Returns (status, message)
    # message can be set if status is true or false
    return False, "No cat found."

  def generate(self, env):
    # create Builder...
    # add vars
    if self._number_lines:
      env.SetDefault('NL', 'nl') # number lines
    else:
      env.SetDefault('CAT', 'cat') # use full paths when necessary
    env.SetDefault('CAT_ARGS', None)

  @property
  def vars(self):
    """Return list of vars set or used by this tool"""
    return ('CAT', 'NL', 'CAT_ARGS')

  @property
  def version(self):
    return 1, 0, 0

  def __str__(self):
    return "cat tool"
