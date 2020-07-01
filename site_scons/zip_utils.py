import os.path


zcat = 'gzip -d -c'

#
# Figure out if we can handle .zip files.
#
zipit = None
unzipit = None
try:
    import zipfile

    def zipit(env, target, source):
        print("Zipping %s:" % str(target[0]))
        def visit(arg, dirname, filenames):
            for filename in filenames:
                path = os.path.join(dirname, filename)
                if os.path.isfile(path):
                    arg.write(path)
        # default ZipFile compression is ZIP_STORED
        zf = zipfile.ZipFile(str(target[0]), 'w', compression=zipfile.ZIP_DEFLATED)
        olddir = os.getcwd()
        os.chdir(env.Dir(env['CD']).abspath)
        try:
            for dirname, dirnames, filenames in os.walk(env['PSV']):
                visit(zf, dirname, filenames)
        finally:
            os.chdir(olddir)
        zf.close()

    def unzipit(env, target, source):
        print("Unzipping %s:" % str(source[0]))
        zf = zipfile.ZipFile(str(source[0]), 'r')
        for name in zf.namelist():
            dest = os.path.join(env['UNPACK_ZIP_DIR'], name)
            dir = os.path.dirname(dest)
            try:
                os.makedirs(dir)
            except:
                pass
            print(dest,name)
            # if the file exists, then delete it before writing
            # to it so that we don't end up trying to write to a symlink:
            if os.path.isfile(dest) or os.path.islink(dest):
                os.unlink(dest)
            if not os.path.isdir(dest):
                with open(dest, 'wb') as fp:
                    fp.write(zf.read(name))

except ImportError:
    if unzip and zip:
        zipit = "cd $CD && $ZIP $ZIPFLAGS $( ${TARGET.abspath} $) $PSV"
        unzipit = "$UNZIP $UNZIPFLAGS $SOURCES"
