#! /usr/bin/env python
#
# SCons - a Software Constructor
#
# Copyright (c) 2001, 2002, 2003 Steven Knight
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

__revision__ = "__REVISION__"

__version__ = "__VERSION__"

__build__ = "__BUILD__"

__buildsys__ = "__BUILDSYS__"

__date__ = "__DATE__"

__developer__ = "__DEVELOPER__"

import os
import os.path
import sys
import time

##############################################################################
# BEGIN STANDARD SCons SCRIPT HEADER
#
# This is the cut-and-paste logic so that a self-contained script can
# interoperate correctly with different SCons versions and installation
# locations for the engine.  If you modify anything in this section, you
# should also change other scripts that use this same header.
##############################################################################

# Strip the script directory from sys.path() so on case-insensitive
# (WIN32) systems Python doesn't think that the "scons" script is the
# "SCons" package.  Replace it with our own library directories
# (version-specific first, in case they installed by hand there,
# followed by generic) so we pick up the right version of the build
# engine modules if they're in either directory.

script_dir = sys.path[0]

if script_dir in sys.path:
    sys.path.remove(script_dir)

libs = []

if os.environ.has_key("SCONS_LIB_DIR"):
    libs.append(os.environ["SCONS_LIB_DIR"])

local = 'scons-local-' + __version__
if script_dir:
    local = os.path.join(script_dir, local)
libs.append(local)

scons_version = 'scons-%s' % __version__

prefs = []

if sys.platform == 'win32':
    # sys.prefix is (likely) C:\Python*;
    # check only C:\Python*.
    prefs.append(sys.prefix)
    prefs.append(os.path.join(sys.prefix, 'Lib', 'site-packages'))
else:
    # On other (POSIX) platforms, things are more complicated due to
    # the variety of path names and library locations.  Try to be smart
    # about it.
    if script_dir == 'bin':
        # script_dir is `pwd`/bin;
        # check `pwd`/lib/scons*.
        prefs.append(os.getcwd())
    else:
        if script_dir == '.' or script_dir == '':
            script_dir = os.getcwd()
        head, tail = os.path.split(script_dir)
        if tail == "bin":
            # script_dir is /foo/bin;
            # check /foo/lib/scons*.
            prefs.append(head)

    head, tail = os.path.split(sys.prefix)
    if tail == "usr":
        # sys.prefix is /foo/usr;
        # check /foo/usr/lib/scons* first,
        # then /foo/usr/local/lib/scons*.
        prefs.append(sys.prefix)
        prefs.append(os.path.join(sys.prefix, "local"))
    elif tail == "local":
        h, t = os.path.split(head)
        if t == "usr":
            # sys.prefix is /foo/usr/local;
            # check /foo/usr/local/lib/scons* first,
            # then /foo/usr/lib/scons*.
            prefs.append(sys.prefix)
            prefs.append(head)
        else:
            # sys.prefix is /foo/local;
            # check only /foo/local/lib/scons*.
            prefs.append(sys.prefix)
    else:
        # sys.prefix is /foo (ends in neither /usr or /local);
        # check only /foo/lib/scons*.
        prefs.append(sys.prefix)

    temp = map(lambda x: os.path.join(x, 'lib'), prefs)
    temp.extend(map(lambda x: os.path.join(x, 'lib', 'python%d.%d' % (sys.version_info[0],
                                                                      sys.version_info[1]),
                                           'site-packages'), prefs))
    prefs = temp

# Look first for 'scons-__version__' in all of our preference libs,
# then for 'scons'.
libs.extend(map(lambda x: os.path.join(x, scons_version), prefs))
libs.extend(map(lambda x: os.path.join(x, 'scons'), prefs))

sys.path = libs + sys.path

##############################################################################
# END STANDARD SCons SCRIPT HEADER
##############################################################################

PF_bsig      = 0x1
PF_csig      = 0x2
PF_timestamp = 0x4
PF_implicit  = 0x8
PF_all       = PF_bsig | PF_csig | PF_timestamp | PF_implicit

Do_Func = None
Print_Directories = []
Print_Entries = []
Print_Flags = 0
Verbose = 0
Readable = 0

def field(name, pf, val):
    if Print_Flags & pf:
        if Verbose:
            sep = "\n    " + name + ": "
        else:
            sep = " "
        return sep + str(val)
    else:
        return ""

