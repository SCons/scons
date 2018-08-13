import os
import sys

path = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'wrapper.out')

# handle the case that an arg was passed in with 
# quotes to protect path spaces on the command line
args = []
for arg in sys.argv[1:]:
    if ' ' in arg:
        args.append('"' + arg + '"')
    else:
        args.append(arg)

open(path, 'a').write("wrapper_with_args.py %s\n" % " ".join(args))
os.system(" ".join(args))
