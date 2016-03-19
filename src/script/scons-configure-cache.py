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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"

__build__ = "__BUILD__"

__buildsys__ = "__BUILDSYS__"

__date__ = "__DATE__"

__developer__ = "__DEVELOPER__"

import argparse
import glob
import json
import os

def rearrange_cache_entries(current_prefix_len, new_prefix_len):
    print 'Changing prefix length from', current_prefix_len, 'to', new_prefix_len
    dirs = set()
    old_dirs = set()
    for file in glob.iglob(os.path.join('*', '*')):
        name = os.path.basename(file)
        dir = name[:current_prefix_len].upper()
        if dir not in old_dirs:
            print 'Migrating', dir
            old_dirs.add(dir)
        dir = name[:new_prefix_len].upper()
        if dir not in dirs:
            os.mkdir(dir)
            dirs.add(dir)
        os.rename(file, os.path.join(dir, name))

    # Now delete the original directories
    for dir in old_dirs:
        os.rmdir(dir)

parser = argparse.ArgumentParser(
    description = 'Modify the configuration of an scons cache directory',
    epilog = '''
             Unless you specify an option, it will not be changed (if it is
             already set in the cache config), or changed to an appropriate
             default (it it is not set).
             '''
    )

parser.add_argument('cache-dir', help='Path to scons cache directory')
parser.add_argument('--prefix-len', 
                    help='Length of cache file name used as subdirectory prefix',
                    metavar = '<number>',
                    type=int)
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

# Get the command line as a dict without any of the unspecified entries.
args = dict(filter(lambda x: x[1], vars(parser.parse_args()).items()))

# It seems somewhat strange to me, but positional arguments don't get the -
# in the name changed to _, whereas optional arguments do...
os.chdir(args['cache-dir'])
del args['cache-dir']

# If a value isn't currently configured, this contains the way it behaves
# currently (implied), and the way it should behave afer running this script
# (default)
# FIXME: I should use this to construct the parameter list and supply an
# upgrade function
implicit = {
    'prefix_len' : { 'implied' : 1, 'default' : 2 }
}

if not os.path.exists('config'):
    # Validate the only files in the directory are directories 0-9, a-f
    expected = [ '{:X}'.format(x) for x in range(0, 16) ]
    if not set(os.listdir('.')).issubset(expected):
        raise RuntimeError("This doesn't look like a version 1 cache directory")
    config = dict()
else:
    with open('config') as conf:
        config = json.load(conf)

# Find any keys that aren't currently set but should be
for key in implicit:
    if key not in config:
        config[key] = implicit[key]['implied']
        if key not in args:
            args[key] = implicit[key]['default']

#Now we go through each entry in args to see if it changes an existing config
#setting.
for key in args:
    if args[key] != config[key]:        
        if key == 'prefix_len':
            rearrange_cache_entries(config[key], args[key])
        config[key] = args[key]

# and write the updated config file
with open('config', 'w') as conf:
    json.dump(config, conf)