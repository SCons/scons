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
Verify that "ghost" entries in the .sconsign file don't have Nodes
created for them on subsequent runs (which would cause errors
when scanning directories).
"""

import os.path

d_current_txt = os.path.join('d', 'current.txt')

import TestSCons

test = TestSCons.TestSCons()

# This test case is from Morten Elo Petersen.  It's harder because
# blib-case1only actually exists in the build dir after the -c, so the
# Dir scanner finds it and adds it to the dir's entries.
# Unfortunately FS.py's File.exists() method checks it later and finds
# it looks like a stale build copy of a missing source, so it deletes
# it.  And then it's later discovered to be missing since it's still
# in the dir's entries list.  The fix for this is to test for missing
# source files in the dir scanner (Scanner/Dir.py), and delete them
# (just like File.exists() does if they're found in the build dir
# rather than making entries for them.

test.write('SConstruct', """\
def cat(target, source, env):
    with open(str(target[0]), 'wb') as fp:
        for s in source:
            with open(str(s), 'rb') as infp:
                fp.write(infp.read())
env=Environment()
Export('env')
env['BUILDERS']['Cat']=Builder(action=cat, multi=1)
SConscript('src/SConscript',variant_dir='build')
""")

test.subdir('src')
test.write(['src', 'SConscript'], """\
Import('env')
if ARGUMENTS['case']=='1':
    A=env.Cat('#build/lib/blib-case1only','src.txt')
    B=env.Cat('#build/lib/blibB','#build/lib/blib-case1only')
if ARGUMENTS['case']=='2':
    A=env.Cat('case2only','src.txt')
    B=env.Cat('#build/lib/blibB.txt','case2only')
env.Alias('go','#build/lib')
""")

test.write(['src', 'src.txt'], "anything")

test.run(arguments="-Q go case=1")
test.must_exist('build/lib/blib-case1only')
test.run(arguments="-Q go case=2")
test.run(arguments="-Q go case=2 -c")
test.run(arguments="-Q go case=2")


#############################################################################
# This test case is from Jason Orendorff.
# Checking for existence before making nodes for things found in the
# .sconsign fixes this one.

test.write('SConstruct', """\
Command("d/current.txt", [], [Touch("$TARGET")])
if 'pass' in ARGUMENTS and ARGUMENTS['pass'] == '1':
  Command("d/obsolete.txt", [], [Touch("$TARGET")])
Command("installer.exe", ['d'], [Touch("$TARGET")])
""")

test.run(arguments='-Q pass=1')

# Now delete the created files
test.unlink(['d', 'obsolete.txt'])
test.unlink(['d', 'current.txt'])
test.rmdir(['d'])

# Run again, as pass 2
expect = """Touch("%(d_current_txt)s")
Touch("installer.exe")
""" % locals()

test.run(arguments='-Q pass=2', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
