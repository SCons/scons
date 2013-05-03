#!/usr/bin/env python
#
# Searches through the whole source tree and validates all
# documentation files against our own XSD in docs/xsd.
#

import os
import SConsDoc

if __name__ == "__main__":
    if SConsDoc.validate_all_xml(['src',
                                  os.path.join('doc','design'),
                                  os.path.join('doc','developer'),
                                  os.path.join('doc','man'),
                                  os.path.join('doc','python10'),
                                  os.path.join('doc','reference'),
                                  os.path.join('doc','user')
                                  ]):
        print "OK"
    else:
        print "Validation failed! Please correct the errors above and try again."
