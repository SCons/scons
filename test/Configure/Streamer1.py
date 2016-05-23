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
Test for BitBucket PR 126:

SConf doesn't work well with 'io' module on pre-3.0 Python. This is because
io.StringIO (used by SCons.SConf.Streamer) accepts only unicode strings.
Non-unicode input causes it to raise an exception.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
# SConstruct
#
# The CheckHello should return 'yes' if everything works fine. Otherwise it
# returns 'failed'.
#
def hello(target, source, env):
  import traceback
  try:
    print('hello!\\n') # this breaks the script
    with open(env.subst('$TARGET', target = target),'w') as f:
      f.write('yes')
  except:
    # write to file, as stdout/stderr is broken
    traceback.print_exc(file=open('traceback','w'))
  return 0

def CheckHello(context):
  import sys
  context.Display('Checking whether hello works... ')
  stat,out = context.TryAction(hello,'','.in')
  if stat and out:
    context.Result(out)
  else:
    context.Result('failed')
  return out

env = Environment()
cfg = Configure(env)

cfg.AddTest('CheckHello', CheckHello)
cfg.CheckHello()

env = cfg.Finish()
""")

test.run(arguments = '.')
test.must_contain_all_lines(test.stdout(), ['Checking whether hello works... yes'])
test.must_not_exist('traceback')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
