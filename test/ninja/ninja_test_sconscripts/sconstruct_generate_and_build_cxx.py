# noqa: f821

DefaultEnvironment(tools=[])
env = Environment()
env.Tool('ninja')
env.Program(target = 'test2', source = 'test2.cpp')
