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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test the transition from the old .sconsign format(s).
"""

import os
import os.path
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.subdir('src1', ['src1', 'subdir'],
            'src2', ['src2', 'subdir'])

convert = test.workpath('convert.py')
convert_dblite = test.workpath('convert_dblite.py')

test.write(convert, """\
import cPickle
import sys
import SCons.SConsign
import SCons.Sig

try:
    SConsignEntry = SCons.Sig.SConsignEntry
except AttributeError:
    class SConsignEntry:
        timestamp = None
        bsig = None
        csig = None
        implicit = None

filename = sys.argv[1]

sconsign = SCons.SConsign.Dir(open(filename, 'rb'))

old_entries = {}
for name, entry in sconsign.entries.items():
    oe = SConsignEntry()
    for attr in ['timestamp', 'bsig', 'csig', 'implicit']:
        try: setattr(oe, attr, getattr(entry, attr))
        except AttributeError: pass
    old_entries[name] = oe

cPickle.dump(old_entries, open(filename, 'wb'), 1)
""")

test.write(convert_dblite, """\
import cPickle
import SCons.dblite
import sys
import SCons.SConsign
import SCons.Sig

try:
    SConsignEntry = SCons.Sig.SConsignEntry
except AttributeError:
    class SConsignEntry:
        timestamp = None
        bsig = None
        csig = None
        implicit = None

filename = sys.argv[1]

db = SCons.dblite.open(filename, "r")

old_db = {}
for dir in db.keys():
    #self.printentries(dir, db[dir])

    new_entries = cPickle.loads(db[dir])
    old_db[dir] = old_entries = {}
    for name, entry in new_entries.items():
        oe = SConsignEntry()
        for attr in ['timestamp', 'bsig', 'csig', 'implicit']:
            try: setattr(oe, attr, getattr(entry, attr))
            except AttributeError: pass
        old_entries[name] = oe

db = SCons.dblite.open(filename, "c")
for key, val in old_db.items():
    db[key] = cPickle.dumps(val)
db.sync()
""")



# Now generate a simple .sconsign file for a simple build.
test.write(['src1', 'SConstruct'], """\
SConsignFile(None)
import os
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()

env = Environment()
env.Append(BUILDERS={'Cat':Builder(action=cat)})

Export("env")
SConscript('SConscript')
""")

test.write(['src1', 'SConscript'], """\
Import("env")
env.Cat('file1', 'file1.in')
env.Cat('subdir/file2', 'subdir/file2.in')
""")

test.write(['src1', 'file1.in'], "file1.in 1\n")
test.write(['src1', 'subdir', 'file2.in'], "subdir/file2.in 1\n")

test.run(chdir='src1', arguments='.')

test.up_to_date(chdir='src1', arguments='.')

sconsign_list = [
        test.workpath('src1', '.sconsign'),
        test.workpath('src1', 'subdir', '.sconsign'),
]

for sconsign in sconsign_list:
    test.run(interpreter=python, program=convert, arguments=sconsign)

test.up_to_date(chdir='src1', arguments='.')



# Now do the same with SConsignFile().
test.write(['src2', 'SConstruct'], """\
import os
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()

env = Environment()
env.Append(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('file1', 'file1.in')
env.Cat('subdir/file2', 'subdir/file2.in')
""")

test.write(['src2', 'file1.in'], "file1.in 1\n")
test.write(['src2', 'subdir', 'file2.in'], "subdir/file2.in 1\n")

test.run(chdir='src2', arguments='.')

test.up_to_date(chdir='src2', arguments='.')

sconsign_list = [
        test.workpath('src2', '.sconsign'),
]

for sconsign in sconsign_list:
    test.run(interpreter=python, program=convert_dblite, arguments=sconsign)

test.up_to_date(chdir='src2', arguments='.')



test.pass_test()
