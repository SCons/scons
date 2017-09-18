import os
import sys
if '--version' not in sys.argv and '-dumpversion' not in sys.argv:
    path = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'wrapper.out')
    open(path, 'w').write("wrapper.py\n")
os.system(" ".join(sys.argv[1:]))
