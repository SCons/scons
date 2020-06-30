def update_init_file(env):
    substitutions = {
        '__VERSION__': env['VERSION'],
        "__copyright__": env['COPYRIGHT'],
        "__DEVELOPER__": env['DEVELOPER'],
        "__DATE__": env['DATE'],
        "__BUILDSYS__": env['BUILDSYS'],
        "__REVISION__": env['REVISION'],
        "__BUILD__": env['BUILD'],
    }
    # env.Textfile('#SCons/__versioninfo.py',

    si = env.Textfile('#SCons/__init__.py',
                      ["%s=\"%s\"" % (k, v) for k, v in substitutions.items()] +
                      ['# make sure compatibility is always in place',
                       'import SCons.compat'],
                      )
    env.Precious(si)
