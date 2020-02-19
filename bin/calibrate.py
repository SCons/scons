#!/usr/bin/env python
#
# Copyright (c) 2009 The SCons Foundation
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
import optparse
import os
import re
import subprocess
import sys

variable_re = re.compile(r'^VARIABLE: (.*)$', re.M)
elapsed_re = re.compile(r'^ELAPSED: (.*)$', re.M)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage="calibrate.py [-h] [-p PACKAGE], [--min time] [--max time] timings/*/*-run.py")
    parser.add_option('--min', type='float', default=9.5,
                      help="minimum acceptable execution time (default 9.5)")
    parser.add_option('--max', type='float', default=10.00,
                      help="maximum acceptable execution time (default 10.00)")
    parser.add_option('-p', '--package', type="string",
                      help="package type")
    opts, args = parser.parse_args(argv[1:])

    os.environ['TIMESCONS_CALIBRATE'] = '1'

    for arg in args:
        if len(args) > 1:
            print(arg + ':')

        command = [sys.executable, 'runtest.py']
        if opts.package:
            command.extend(['-p', opts.package])
        command.append(arg)

        run = 1
        good = 0
        while good < 3:
            p = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
            output = p.communicate()[0]
            vm = variable_re.search(output)
            em = elapsed_re.search(output)
            try:
                elapsed = float(em.group(1))
            except AttributeError:
                print(output)
                raise
            print("run %3d: %7.3f:  %s" % (run, elapsed, ' '.join(vm.groups())))
            if opts.min < elapsed < opts.max:
                good += 1
            else:
                good = 0
                for v in vm.groups():
                    var, value = v.split('=', 1)
                    # TODO: this sometimes converges slowly, better algorithm?
                    value = int((int(value) * opts.max) // elapsed)
                    os.environ[var] = str(value)
            run += 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
