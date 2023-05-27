# SPDX-License-Identifier: MIT
#
# Copyright The SCons Foundation

"""Test that spaces in the target dir name doesn't break MSVC_BATCH."""

import TestSCons

test = TestSCons.TestSCons()

test.skip_if_not_msvc()
test.dir_fixture('MSVC_BATCH-spaces-fixture')
test.run(stderr=None)  # it's enough that the build didn't fail
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4
