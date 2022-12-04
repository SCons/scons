DefaultEnvironment(tools=[])
env = Environment(tools=[])

# We name the files 'Tfile' so that they will sort after the SConstruct
# file regardless of whether the test is being run on a case-sensitive
# or case-insensitive system.

env.Command('Tfile.out', 'Tfile.mid', Copy('$TARGET', '$SOURCE'))
env.Command('Tfile.mid', 'Tfile.in', Copy('$TARGET', '$SOURCE'))
