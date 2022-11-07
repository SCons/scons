import TestSCons

test = TestSCons.TestSCons()

test.dir_fixture("CXX-modules-fixture")

test.run(arguments = ".")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
