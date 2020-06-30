def update_init_file(env):
    substitutions = {
        '__version__': env['VERSION'],
        "__copyright__": env['COPYRIGHT'],
        "__developer__": env['DEVELOPER'],
        "__date__": env['DATE'],
        "__buildsys__": env['BUILDSYS'],
        "__revision__": env['REVISION'],
        "__build__": env['BUILD'],
    }
    si = env.Textfile('#SCons/__init__.py',
                      ["%s=\"%s\"" % (k, v) for k, v in substitutions.items()] +
                      ['# make sure compatibility is always in place',
                       'import SCons.compat # noqa'],
                      )
    env.Precious(si)
