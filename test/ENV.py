#!/usr/bin/env python

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir('bin1', 'bin2')

bin1 = test.workpath('bin1')
bin2 = test.workpath('bin2')
bin1_build_py = test.workpath('bin1', 'build.py')
bin2_build_py = test.workpath('bin2', 'build.py')

test.write('SConstruct', """
import os
bin1_path = r'%s' + os.pathsep + os.environ['PATH']
bin2_path = r'%s' + os.pathsep + os.environ['PATH']
Bld = Builder(name = 'Bld', action = "build.py %%(target)s %%(source)s")
bin1 = Environment(ENV = {'PATH' : bin1_path}, BUILDERS = [Bld])
bin2 = Environment(ENV = {'PATH' : bin2_path}, BUILDERS = [Bld])
bin1.Bld(target = 'bin1.out', source = 'input')
bin2.Bld(target = 'bin2.out', source = 'input')
""" % (bin1, bin2))

test.write(bin1_build_py,
"""#!/usr/bin/env python
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write("bin1/build.py\\n")
file.write(contents)
file.close()
""")
os.chmod(bin1_build_py, 0755)

test.write(bin2_build_py,
"""#!/usr/bin/env python
import sys
contents = open(sys.argv[2], 'r').read()
file = open(sys.argv[1], 'w')
file.write("bin2/build.py\\n")
file.write(contents)
file.close()
""")
os.chmod(bin2_build_py, 0755)

test.write('input', "input file\n")

#test.run(arguments = '.')
test.run(arguments = 'bin1.out bin2.out')

test.fail_test(test.read('bin1.out') != "bin1/build.py\ninput file\n")
test.fail_test(test.read('bin2.out') != "bin2/build.py\ninput file\n")

test.pass_test()
