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
import SConsDoc

# Directory where all generated files are stored
gen_folder = os.path.join('doc','generated')

def argpair(key):
    """ Return the argument pair *.gen,*.mod for the given key. """
    arg = '%s,%s' % (os.path.join(gen_folder,'%s.gen' % key),
                     os.path.join(gen_folder,'%s.mod' % key))
    
    return arg

def generate_all():
    """ Scan for XML files in the src directory and call scons-proc.py
        to generate the *.gen/*.mod files from it.
    """
    flist = []
    for path, dirs, files in os.walk('src'):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    flist.append(fpath)

    if flist:
        # Does the destination folder exist
        if not os.path.isdir(gen_folder):
            try:
                os.makedirs(gen_folder)
            except:
                print "Couldn't create destination folder %s! Exiting..." % gen_folder
                return
        # Call scons-proc.py
        os.system('%s %s -b %s -f %s -t %s -v %s %s' %
                  (sys.executable, os.path.join('bin','scons-proc.py'),
                   argpair('builders'), argpair('functions'),
                   argpair('tools'), argpair('variables'), ' '.join(flist)))
    
    
if __name__ == "__main__":
    generate_all()
