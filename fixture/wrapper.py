import os
import sys
path = os.path.join(os.path.abspath(__file__), 'wrapper.out')
open(path, 'wb').write(b"wrapper.py\n")
os.system(" ".join(sys.argv[1:]))
