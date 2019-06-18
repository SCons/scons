#! /usr/bin/env python
#
# SCons - a Software Constructor
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

from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"

__build__ = "__BUILD__"

__buildsys__ = "__BUILDSYS__"

__date__ = "__DATE__"

__developer__ = "__DEVELOPER__"

import os
import sys

##############################################################################
# BEGIN STANDARD SCons SCRIPT HEADER
#
# This is the cut-and-paste logic so that a self-contained script can
# interoperate correctly with different SCons versions and installation
# locations for the engine.  If you modify anything in this section, you
# should also change other scripts that use this same header.
##############################################################################

# compatibility check
if (3,0,0) < sys.version_info < (3,5,0) or sys.version_info < (2,7,0):
    msg = "scons: *** SCons version %s does not run under Python version %s.\n\
Python 2.7 or >= 3.5 is required.\n"
    sys.stderr.write(msg % (__version__, sys.version.split()[0]))
    sys.exit(1)

# Strip the script directory from sys.path so on case-insensitive
# (WIN32) systems Python doesn't think that the "scons" script is the
# "SCons" package.
script_dir = os.path.dirname(os.path.realpath(__file__))
script_path = os.path.realpath(os.path.dirname(__file__))
if script_path in sys.path:
    sys.path.remove(script_path)

libs = []

if "SCONS_LIB_DIR" in os.environ:
    libs.append(os.environ["SCONS_LIB_DIR"])

# running from source takes 2nd priority (since 2.3.2), following SCONS_LIB_DIR
source_path = os.path.join(script_path, os.pardir, 'engine')
if os.path.isdir(source_path):
    libs.append(source_path)

# add local-install locations
local_version = 'scons-local-' + __version__
local = 'scons-local'
if script_dir:
    local_version = os.path.join(script_dir, local_version)
    local = os.path.join(script_dir, local)
if os.path.isdir(local_version):
    libs.append(os.path.abspath(local_version))
if os.path.isdir(local):
    libs.append(os.path.abspath(local))

scons_version = 'scons-%s' % __version__

# preferred order of scons lookup paths
prefs = []

# if we can find package information, use it
try:
    import pkg_resources
except ImportError:
    pass
else:
    try:
        d = pkg_resources.get_distribution('scons')
    except pkg_resources.DistributionNotFound:
        pass
    else:
        prefs.append(d.location)

if sys.platform == 'win32':
    # Use only sys.prefix on Windows
    prefs.append(sys.prefix)
    prefs.append(os.path.join(sys.prefix, 'Lib', 'site-packages'))
else:
    # On other (POSIX) platforms, things are more complicated due to
    # the variety of path names and library locations.
    # Build up some possibilities, then transform them into candidates
    temp = []
    if script_dir == 'bin':
        # script_dir is `pwd`/bin;
        # check `pwd`/lib/scons*.
        temp.append(os.getcwd())
    else:
        if script_dir in ('.', ''):
            script_dir = os.getcwd()
        head, tail = os.path.split(script_dir)
        if tail == "bin":
            # script_dir is /foo/bin;
            # check /foo/lib/scons*.
            temp.append(head)

    head, tail = os.path.split(sys.prefix)
    if tail == "usr":
        # sys.prefix is /foo/usr;
        # check /foo/usr/lib/scons* first,
        # then /foo/usr/local/lib/scons*.
        temp.append(sys.prefix)
        temp.append(os.path.join(sys.prefix, "local"))
    elif tail == "local":
        h, t = os.path.split(head)
        if t == "usr":
            # sys.prefix is /foo/usr/local;
            # check /foo/usr/local/lib/scons* first,
            # then /foo/usr/lib/scons*.
            temp.append(sys.prefix)
            temp.append(head)
        else:
            # sys.prefix is /foo/local;
            # check only /foo/local/lib/scons*.
            temp.append(sys.prefix)
    else:
        # sys.prefix is /foo (ends in neither /usr or /local);
        # check only /foo/lib/scons*.
        temp.append(sys.prefix)

    # suffix these to add to our original prefs:
    prefs.extend([os.path.join(x, 'lib') for x in temp])
    prefs.extend([os.path.join(x, 'lib', 'python' + sys.version[:3],
                               'site-packages') for x in temp])


    # Add the parent directory of the current python's library to the
    # preferences.  This picks up differences between, e.g., lib and lib64,
    # and finds the base location in case of a non-copying virtualenv.
    try:
        libpath = os.__file__
    except AttributeError:
        pass
    else:
        # Split /usr/libfoo/python*/os.py to /usr/libfoo/python*.
        libpath, _ = os.path.split(libpath)
        # Split /usr/libfoo/python* to /usr/libfoo
        libpath, tail = os.path.split(libpath)
        # Check /usr/libfoo/scons*.
        prefs.append(libpath)

