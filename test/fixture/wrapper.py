import os
import sys
import subprocess

if __name__ == '__main__':
    path = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'wrapper.out')
    if '--version' not in sys.argv and '-dumpversion' not in sys.argv:
        with open(path, 'wb') as f:
            f.write(b"wrapper.py\n")
    subprocess.run(sys.argv[1:])
