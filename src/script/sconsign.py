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

    prefs = map(lambda x: os.path.join(x, 'lib'), prefs)

# Look first for 'scons-__version__' in all of our preference libs,
# then for 'scons'.
libs.extend(map(lambda x: os.path.join(x, scons_version), prefs))
libs.extend(map(lambda x: os.path.join(x, 'scons'), prefs))

sys.path = libs + sys.path

##############################################################################
# END STANDARD SCons SCRIPT HEADER
##############################################################################

import getopt

helpstr = """\
Usage: sconsign [OPTIONS] FILE [...]
Options:
  -b, --bsig                  Print build signature information.
  -c, --csig                  Print content signature information.
  -e, --entry ENTRY           Print only info about ENTRY.
  -h, --help                  Print this message and exit.
  -i, --implicit              Print implicit dependency information.
  -t, --timestamp             Print timestamp information.
  -v, --verbose               Verbose, describe each field.
"""

opts, args = getopt.getopt(sys.argv[1:], "bce:hitv",
                            ['bsig', 'csig', 'entry=', 'help', 'implicit',
                             'timestamp', 'verbose'])

pf_bsig      = 0x1
pf_csig      = 0x2
pf_timestamp = 0x4
pf_implicit  = 0x8
pf_all       = pf_bsig | pf_csig | pf_timestamp | pf_implicit

entries = []
printflags = 0
verbose = 0

for o, a in opts:
    if o in ('-b', '--bsig'):
        printflags = printflags | pf_bsig
    elif o in ('-c', '--csig'):
        printflags = printflags | pf_csig
    elif o in ('-e', '--entry'):
        entries.append(a)
    elif o in ('-h', o == '--help'):
        print helpstr
        sys.exit(0)
    elif o in ('-i', '--implicit'):
        printflags = printflags | pf_implicit
    elif o in ('-t', '--timestamp'):
        printflags = printflags | pf_timestamp
    elif o in ('-v', '--verbose'):
        verbose = 1

if printflags == 0:
    printflags = pf_all

def field(name, pf, val):
    if printflags & pf:
        if verbose:
            sep = "\n    " + name + ": "
        else:
            sep = " "
        return sep + (val or '-')
    else:
        return ""

def printfield(name, entry):
    timestamp = field("timestamp", pf_timestamp, entry.timestamp)
    bsig = field("bsig", pf_bsig, entry.bsig)
    csig = field("csig", pf_csig, entry.csig)
    print name + ":" + timestamp + bsig + csig
    if printflags & pf_implicit and entry.implicit:
        if verbose:
            print "    implicit:"
        for i in entry.implicit:
            print "        %s" % i

import SCons.Sig

def do_sconsign(fp):
    sconsign = SCons.Sig._SConsign(fp)
    if entries:
        for name in entries:
            try:
                entry = sconsign.entries[name]
            except KeyError:
                sys.stderr.write("sconsign: no entry `%s' in `%s'\n" % (name, args[0]))
            else:
                printfield(name, entry)
    else:
        for name, e in sconsign.entries.items():
            printfield(name, e)
    
    
for a in args:
    do_sconsign(open(a, 'rb'))
