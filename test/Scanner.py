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

import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('build.py', r"""
import sys
input = open(sys.argv[1], 'rb')
output = open(sys.argv[2], 'wb')

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            process(open(file, 'rb'), outfp)
        elif line[:8] == 'getfile ':
            outfp.write('include ')
            outfp.write(line[8:])
            # note: converted, but not acted upon
        else:
            outfp.write(line)

process(input, output)

sys.exit(0)
""")

# Execute a subsidiary SConscript just to make sure we can
# get at the Scanner keyword from there.

test.write('SConstruct', """
SConscript('SConscript')
""")

test.write('SConscript', """
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def kfile_scan(node, env, scanpaths, arg):
    contents = node.get_contents()
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

env = Environment()
env.Append(SCANNERS = kscan)

env.Command('foo', 'foo.k', r'%(python)s build.py $SOURCES $TARGET')

##########################################################
# Test resetting the environment scanners (and specifying as a list).

env2 = env.Copy()
env2.Append(SCANNERS = [k2scan])
env2.Command('junk', 'junk.k2', r'%(python)s build.py $SOURCES $TARGET')

##########################################################
# Test specifying a specific source scanner for a Builder

bar = env.Command('bar', 'bar.in',
                  r'%(python)s build.py $SOURCES  $TARGET',
                  source_scanner=kscan)

##########################################################
# Test specifying a source scanner for an intermediary Builder to
# ensure that the right scanner gets used for the right nodes.

import string

def blork(env, target, source):
    open(str(target[0]), 'wb').write(
        string.replace(source[0].get_contents(), 'getfile', 'MISSEDME'))

kbld = Builder(action=r'%(python)s build.py $SOURCES $TARGET',
               src_suffix='.lork',
               suffix='.blork',
               source_scanner=kscan)
blorkbld = Builder(action=blork,
                   src_suffix='.blork',
                   suffix='.ork')

env.Append(BUILDERS={'BLORK':blorkbld, 'KB':kbld})

blork = env.KB('moo.lork')
ork = env.BLORK(blork)
Alias('make_ork', ork)

""" % {'python': python})

test.write('foo.k', 
"""foo.k 1 line 1
include xxx
include yyy
foo.k 1 line 4
""")

test.write('bar.in', 
"""include yyy
bar.in 1 line 2
bar.in 1 line 3
include zzz
""")

test.write('junk.k2', 
"""include yyy
junk.k2 1 line 2
junk.k2 1 line 3
include zzz
""")

test.write('moo.lork',
"""include xxx
moo.lork 1 line 2
include yyy
moo.lork 1 line 4
include moo.inc
""")

test.write('moo.inc',
"""getfile zzz
""")

test.write('xxx', "xxx 1\n")
test.write('yyy', "yyy 1\n")
test.write('zzz', "zzz 1\n")

test.run(arguments = '.',
         stdout=test.wrap_stdout("""\
%(python)s build.py bar.in bar
%(python)s build.py foo.k foo
%(python)s build.py junk.k2 junk
%(python)s build.py moo.lork moo.blork
blork(["moo.ork"], ["moo.blork"])
""" % {'python':python}))

test.must_match('foo', "foo.k 1 line 1\nxxx 1\nyyy 1\nfoo.k 1 line 4\n")
test.must_match('bar', "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")
test.must_match('junk', "yyy 1\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n")
test.must_match('moo.ork', "xxx 1\nmoo.lork 1 line 2\nyyy 1\nmoo.lork 1 line 4\ninclude zzz\n")

test.up_to_date(arguments = '.')

test.write('xxx', "xxx 2\n")

test.run(arguments = '.',
         stdout=test.wrap_stdout("""\
%(python)s build.py foo.k foo
%(python)s build.py moo.lork moo.blork
blork(["moo.ork"], ["moo.blork"])
""" % {'python':python}))

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 1\nfoo.k 1 line 4\n")
test.must_match('bar', "yyy 1\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")
test.must_match('junk', "yyy 1\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n")
test.must_match('moo.ork', "xxx 2\nmoo.lork 1 line 2\nyyy 1\nmoo.lork 1 line 4\ninclude zzz\n")

