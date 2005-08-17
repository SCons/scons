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
Test fetching source files from Perforce.

This test requires that a Perforce server be running on the test system
on port 1666, as well as that of course a client must be present.
"""

import os
import socket
import string

import TestSCons

test = TestSCons.TestSCons()

p4 = test.where_is('p4')
if not p4:
    test.skip_test("Could not find 'p4'; skipping test(s).\n")

user = os.environ.get('USER')
if not user:
    user = os.environ.get('USERNAME')
if not user:
    user = os.environ.get('P4USER')

host = socket.gethostname()

# clean out everything
try:
    test.run(program=p4, arguments='-p 1666 obliterate -y //testme/...')
    test.run(program=p4, arguments='-p 1666 depot -d testme')
except TestSCons.TestFailed:
    pass # it's okay if this fails...it will fail if the depot is clear already.

# Set up a perforce depot for testing.
depotspec = """\
# A Perforce Depot Specification.
Depot:	testme

Owner:	%s

Date:	2003/02/19 17:21:41

Description:
	A test depot.

Type:	local

Address:	subdir

Map:	testme/...
""" % user

test.run(program=p4, arguments='-p 1666 depot -i', stdin = depotspec)

# Now set up 2 clients, one to check in some files, and one to
# do the building.
clientspec = """\
# A Perforce Client Specification.
Client:	%s

Owner:	%s

Host: %s

Description:
	Created by ccrain.

Root:	%s

Options:	noallwrite noclobber nocompress unlocked nomodtime normdir

LineEnd:	local

View:
	%s //%s/...
"""

clientspec1 = clientspec % ("testclient1", user, host, test.workpath('import'),
                            "//testme/foo/...", "testclient1")
clientspec2 = clientspec % ("testclient2", user, host, test.workpath('work'),
                            "//testme/...", "testclient2")

test.subdir('import', ['import', 'sub'], 'work')

test.run(program=p4, arguments = '-p 1666 client -i', stdin=clientspec1)
test.run(program=p4, arguments = '-p 1666 client -i', stdin=clientspec2)

test.write(['import', 'aaa.in'], "import/aaa.in\n")
test.write(['import', 'bbb.in'], "import/bbb.in\n")
test.write(['import', 'ccc.in'], "import/ccc.in\n")

test.write(['import', 'sub', 'SConscript'], """
Import("env")
env.Cat('ddd.out', 'ddd.in')
env.Cat('eee.out', 'eee.in')
env.Cat('fff.out', 'fff.in')
env.Cat('all', ['ddd.out', 'eee.out', 'fff.out'])
""")

test.write(['import', 'sub', 'ddd.in'], "import/sub/ddd.in\n")
test.write(['import', 'sub', 'eee.in'], "import/sub/eee.in\n")
test.write(['import', 'sub', 'fff.in'], "import/sub/fff.in\n")

# Perforce uses the PWD environment variable in preference to the actual cwd
os.environ["PWD"] = test.workpath('import')
paths = [ 'aaa.in', 'bbb.in', 'ccc.in',
          'sub/ddd.in', 'sub/eee.in', 'sub/fff.in', 'sub/SConscript' ]
paths = map(os.path.normpath, paths)
args = '-p 1666 -c testclient1 add -t binary %s' % string.join(paths)
test.run(program=p4, chdir='import', arguments=args)

changespec = """
Change:	new

Client:	testclient1

User:	%s

Status:	new

Description:
	A test check in

Files:
	//testme/foo/aaa.in	# add
	//testme/foo/bbb.in	# add
	//testme/foo/ccc.in	# add
	//testme/foo/sub/SConscript	# add
	//testme/foo/sub/ddd.in	# add
	//testme/foo/sub/eee.in	# add
	//testme/foo/sub/fff.in	# add
""" % user

test.run(program=p4,
         arguments='-p 1666 -c testclient1 submit -i',
         stdin=changespec)

test.write(['work', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)},
                  P4FLAGS='-p 1666 -c testclient2')
env.Cat('aaa.out', 'foo/aaa.in')
env.Cat('bbb.out', 'foo/bbb.in')
env.Cat('ccc.out', 'foo/ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
env.SourceCode('.', env.Perforce())
SConscript('foo/sub/SConscript', 'env')
""")

test.subdir(['work', 'foo'])
test.write(['work', 'foo', 'bbb.in'], "work/foo/bbb.in\n")

test.subdir(['work', 'foo', 'sub'])
test.write(['work', 'foo', 'sub', 'eee.in'], "work/foo/sub/eee.in\n")

test.run(chdir = 'work', arguments = '.')
test.fail_test(test.read(['work', 'all']) != "import/aaa.in\nwork/foo/bbb.in\nimport/ccc.in\n")
test.fail_test(test.read(['work', 'foo', 'sub', 'all']) != "import/sub/ddd.in\nwork/foo/sub/eee.in\nimport/sub/fff.in\n")

test.pass_test()
