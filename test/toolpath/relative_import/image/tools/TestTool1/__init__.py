from . import TestTool1_1

def generate(env):
    env['TestTool1'] = 1
    # Include another tool within the same directory
    TestTool1_1.generate(env)
def exists(env):
    TestTool1_1.exists(env)
    return 1
