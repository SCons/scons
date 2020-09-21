#!/usr/bin/env python
#
# Searches through the whole doc/user tree and creates
# all output files for the single examples.
#
import os
import sys
import SConsExamples

if __name__ == "__main__":
    print("Checking whether all example names are unique...")
    if SConsExamples.exampleNamesAreUnique(os.path.join('doc', 'user')):
        print("OK")
    else:
        print(
            "Not all example names and suffixes are unique! "
            "Please correct the errors listed above and try again."
        )
        sys.exit(1)

    SConsExamples.createAllExampleOutputs(os.path.join('doc', 'user'))
