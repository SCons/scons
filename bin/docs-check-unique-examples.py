#!/usr/bin/env python
#
# Searches through the whole doc/user tree and verifies
# that the names of the single examples are unique over
# all *.xml files.
# Additionally, the suffix entries have to be unique
# within each scons_command_output.
#

import os
import SConsExamples

if __name__ == "__main__":
    if SConsExamples.exampleNamesAreUnique(os.path.join('doc','user')):
        print "OK"
    else:
        print "Not all example names and suffixes are unique! Please correct the errors listed above and try again."
