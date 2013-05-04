#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import os.path
import sys
import glob
import subprocess

__doc__ = """bootstrap.py

Execute SCons from this source tree. It copies Python scripts and modules
from src/ subdirectory into a subdirectory named "bootstrap/" (by default),
and executes SCons from there with the supplied command-line arguments.

This is a minimal build of SCons to bootstrap the full build of all the
packages, as specified in our local SConstruct file.

Some options are specific to this bootstrap.py script and are *not* passed
on to the SCons script. All of these begin with the string "bootstrap_":

    --bootstrap_dir=DIR

        Sets the name of the directory into which the SCons files will
        be copied.  The default is "bootstrap" in the local subdirectory.

    --bootstrap_force

        Forces a copy of all necessary files.  By default, the
        bootstrap.py script only updates the bootstrap copy if the
        content of the source copy is different.

    --bootstrap_src=DIR

        Searches for the SCons files relative to the specified DIR,
        then relative to the directory in which this bootstrap.py
        script is found.

    --bootstrap_update

        Only updates the bootstrap subdirectory, and then exits.

In addition to the above, the bootstrap.py script understands
the following SCons options:

    -C, --directory

        Changes to the specified directory before invoking SCons.
        Because we change directory right away to the specified directory,
        the SCons script itself doesn't need to, so this option gets
        "eaten" by the bootstrap.py script.
"""

def parseManifestLines(basedir, lines):
    """ Scans the single lines of a MANIFEST file,
        and returns the list of source files.
        Has basic support for recursive globs '**',
        filename wildcards of the form '*.xml' and
        comment lines, starting with a '#'.
    """
    sources = []
    oldwd = os.path.abspath(os.getcwd())
    basewd = os.path.abspath(basedir)
    os.chdir(basedir)
    for l in lines:
        if l.startswith('#'):
            # Skip comments
            continue
        l = l.rstrip('\n')
        if l.endswith('**'):
            # Glob all files recursively
            globwd, tail = os.path.split(l)
            if globwd:
                os.chdir(globwd)
            for path, dirs, files in os.walk('.'):
                for f in files:
                    if globwd:
                        fpath = os.path.join(globwd, path, f)
                    else:
                        fpath = os.path.join(path, f)
                    sources.append(os.path.normpath(fpath))
            if globwd:
                os.chdir(basewd)
        elif '*' in l:
            # Glob file pattern
            globwd, tail = os.path.split(l)
            if globwd:
                os.chdir(globwd)
                files = glob.glob(tail)
                for f in files:
                    fpath = os.path.join(globwd, f)
                    sources.append(os.path.normpath(fpath))
                os.chdir(basewd)
            else:
                sources.extend(glob.glob(tail))
        else:
            sources.append(l)
    os.chdir(oldwd)

    return sources

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    
    bootstrap_dir = os.path.join(script_dir, 'bootstrap')
    
    pass_through_args = []
    update_only = None
    
    requires_an_argument = 'bootstrap.py:  %s requires an argument\n'
    
    search = [script_dir]
    
    def find(file, search=search):
        for dir in search:
            f = os.path.join(dir, file)
            if os.path.exists(f):
                return os.path.normpath(f)
        sys.stderr.write("could not find `%s' in search path:\n" % file)
        sys.stderr.write("\t" + "\n\t".join(search) + "\n")
        sys.exit(2)
    
    def must_copy(dst, src):
        if not os.path.exists(dst):
            return 1
        return open(dst, 'rb').read() != open(src, 'rb').read()
    
    # Note:  We don't use the getopt module to process the command-line
    # arguments because we'd have to teach it about all of the SCons options.
    
    command_line_args = sys.argv[1:]
    
    while command_line_args:
        arg = command_line_args.pop(0)
    
        if arg == '--bootstrap_dir':
            try:
                bootstrap_dir = command_line_args.pop(0)
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
        elif arg[:16] == '--bootstrap_dir=':
            bootstrap_dir = arg[16:]
    
        elif arg == '--bootstrap_force':
            def must_copy(dst, src):
                return 1
    
        elif arg == '--bootstrap_src':
            try:
                search.insert(0, command_line_args.pop(0))
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
        elif arg[:16] == '--bootstrap_src=':
            search.insert(0, arg[16:])
    
        elif arg == '--bootstrap_update':
            update_only = 1
    
        elif arg in ('-C', '--directory'):
            try:
                dir = command_line_args.pop(0)
            except IndexError:
                sys.stderr.write(requires_an_argument % arg)
                sys.exit(1)
            else:
                os.chdir(dir)
        elif arg[:2] == '-C':
            os.chdir(arg[2:])
        elif arg[:12] == '--directory=':
            os.chdir(arg[12:])
    
        else:
            pass_through_args.append(arg)
    
    
    scons_py = os.path.join('src', 'script', 'scons.py')
    src_engine = os.path.join('src', 'engine')
    MANIFEST_in = find(os.path.join(src_engine, 'MANIFEST.in'))
    
    files = [ scons_py ] + [os.path.join(src_engine, x)
                            for x in parseManifestLines(src_engine, open(MANIFEST_in).readlines())]
    
    for file in files:
        src = find(file)
        dst = os.path.join(bootstrap_dir, file)
        if must_copy(dst, src):
            dir = os.path.split(dst)[0]
            if not os.path.isdir(dir):
                os.makedirs(dir)
            try: os.unlink(dst)
            except: pass
            open(dst, 'wb').write( open(src, 'rb').read() )
    
    if update_only:
        sys.exit(0)
    
    args = [
                sys.executable,
                os.path.join(bootstrap_dir, scons_py)
           ] + pass_through_args
    
    sys.stdout.write(" ".join(args) + '\n')
    sys.stdout.flush()
    
    os.environ['SCONS_LIB_DIR'] = os.path.join(bootstrap_dir, src_engine)
    
    sys.exit(subprocess.Popen(args, env=os.environ).wait())

if __name__ == "__main__":
    main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
