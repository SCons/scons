from . import TestTool1_2_1
from . import TestTool1_2_2

def generate(env):
    env['TestTool1_2'] = 1
    TestTool1_2_1.generate(env)
    TestTool1_2_2.generate(env)
def exists(env):
    TestTool1_2_1.exists(env)
    TestTool1_2_2.exists(env)
    return 1
