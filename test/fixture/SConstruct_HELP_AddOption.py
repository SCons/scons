
AddOption(
    '--debugging',
    dest='debugging',
    action='store_true',
    default=False,
    metavar='BDEBUGGING',
    help='Compile with debugging symbols',
)

vars = Variables()
vars.Add(ListVariable('buildmod', 'List of modules to build', 'none', ['python']))
DefaultEnvironment(tools=[])
env = Environment()

if ARGUMENTS.get('NO_APPEND',False):
    Help(vars.GenerateHelpText(env), append=False)
elif ARGUMENTS.get('LOCAL_ONLY',False):
    Help(vars.GenerateHelpText(env), append=True, local_only=True)
else:
    Help(vars.GenerateHelpText(env), append=True)

