import TestSCons

test = TestSCons.TestSCons()

from SCons.Tool import gxx
from SCons.Script import DefaultEnvironment

if not gxx.exists(DefaultEnvironment()):
    test.skip_test('g++ not found, skipping test\n')

test.dir_fixture("CXX-modules-fixture")

test.run(arguments = ". toolset=g++")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
