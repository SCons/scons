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
Test the --cache-debug option to see if it prints the expected messages.

Note that we don't check for the "race condition" message when someone
else's build populates the CacheDir with a file in between the time we
to build it because it doesn't exist in the CacheDir, and the time our
build of the file completes and we push it out.
"""

import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re)

test.subdir('cache', 'src')

cache = test.workpath('cache')
debug_out = test.workpath('cache-debug.out')



test.write(['src', 'SConstruct'], """\
CacheDir(r'%(cache)s')
SConscript('SConscript')
""" % locals())

test.write(['src', 'SConscript'], """\
def cat(env, source, target):
    target = str(target[0])
    open('cat.out', 'ab').write(target + "\\n")
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Cat('aaa.out', 'aaa.in')
env.Cat('bbb.out', 'bbb.in')
env.Cat('ccc.out', 'ccc.in')
env.Cat('all', ['aaa.out', 'bbb.out', 'ccc.out'])
""")

test.write(['src', 'aaa.in'], "aaa.in\n")
test.write(['src', 'bbb.in'], "bbb.in\n")
test.write(['src', 'ccc.in'], "ccc.in\n")



# Test for messages about files not being in CacheDir, with -n (don't
# actually build or push) and sendinig the message to a file.

expect = \
r"""cat\(\["aaa.out"\], \["aaa.in"\]\)
cat\(\["bbb.out"\], \["bbb.in"\]\)
cat\(\["ccc.out"\], \["ccc.in"\]\)
cat\(\["all"\], \["aaa.out", "bbb.out", "ccc.out"\]\)
"""

test.run(chdir='src',
         arguments='-n -Q --cache-debug=%s .' % debug_out,
         stdout=expect)

expect = \
r"""CacheRetrieve\(aaa.out\):  [0-9a-fA-F]+ not in cache
CacheRetrieve\(bbb.out\):  [0-9a-fA-F]+ not in cache
CacheRetrieve\(ccc.out\):  [0-9a-fA-F]+ not in cache
CacheRetrieve\(all\):  [0-9a-fA-F]+ not in cache
"""

test.must_match(debug_out, expect, mode='r')



# Test for messages about actually pushing to the cache, without -n
# and to standard ouput.

expect = \
r"""CacheRetrieve\(aaa.out\):  [0-9a-fA-F]+ not in cache
cat\(\["aaa.out"\], \["aaa.in"\]\)
CachePush\(aaa.out\):  pushing to [0-9a-fA-F]+
CacheRetrieve\(bbb.out\):  [0-9a-fA-F]+ not in cache
cat\(\["bbb.out"\], \["bbb.in"\]\)
CachePush\(bbb.out\):  pushing to [0-9a-fA-F]+
CacheRetrieve\(ccc.out\):  [0-9a-fA-F]+ not in cache
cat\(\["ccc.out"\], \["ccc.in"\]\)
CachePush\(ccc.out\):  pushing to [0-9a-fA-F]+
CacheRetrieve\(all\):  [0-9a-fA-F]+ not in cache
cat\(\["all"\], \["aaa.out", "bbb.out", "ccc.out"\]\)
CachePush\(all\):  pushing to [0-9a-fA-F]+
"""

test.run(chdir='src',
         arguments='-Q --cache-debug=- .',
         stdout=expect)



# Clean up the local targets.

test.run(chdir='src', arguments='-c --cache-debug=%s .' % debug_out)
test.unlink(['src', 'cat.out'])



# Test for messages about retrieving files from CacheDir, with -n
# and sending the messages to standard output.

expect = \
r"""Retrieved `aaa.out' from cache
CacheRetrieve\(aaa.out\):  retrieving from [0-9a-fA-F]+
Retrieved `bbb.out' from cache
CacheRetrieve\(bbb.out\):  retrieving from [0-9a-fA-F]+
Retrieved `ccc.out' from cache
CacheRetrieve\(ccc.out\):  retrieving from [0-9a-fA-F]+
Retrieved `all' from cache
CacheRetrieve\(all\):  retrieving from [0-9a-fA-F]+
"""

test.run(chdir='src',
         arguments='-n -Q --cache-debug=- .',
         stdout=expect)



# And finally test for message about retrieving file from CacheDir
# *without* -n and sending the message to a file.

expect = \
r"""Retrieved `aaa.out' from cache
Retrieved `bbb.out' from cache
Retrieved `ccc.out' from cache
Retrieved `all' from cache
"""

test.run(chdir='src',
         arguments='-Q --cache-debug=%s .' % debug_out,
         stdout=expect)

expect = \
r"""CacheRetrieve\(aaa.out\):  retrieving from [0-9a-fA-F]+
CacheRetrieve\(bbb.out\):  retrieving from [0-9a-fA-F]+
CacheRetrieve\(ccc.out\):  retrieving from [0-9a-fA-F]+
CacheRetrieve\(all\):  retrieving from [0-9a-fA-F]+
"""

test.must_match(debug_out, expect, mode='r')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
