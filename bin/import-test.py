#!/usr/bin/env python
#
# __COPYRIGHT__
#
# tree2test.py - turn a directory tree into TestSCons code
#
# A quick script for importing directory hierarchies containing test
# cases that people supply (typically in a .zip or .tar.gz file) into a
# TestSCons.py script.  No error checking or options yet, it just walks
# the first command-line argument (assumed to be the directory containing
# the test case) and spits out code looking like the following:
#
#       test.subdir(['sub1'],
#                   ['sub1', 'sub2'])
#
#       test.write(['sub1', 'file1'], """\
#       contents of file1
#       """)
#
#       test.write(['sub1', 'sub2', 'file2'], """\
#       contents of file2
#       """)
#
# There's no massaging of contents, so any files that themselves contain
# """ triple-quotes will need to have their contents edited by hand.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import sys

directory = sys.argv[1]

Top = None
TopPath = None

class Dir:
    def __init__(self, path):
        self.path = path
        self.entries = {}
    def call_for_each_entry(self, func):
        for name in sorted(self.entries.keys()):
            func(name, self.entries[name])

def lookup(dirname):
    global Top, TopPath
    if not Top:
        Top = Dir([])
        TopPath = dirname + os.sep
        return Top
    dirname = dirname.replace(TopPath, '')
    dirs = dirname.split(os.sep)
    t = Top
    for d in dirs[:-1]:
        t = t.entries[d]
    node = t.entries[dirs[-1]] = Dir(dirs)
    return node

def collect_dirs(l, dir):
    if dir.path:
        l.append(dir.path)
    def recurse(n, d):
        if d:
            collect_dirs(l, d)
    dir.call_for_each_entry(recurse)

def print_files(dir):
    def print_a_file(n, d):
        if not d:
            l = dir.path + [n]
            sys.stdout.write('\ntest.write(%s, """\\\n' % l)
            p = os.path.join(directory, *l)
            sys.stdout.write(open(p, 'r').read())
            sys.stdout.write('""")\n')
    dir.call_for_each_entry(print_a_file)

    def recurse(n, d):
        if d:
            print_files(d)
    dir.call_for_each_entry(recurse)

for dirpath, dirnames, filenames in os.walk(directory):
    dir = lookup(dirpath)
    for f in filenames:
        dir.entries[f] = None

subdir_list = []
collect_dirs(subdir_list, Top)
subdir_list = [ str(l) for l in subdir_list ]
sys.stdout.write('test.subdir(' + ',\n            '.join(subdir_list) + ')\n')

print_files(Top)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
