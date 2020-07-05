#!/usr/bin/env python
#
# Searches through the whole source tree and updates
# the generated *.gen/*.mod files in the docs folder, keeping all
# documentation for the tools, builders and functions...
# as well as the entity declarations for them.
# Uses scons-proc.py under the hood...
#
import os
import sys
import subprocess

import SConsDoc

# Directory where all generated files are stored
gen_folder = os.path.join('doc', 'generated')

def argpair(key):
    """ Return the argument pair *.gen,*.mod for the given key. """
    arg = '%s,%s' % (
        os.path.join(gen_folder, '%s.gen' % key),
        os.path.join(gen_folder, '%s.mod' % key),
    )

    return arg

def generate_all():
    """Generate the entity files.

    Scan for XML files in the SCons directory and call scons-proc.py
    to generate the *.gen/*.mod files from it.
    """
    flist = []
    for path, dirs, files in os.walk('SCons'):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    flist.append(fpath)

    if flist:
        # Does the destination folder exist
        try:
            os.makedirs(gen_folder, exist_ok=True)
        except Exception:
            print("Couldn't create destination folder %s! Exiting..." % gen_folder, file=sys.stdout)
            return False

        # Call scons-proc.py
        cp = subprocess.run(
            [
                sys.executable,
                os.path.join('bin', 'scons-proc.py'),
                '-b', argpair('builders'),
                '-f', argpair('functions'),
                '-t', argpair('tools'),
                '-v', argpair('variables'),
            ] + flist,
            shell=False,
        )

        if cp.returncode:
            print("Generation failed", file=sys.stderr)
            return False
    return True
    
    
if __name__ == "__main__":
    if not generate_all():
        sys.exit(1)
