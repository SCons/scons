import TestSCons



test = TestSCons.TestSCons()

test.skip_if_not_msvc()


test.dir_fixture('MSVC_BATCH-spaces-targetdir')
test.run()