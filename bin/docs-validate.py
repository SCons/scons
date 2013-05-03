#!/usr/bin/env python
#
# Searches through the whole source tree and validates all
# documentation files against our own XSD in docs/xsd.
# Additionally, it rewrites all files such that the XML gets
# pretty-printed in a consistent way. This is done to ensure that
# merging and diffing doesn't get too hard when people start to
# use different XML editors...
#

import SConsDoc

if __name__ == "__main__":
    if SConsDoc.validate_all_xml():
        print "OK"
    else:
        print "Validation failed! Please correct the errors above and try again."