test.write('yyy', "yyy 2\n")

test.run(arguments = '.',
         stdout=test.wrap_stdout("""\
%(python)s build.py bar.in bar
%(python)s build.py foo.k foo
%(python)s build.py junk.k2 junk
%(python)s build.py moo.lork moo.blork
blork(["moo.ork"], ["moo.blork"])
""" % {'python':python}))

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n")
test.must_match('bar', "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 1\n")
test.must_match('junk', "yyy 2\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 1\n")
test.must_match('moo.ork', "xxx 2\nmoo.lork 1 line 2\nyyy 2\nmoo.lork 1 line 4\ninclude zzz\n")

test.write('zzz', "zzz 2\n")

test.run(arguments = '.',
         stdout=test.wrap_stdout("""\
%(python)s build.py bar.in bar
%(python)s build.py junk.k2 junk
""" % {'python':python}))

test.must_match('foo', "foo.k 1 line 1\nxxx 2\nyyy 2\nfoo.k 1 line 4\n")
test.must_match('bar', "yyy 2\nbar.in 1 line 2\nbar.in 1 line 3\nzzz 2\n")
test.must_match('junk', "yyy 2\njunk.k2 1 line 2\njunk.k2 1 line 3\nzzz 2\n")
test.must_match('moo.ork', "xxx 2\nmoo.lork 1 line 2\nyyy 2\nmoo.lork 1 line 4\ninclude zzz\n")

test.up_to_date(arguments = 'foo')

# Now make sure that using the same source file in different
# environments will get the proper scanner for the environment being
# used.

test.write('SConstruct2', """
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)
input_re = re.compile(r'^input\s+(\S+)$', re.M)

scan1 = Scanner(name = 'Include',
                function = lambda N,E,P,A: A.findall(N.get_contents()),
                argument = include_re,
                skeys = ['.inp'])

scan2 = Scanner(name = 'Input',
                function = lambda N,E,P,A: A.findall(N.get_contents()),
                argument = input_re,
                skeys = ['.inp'])

env1 = Environment()
env2 = Environment()

env1.Append(SCANNERS=scan1)
env2.Append(SCANNERS=scan2)

env1.Command('frog.1', 'frog.inp', r'%(python)s do_incl.py $TARGET $SOURCES')
env2.Command('frog.2', 'frog.inp', r'%(python)s do_inp.py $TARGET $SOURCES')

"""%{'python':python})

process = r"""
import sys

def process(infp, outfp):
    prefix = '%(command)s '
    l = len(prefix)
    for line in infp.readlines():
        if line[:l] == prefix:
            process(open(line[l:-1], 'rb'), outfp)
        else:
            outfp.write(line)

process(open(sys.argv[2], 'rb'),
        open(sys.argv[1], 'wb'))
sys.exit(0)
"""

test.write('do_incl.py', process % { 'command' : 'include' })
test.write('do_inp.py', process % { 'command' : 'input' })

test.write('frog.inp', """\
include sound1
input sound2
""")

test.write('sound1', 'croak\n')
test.write('sound2', 'ribbet\n')

test.run(arguments='-f SConstruct2 .',
stdout=test.wrap_stdout("""\
%(python)s do_incl.py frog.1 frog.inp
%(python)s do_inp.py frog.2 frog.inp
""" % { 'python':python }))

test.must_match('frog.1', 'croak\ninput sound2\n')
test.must_match('frog.2', 'include sound1\nribbet\n')

test.write('sound2', 'rudeep\n')

test.run(arguments='-f SConstruct2 .',
stdout=test.wrap_stdout("""\
%(python)s do_inp.py frog.2 frog.inp
""" % { 'python':python }))

test.must_match('frog.1', 'croak\ninput sound2\n')
test.must_match('frog.2', 'include sound1\nrudeep\n')

test.pass_test()