# Look first for 'scons-__version__' in all of our preference libs,
# then for 'scons'.  Skip paths that do not exist.
libs.extend([os.path.join(x, scons_version) for x in prefs if os.path.isdir(x)])
libs.extend([os.path.join(x, 'scons') for x in prefs if os.path.isdir(x)])

sys.path = libs + sys.path

##############################################################################
# END STANDARD SCons SCRIPT HEADER
##############################################################################

import SCons.compat

try:
    import whichdb

    whichdb = whichdb.whichdb
except ImportError as e:
    from dbm import whichdb

import time
import pickle

import SCons.SConsign


def my_whichdb(filename):
    if filename[-7:] == ".dblite":
        return "SCons.dblite"
    try:
        with open(filename + ".dblite", "rb"):
            return "SCons.dblite"
    except IOError:
        pass
    return _orig_whichdb(filename)


# Should work on python2
_orig_whichdb = whichdb
whichdb = my_whichdb

# was changed for python3
#_orig_whichdb = whichdb.whichdb
#dbm.whichdb = my_whichdb

def my_import(mname):
    import imp

    if '.' in mname:
        i = mname.rfind('.')
        parent = my_import(mname[:i])
        fp, pathname, description = imp.find_module(mname[i+1:],
                                                    parent.__path__)
    else:
        fp, pathname, description = imp.find_module(mname)
    return imp.load_module(mname, fp, pathname, description)


class Flagger(object):
    default_value = 1

    def __setitem__(self, item, value):
        self.__dict__[item] = value
        self.default_value = 0

    def __getitem__(self, item):
        return self.__dict__.get(item, self.default_value)


Do_Call = None
Print_Directories = []
Print_Entries = []
Print_Flags = Flagger()
Verbose = 0
Readable = 0
Warns = 0


def default_mapper(entry, name):
    """
    Stringify an entry that doesn't have an explicit mapping.

    Args:
        entry:  entry
        name: field name

    Returns: str

    """
    try:
        val = eval("entry." + name)
    except AttributeError:
        val = None
    if sys.version_info.major >= 3 and isinstance(val, bytes):
        # This is a dirty hack for py 2/3 compatibility. csig is a bytes object
        # in Python3 while Python2 bytes are str. Hence, we decode the csig to a
        # Python3 string
        val = val.decode()
    return str(val)


def map_action(entry, _):
    """
    Stringify an action entry and signature.

    Args:
        entry: action entry
        second argument is not used

    Returns: str

    """
    try:
        bact = entry.bact
        bactsig = entry.bactsig
    except AttributeError:
        return None
    return '%s [%s]' % (bactsig, bact)


def map_timestamp(entry, _):
    """
    Stringify a timestamp entry.

    Args:
        entry: timestamp entry
        second argument is not used

    Returns: str

    """
    try:
        timestamp = entry.timestamp
    except AttributeError:
        timestamp = None
    if Readable and timestamp:
        return "'" + time.ctime(timestamp) + "'"
    else:
        return str(timestamp)


def map_bkids(entry, _):
    """
    Stringify an implicit entry.

    Args:
        entry:
        second argument is not used

    Returns: str

    """
    try:
        bkids = entry.bsources + entry.bdepends + entry.bimplicit
        bkidsigs = entry.bsourcesigs + entry.bdependsigs + entry.bimplicitsigs
    except AttributeError:
        return None

    if len(bkids) != len(bkidsigs):
        global Warns
        Warns += 1
        # add warning to result rather than direct print so it will line up
        msg = "Warning: missing information, {} ids but {} sigs"
        result = [msg.format(len(bkids), len(bkidsigs))]
    else:
        result = []
    result += [nodeinfo_string(bkid, bkidsig, "        ")
               for bkid, bkidsig in zip(bkids, bkidsigs)]
    if not result:
        return None
    return "\n        ".join(result)


map_field = {
    'action'    : map_action,
    'timestamp' : map_timestamp,
    'bkids'     : map_bkids,
}

map_name = {
    'implicit'  : 'bkids',
}


def field(name, entry, verbose=Verbose):
    if not Print_Flags[name]:
        return None
    fieldname = map_name.get(name, name)
    mapper = map_field.get(fieldname, default_mapper)
    val = mapper(entry, name)
    if verbose:
        val = name + ": " + val
    return val


