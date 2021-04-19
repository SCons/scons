import package1  # noqa: F401
import package2  # noqa: F401
import sys

with open(sys.argv[1], 'w') as f:
    f.write('test')
