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

import glob
import json
import os

# The entire purpose of this script is to rename the files in the specified
# cache directory from the 16 single hex digit directories to 256 2 hex digit
# directories.

# You run this in the cache directory.

expected = ['{:X}'.format(x) for x in range(0, 16)]

if not os.path.exists('config'):    
    # check there are 16 directories, 0 - 9, A - F
    if sorted(glob.glob('*')) != expected:
        raise RuntimeError("This doesn't look like a (version 1) cache directory")
    config = { 'prefix_len' : 1 }
else:
    with open('config') as conf:
        config = json.load(conf)
    if config['prefix_len'] != 1:
        raise RuntimeError("This doesn't look like a (version 1) cache directory")

dirs = set()
for file in glob.iglob(os.path.join('*', '*')):
    name = os.path.basename(file)
    dir = name[:2].upper()
    if dir not in dirs:
        os.mkdir(dir)
        dirs.add(dir)
    os.rename(file, os.path.join(dir, name))

# Now delete the original directories
for dir in expected:
    if os.path.exists(dir):
        os.rmdir(dir)

# and write a config file
config['prefix_len'] = 2
with open('config', 'w') as conf:
    json.dump(config, conf)