def nodeinfo_raw(name, ninfo, prefix=""):
    # This just formats the dictionary, which we would normally use str()
    # to do, except that we want the keys sorted for deterministic output.
    d = ninfo.__getstate__()
    try:
        keys = ninfo.field_list + ['_version_id']
    except AttributeError:
        keys = sorted(d.keys())
    l = []
    for k in keys:
        l.append('%s: %s' % (repr(k), repr(d.get(k))))
    if '\n' in name:
        name = repr(name)
    return name + ': {' + ', '.join(l) + '}'


def nodeinfo_cooked(name, ninfo, prefix=""):
    try:
        field_list = ninfo.field_list
    except AttributeError:
        field_list = []
    if '\n' in name:
        name = repr(name)
    outlist = [name + ':'] + [
        f for f in [field(x, ninfo, Verbose) for x in field_list] if f
    ]
    if Verbose:
        sep = '\n    ' + prefix
    else:
        sep = ' '
    return sep.join(outlist)


nodeinfo_string = nodeinfo_cooked


def printfield(name, entry, prefix=""):
    outlist = field("implicit", entry, 0)
    if outlist:
        if Verbose:
            print("    implicit:")
        print("        " + outlist)
    outact = field("action", entry, 0)
    if outact:
        if Verbose:
            print("    action: " + outact)
        else:
            print("        " + outact)


def printentries(entries, location):
    if Print_Entries:
        for name in Print_Entries:
            try:
                entry = entries[name]
            except KeyError:
                err = "sconsign: no entry `%s' in `%s'\n" % (name, location)
                sys.stderr.write(err)
            else:
                try:
                    ninfo = entry.ninfo
                except AttributeError:
                    print(name + ":")
                else:
                    print(nodeinfo_string(name, entry.ninfo))
                printfield(name, entry.binfo)
    else:
        for name in sorted(entries.keys()):
            entry = entries[name]
            try:
                ninfo = entry.ninfo
            except AttributeError:
                print(name + ":")
            else:
                print(nodeinfo_string(name, entry.ninfo))
            printfield(name, entry.binfo)


class Do_SConsignDB(object):
    def __init__(self, dbm_name, dbm):
        self.dbm_name = dbm_name
        self.dbm = dbm

    def __call__(self, fname):
        # The *dbm modules stick their own file suffixes on the names
        # that are passed in.  This causes us to jump through some
        # hoops here.
        try:
            # Try opening the specified file name.  Example:
            #   SPECIFIED                  OPENED BY self.dbm.open()
            #   ---------                  -------------------------
            #   .sconsign               => .sconsign.dblite
            #   .sconsign.dblite        => .sconsign.dblite.dblite
            db = self.dbm.open(fname, "r")
        except (IOError, OSError) as e:
            print_e = e
            try:
                # That didn't work, so try opening the base name,
                # so that if they actually passed in 'sconsign.dblite'
                # (for example), the dbm module will put the suffix back
                # on for us and open it anyway.
                db = self.dbm.open(os.path.splitext(fname)[0], "r")
            except (IOError, OSError):
                # That didn't work either.  See if the file name
                # they specified even exists (independent of the dbm
                # suffix-mangling).
                try:
                    with open(fname, "rb"):
                        pass  # this is a touch only, we don't use it here.
                except (IOError, OSError) as e:
                    # Nope, that file doesn't even exist, so report that
                    # fact back.
                    print_e = e
                sys.stderr.write("sconsign: %s\n" % print_e)
                return
        except KeyboardInterrupt:
            raise
        except pickle.UnpicklingError:
            sys.stderr.write("sconsign: ignoring invalid `%s' file `%s'\n"
                             % (self.dbm_name, fname))
            return
        except Exception as e:
            sys.stderr.write("sconsign: ignoring invalid `%s' file `%s': %s\n"
                             % (self.dbm_name, fname, e))
            exc_type, _, _ = sys.exc_info()
            if exc_type.__name__ == "ValueError" and sys.version_info < (3,0,0):
                sys.stderr.write("Python 2 only supports pickle protocols 0-2.\n")
            return

        if Print_Directories:
            for dir in Print_Directories:
                try:
                    val = db[dir]
                except KeyError:
                    err = "sconsign: no dir `%s' in `%s'\n" % (dir, args[0])
                    sys.stderr.write(err)
                else:
                    self.printentries(dir, val)
        else:
            for dir in sorted(db.keys()):
                self.printentries(dir, db[dir])

    @staticmethod
    def printentries(dir, val):
        try:
            print('=== ' + dir + ':')
        except TypeError:
            print('=== ' + dir.decode() + ':')
        printentries(pickle.loads(val), dir)


