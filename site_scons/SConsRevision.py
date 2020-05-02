import os

def SCons_revision(target, source, env):
    """Interpolate specific values from the environment into a file.

    This is used to copy files into a tree that gets packaged up
    into the source file package.
    """
    t = str(target[0])
    s = source[0].rstr()

    try:
        with open(s, 'r') as fp:
            contents = fp.read()


        # Note:  We construct the __*__ substitution strings here
        # so that they don't get replaced when this file gets
        # copied into the tree for packaging.
        contents = contents.replace('__BUILD'     + '__', env['BUILD'])
        contents = contents.replace('__BUILDSYS'  + '__', env['BUILDSYS'])
        contents = contents.replace('__COPYRIGHT' + '__', env['COPYRIGHT'])
        contents = contents.replace('__DATE'      + '__', env['DATE'])
        contents = contents.replace('__DEB_DATE'  + '__', env['DEB_DATE'])

        contents = contents.replace('__DEVELOPER' + '__', env['DEVELOPER'])
        contents = contents.replace('__FILE'      + '__', str(source[0]).replace('\\', '/'))
        contents = contents.replace('__MONTH_YEAR'+ '__', env['MONTH_YEAR'])
        contents = contents.replace('__REVISION'  + '__', env['REVISION'])
        contents = contents.replace('__VERSION'   + '__', env['VERSION'])
        contents = contents.replace('__NULL'      + '__', '')
        
        with open(t,'w') as of:
            of.write(contents)
    except UnicodeDecodeError as e:
        print("Error decoding file:%s just copying no revision edit")
        with open(s, 'rb') as fp, open(t, 'wb') as of:
            contents = fp.read()
            of.write(contents)


    os.chmod(t, os.stat(s)[0])