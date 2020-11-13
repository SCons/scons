import package1
import package2
import sys

raise Exception(sys.argv)

with open(sys.argv[1], 'w') as f:
    f.write('test')