def printfield(name, entry):
    if Readable and entry.timestamp:
        ts = "'" + time.ctime(entry.timestamp) + "'"
    else:
        ts = entry.timestamp
    timestamp = field("timestamp", PF_timestamp, ts)
    bsig = field("bsig", PF_bsig, entry.bsig)
    csig = field("csig", PF_csig, entry.csig)
    print name + ":" + timestamp + bsig + csig
    if Print_Flags & PF_implicit and entry.implicit:
        if Verbose:
            print "    implicit:"
        for i in entry.implicit:
            print "        %s" % i

def printentries(entries):
    if Print_Entries:
        for name in Print_Entries:
            try:
                entry = entries[name]
            except KeyError:
                sys.stderr.write("sconsign: no entry `%s' in `%s'\n" % (name, args[0]))
            else:
                printfield(name, entry)
    else:
        for name, e in entries.items():
            printfield(name, e)

import SCons.Sig

def Do_SConsignDB(name):
    import anydbm
    import cPickle
    try:
        open(name, 'rb')
    except (IOError, OSError), e:
        sys.stderr.write("sconsign: %s\n" % (e))
        return
    try:
        db = anydbm.open(name, "r")
    except anydbm.error, e:
        sys.stderr.write("sconsign: ignoring invalid .sconsign.dbm file `%s': %s\n" % (name, e))
        return
    if Print_Directories:
        for dir in Print_Directories:
            try:
                val = db[dir]
            except KeyError:
                sys.stderr.write("sconsign: no dir `%s' in `%s'\n" % (dir, args[0]))
            else:
                entries = cPickle.loads(val)
                print '=== ' + dir + ':'
                printentries(entries)
    else:
        keys = db.keys()
        keys.sort()
        for dir in keys:
            entries = cPickle.loads(db[dir])
            print '=== ' + dir + ':'
            printentries(entries)

def Do_SConsignDir(name):
    try:
        fp = open(name, 'rb')
    except (IOError, OSError), e:
        sys.stderr.write("sconsign: %s\n" % (e))
        return
    try:
        sconsign = SCons.Sig.SConsignDir(fp)
    except:
        sys.stderr.write("sconsign: ignoring invalid .sconsign file `%s'\n" % name)
        return
    printentries(sconsign.entries)

Function_Map = {'dbm'      : Do_SConsignDB,
                'sconsign' : Do_SConsignDir}

##############################################################################

import getopt

helpstr = """\
Usage: sconsign [OPTIONS] FILE [...]
Options:
  -b, --bsig                  Print build signature information.
  -c, --csig                  Print content signature information.
  -d DIR, --dir=DIR           Print only info about DIR.
  -e ENTRY, --entry=ENTRY     Print only info about ENTRY.
  -f FORMAT, --format=FORMAT  FILE is in the specified FORMAT.
  -h, --help                  Print this message and exit.
  -i, --implicit              Print implicit dependency information.
  -r, --readable              Print timestamps in human-readable form.
  -t, --timestamp             Print timestamp information.
  -v, --verbose               Verbose, describe each field.
"""

opts, args = getopt.getopt(sys.argv[1:], "bcd:e:f:hirtv",
                            ['bsig', 'csig', 'dir=', 'entry=',
                             'format=', 'help', 'implicit',
                             'readable', 'timestamp', 'verbose'])

for o, a in opts:
    if o in ('-b', '--bsig'):
        Print_Flags = Print_Flags | PF_bsig
    elif o in ('-c', '--csig'):
        Print_Flags = Print_Flags | PF_csig
    elif o in ('-d', '--dir'):
        Print_Directories.append(a)
    elif o in ('-e', '--entry'):
        Print_Entries.append(a)
    elif o in ('-f', '--format'):
        try:
            Do_Func = Function_Map[a]
        except KeyError:
            sys.stderr.write("sconsign: illegal file format `%s'\n" % a)
            print helpstr
            sys.exit(2)
    elif o in ('-h', '--help'):
        print helpstr
        sys.exit(0)
    elif o in ('-i', '--implicit'):
        Print_Flags = Print_Flags | PF_implicit
    elif o in ('-r', '--readable'):
        Readable = 1
    elif o in ('-t', '--timestamp'):
        Print_Flags = Print_Flags | PF_timestamp
    elif o in ('-v', '--verbose'):
        Verbose = 1

if Print_Flags == 0:
    Print_Flags = PF_all
    
for a in args:
    if Do_Func:
        Do_Func(a)
    elif a[-4:] == '.dbm':
        Do_SConsignDB(a)
    else:
        Do_SConsignDir(a)

sys.exit(0)
