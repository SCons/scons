# noqa: f821
DefaultEnvironment(tools=[])

env = Environment()
env.Tool('ninja')
env.Program(target='foo', source='foo.c')
