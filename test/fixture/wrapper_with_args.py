import os
import sys

path = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'wrapper.out')

open(path, 'a').write("wrapper_with_args.py %s\n" % " ".join(sys.argv[1:]))
os.system(" ".join(sys.argv[1:]))
