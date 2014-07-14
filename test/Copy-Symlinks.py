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
Verify that the Copy() Action symlink soft-copy support works.
"""

import os
import stat
import sys
import TestSCons

import SCons.Defaults
SCons.Defaults.DefaultEnvironment( tools = [] )

test = TestSCons.TestSCons()

filelinkToCopy = 'filelinkToCopy'
fileToLink = 'file.in'
fileContents = 'stuff n things\n'
dirToLink = 'dir'
dirlinkToCopy = 'dirlinkToCopy'
treeToLink = 'tree'
treelinkToCopy = 'treelinkToCopy'

try:
    test.symlink( fileToLink, filelinkToCopy )
    test.symlink( dirToLink, dirlinkToCopy )
    test.symlink( treeToLink, treelinkToCopy )
except:
    test.no_result()

test.write( fileToLink, fileContents )
test.subdir( treeToLink )
test.write( os.path.join( treeToLink, fileToLink ), fileContents )

test.write('SConstruct',
"""\
import SCons.Defaults
SCons.Defaults.DefaultEnvironment( tools = [] )

Execute( Copy( 'F1', '%(filelinkToCopy)s', False ) )
Execute( Copy( 'L1', '%(filelinkToCopy)s' ) )
Execute( Copy( 'L2', '%(filelinkToCopy)s', True ) )

Execute( Mkdir( '%(dirToLink)s' ) )
Execute( Copy( 'D1', '%(dirlinkToCopy)s', False ) )
Execute( Copy( 'L3', '%(dirlinkToCopy)s' ) )
Execute( Copy( 'L4', '%(dirlinkToCopy)s', True ) )

Execute( Copy( 'T1', '%(treelinkToCopy)s', False ) )
Execute( Copy( 'L5', '%(treelinkToCopy)s' ) )
Execute( Copy( 'L6', '%(treelinkToCopy)s', True ) )
"""
% locals()
)

test.must_exist( 'SConstruct' )
test.must_exist( fileToLink )
test.must_exist( filelinkToCopy )
test.must_exist( dirlinkToCopy )
test.must_exist( treelinkToCopy )

expect = test.wrap_stdout(
read_str =
'''\
Copy("F1", "%(filelinkToCopy)s")
Copy("L1", "%(filelinkToCopy)s")
Copy("L2", "%(filelinkToCopy)s")
Mkdir("%(dirToLink)s")
Copy("D1", "%(dirlinkToCopy)s")
Copy("L3", "%(dirlinkToCopy)s")
Copy("L4", "%(dirlinkToCopy)s")
Copy("T1", "%(treelinkToCopy)s")
Copy("L5", "%(treelinkToCopy)s")
Copy("L6", "%(treelinkToCopy)s")
''' % locals(),
build_str =
'''\
scons: `.' is up to date.
'''
)

test.run( stdout = expect )

test.must_exist('D1')
test.must_exist('F1')
test.must_exist('L2')
test.must_exist('L3')
test.must_exist('L4')
test.must_exist('L5')
test.must_exist('L6')
test.must_exist('T1')

test.must_match( fileToLink, fileContents )
test.must_match( 'F1', fileContents )
test.must_match( 'L1', fileContents )
test.must_match( 'L2', fileContents )
test.must_match( os.path.join( treeToLink, fileToLink ), fileContents )

test.fail_test( condition=os.path.islink('D1') )
test.fail_test( condition=os.path.islink('F1') )
test.fail_test( condition=os.path.islink('T1') )
test.fail_test( condition=(not os.path.isdir('D1')) )
test.fail_test( condition=(not os.path.isfile('F1')) )
test.fail_test( condition=(not os.path.isdir('T1')) )
test.fail_test( condition=(not os.path.islink('L1')) )
test.fail_test( condition=(not os.path.islink('L2')) )
test.fail_test( condition=(not os.path.islink('L3')) )
test.fail_test( condition=(not os.path.islink('L4')) )
test.fail_test( condition=(not os.path.islink('L5')) )
test.fail_test( condition=(not os.path.islink('L6')) )
test.fail_test( condition=(os.readlink(filelinkToCopy) != os.readlink('L1')) )
test.fail_test( condition=(os.readlink(filelinkToCopy) != os.readlink('L2')) )
test.fail_test( condition=(os.readlink(dirlinkToCopy) != os.readlink('L3')) )
test.fail_test( condition=(os.readlink(dirlinkToCopy) != os.readlink('L4')) )
test.fail_test( condition=(os.readlink(treelinkToCopy) != os.readlink('L5')) )
test.fail_test( condition=(os.readlink(treelinkToCopy) != os.readlink('L6')) )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