def Do_SConsignDir(name):
    try:
        with open(name, 'rb') as fp:
            try:
                sconsign = SCons.SConsign.Dir(fp)
            except KeyboardInterrupt:
                raise
            except pickle.UnpicklingError:
                err = "sconsign: ignoring invalid .sconsign file `%s'\n" % (name)
                sys.stderr.write(err)
                return
            except Exception as e:
                err = "sconsign: ignoring invalid .sconsign file `%s': %s\n" % (name, e)
                sys.stderr.write(err)
                return
            printentries(sconsign.entries, args[0])
    except (IOError, OSError) as e:
        sys.stderr.write("sconsign: %s\n" % e)
        return


##############################################################################

import getopt

helpstr = """\
Usage: sconsign [OPTIONS] [FILE ...]
Options:
  -a, --act, --action         Print build action information.
  -c, --csig                  Print content signature information.
  -d DIR, --dir=DIR           Print only info about DIR.
  -e ENTRY, --entry=ENTRY     Print only info about ENTRY.
  -f FORMAT, --format=FORMAT  FILE is in the specified FORMAT.
  -h, --help                  Print this message and exit.
  -i, --implicit              Print implicit dependency information.
  -r, --readable              Print timestamps in human-readable form.
  --raw                       Print raw Python object representations.
  -s, --size                  Print file sizes.
  -t, --timestamp             Print timestamp information.
  -v, --verbose               Verbose, describe each field.
"""

try:
    opts, args = getopt.getopt(sys.argv[1:], "acd:e:f:hirstv",
                               ['act', 'action',
                                'csig', 'dir=', 'entry=',
                                'format=', 'help', 'implicit',
                                'raw', 'readable',
                                'size', 'timestamp', 'verbose'])
except getopt.GetoptError as err:
    sys.stderr.write(str(err) + '\n')
    print(helpstr)
    sys.exit(2)

for o, a in opts:
    if o in ('-a', '--act', '--action'):
        Print_Flags['action'] = 1
    elif o in ('-c', '--csig'):
        Print_Flags['csig'] = 1
    elif o in ('-d', '--dir'):
        Print_Directories.append(a)
    elif o in ('-e', '--entry'):
        Print_Entries.append(a)
    elif o in ('-f', '--format'):
        # Try to map the given DB format to a known module
        # name, that we can then try to import...
        Module_Map = {'dblite': 'SCons.dblite', 'sconsign': None}
        dbm_name = Module_Map.get(a, a)
        if dbm_name:
            try:
                if dbm_name != "SCons.dblite":
                    dbm = my_import(dbm_name)
                else:
                    import SCons.dblite

                    dbm = SCons.dblite
                    # Ensure that we don't ignore corrupt DB files,
                    # this was handled by calling my_import('SCons.dblite')
                    # again in earlier versions...
                    SCons.dblite.ignore_corrupt_dbfiles = 0
            except ImportError:
                sys.stderr.write("sconsign: illegal file format `%s'\n" % a)
                print(helpstr)
                sys.exit(2)
            Do_Call = Do_SConsignDB(a, dbm)
        else:
            Do_Call = Do_SConsignDir
    elif o in ('-h', '--help'):
        print(helpstr)
        sys.exit(0)
    elif o in ('-i', '--implicit'):
        Print_Flags['implicit'] = 1
    elif o in ('--raw',):
        nodeinfo_string = nodeinfo_raw
    elif o in ('-r', '--readable'):
        Readable = 1
    elif o in ('-s', '--size'):
        Print_Flags['size'] = 1
    elif o in ('-t', '--timestamp'):
        Print_Flags['timestamp'] = 1
    elif o in ('-v', '--verbose'):
        Verbose = 1

if Do_Call:
    for a in args:
        Do_Call(a)
else:
    if not args:
        args = [".sconsign.dblite"]
    for a in args:
        dbm_name = whichdb(a)
        if dbm_name:
            Map_Module = {'SCons.dblite': 'dblite'}
            if dbm_name != "SCons.dblite":
                dbm = my_import(dbm_name)
            else:
                import SCons.dblite

                dbm = SCons.dblite
                # Ensure that we don't ignore corrupt DB files,
                # this was handled by calling my_import('SCons.dblite')
                # again in earlier versions...
                SCons.dblite.ignore_corrupt_dbfiles = 0
            Do_SConsignDB(Map_Module.get(dbm_name, dbm_name), dbm)(a)
        else:
            Do_SConsignDir(a)

    if Warns:
        print("NOTE: there were %d warnings, please check output" % Warns)
sys.exit(0)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
