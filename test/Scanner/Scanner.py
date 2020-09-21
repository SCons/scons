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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            with open(file, 'r') as f:
                process(f, outfp)
        elif line[:8] == 'getfile ':
            outfp.write('include ')
            outfp.write(line[8:])
            # note: converted, but not acted upon
        else:
            outfp.write(line)

with open(sys.argv[1], 'r') as ifp, open(sys.argv[2], 'w') as ofp:
    process(ifp, ofp)

sys.exit(0)
""", mode='w')

# Execute a subsidiary SConscript just to make sure we can
# get at the Scanner keyword from there.

test.write('SConstruct', """
SConscript('SConscript')
""", mode='w')

test.write('SConscript', r"""
import re

include_re = re.compile(r'^include\s+(\S+)\s*$', re.M)

def kfile_scan(node, env, scanpaths, arg):
    contents = node.get_text_contents()
    includes = include_re.findall(contents)
    return includes

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'])

env = Environment(K2SCAN=kfile_scan)

k2scan = env.Scanner(name = 'k2',
                     # We'd like to do the following, but it will take
                     # some major surgery to subst() and subst_list(),
                     # so comment it out for now.
                     # function = '$K2SCAN',
                     function = kfile_scan,
                     argument = None,
                     skeys = ['.k2'])

##########################################################
# Test scanner as found automatically from the environment
# (backup_source_scanner)

env = Environment()
env.Append(SCANNERS = kscan)

env.Command('foo', 'foo.k', r'%(_python_)s build.py $SOURCES $TARGET')

##########################################################
# Test resetting the environment scanners (and specifying as a list).

env2 = env.Clone()
env2.Append(SCANNERS = [k2scan])
env2.Command('junk', 'junk.k2', r'%(_python_)s build.py $SOURCES $TARGET')

##########################################################
# Test specifying a specific source scanner for a target Node

barbld = Builder(action=r'%(_python_)s build.py $SOURCES  $TARGET',
                     source_scanner=kscan)
env.Append(BUILDERS={'BarBld':barbld})
bar = env.BarBld(target='bar', source='bar.in')

##########################################################
# Test specifying a source scanner for a Builder that gets
# automatically applied to targets generated from that Builder

def third(env, target, source):
    contents = source[0].get_contents()
    # print("TYPE:"+str(type(contents)))
    contents = contents.replace(b'getfile', b'MISSEDME')
    with open(str(target[0]), 'wb') as f:
        f.write(contents)

kbld = Builder(action=r'%(_python_)s build.py $SOURCES $TARGET',
               src_suffix='.first',
               suffix='.second',
               source_scanner=kscan)
thirdbld = Builder(action=third,
                   src_suffix='.second',
                   suffix='.third')

env.Append(BUILDERS={'Second':thirdbld, 'KB':kbld})

blork = env.KB('moo.first')
ork = env.Second(blork)
Alias('make_ork', ork)

""" % locals(),mode='w')

test.write('foo.k',
"""foo.k 1 line 1
include xxx
include yyy
foo.k 1 line 4
""", mode='w')

test.write('bar.in',
"""include yyy
bar.in 1 line 2
bar.in 1 line 3
include zzz
""", mode='w')

test.write('junk.k2',
"""include yyy
junk.k2 1 line 2
junk.k2 1 line 3
include zzz
""", mode='w')

test.write('moo.first',
"""include xxx
moo.first 1 line 2
include yyy
moo.first 1 line 4
include moo.inc
""", mode='w')

test.write('moo.inc',
"""getfile zzz
""", mode='w')

test.write('xxx', "xxx 1\n",mode='w')
test.write('yyy', "yyy 1\n",mode='w')
test.write('zzz', "zzz 1\n",mode='w')

expect = test.wrap_stdout("""\
%(_python_)s build.py bar.in bar
%(_python_)s build.py foo.k foo
%(_python_)s build.py junk.k2 junk
%(_python_)s build.py moo.first moo.second
third(["moo.third"], ["moo.second"])
""" % locals())

test.run(arguments = '.', stdout=expect)

test.must_match('foo', "foo.k 1 line 1\nxxx 1\nyyy 1\nfoo.k 1 line 4\n", mode='r')
test.must_match('bar', "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n", mode='r')
test.must_match('junk', "yyy 1\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n", mode='r')
test.must_match('moo.third', "xxx 1\nmoo.first 1 line 2\nyyy 1\nmoo.first 1 line 4\ninclude zzz\n", mode='r')

test.up_to_date(arguments = '.')

test.write('xxx', "xxx 2\n",mode='w')

expect = test.wrap_stdout("""\
%(_python_)s build.py foo.k foo
%(_python_)s build.py moo.first moo.second
third(["moo.third"], ["moo.second"])
""" % locals())

test.run(arguments = '.', stdout=expect)

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 1\nfoo.k 1 line 4\n", mode='r')
test.must_match('bar', "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n", mode='r')
test.must_match('junk', "yyy 1\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n", mode='r')
test.must_match('moo.third', "xxx 2\nmoo.first 1 line 2\nyyy 1\nmoo.first 1 line 4\ninclude zzz\n", mode='r')

test.write('yyy', "yyy 2\n",mode='w')

expect = test.wrap_stdout("""\
%(_python_)s build.py bar.in bar
%(_python_)s build.py foo.k foo
%(_python_)s build.py junk.k2 junk
%(_python_)s build.py moo.first moo.second
third(["moo.third"], ["moo.second"])
""" % locals())

test.run(arguments = '.', stdout=expect)

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n", mode='r')
test.must_match('bar', "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n", mode='r')
test.must_match('junk', "yyy 2\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n", mode='r')
test.must_match('moo.third', "xxx 2\nmoo.first 1 line 2\nyyy 2\nmoo.first 1 line 4\ninclude zzz\n", mode='r')

test.write('zzz', "zzz 2\n")

expect = test.wrap_stdout("""\
%(_python_)s build.py bar.in bar
%(_python_)s build.py junk.k2 junk
""" % locals())

test.run(arguments = '.', stdout=expect)

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n", mode='r')
test.must_match('bar', "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 2\n", mode='r')
test.must_match('junk', "yyy 2\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 2\n", mode='r')
test.must_match('moo.third', "xxx 2\nmoo.first 1 line 2\nyyy 2\nmoo.first 1 line 4\ninclude zzz\n", mode='r')

test.up_to_date(arguments = 'foo')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
