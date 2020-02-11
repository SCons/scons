import subprocess
import sys
if '-dumpversion' in sys.argv:
    print('3.9.9')
    sys.exit(0)
if '--version' in sys.argv:
    print('this is version 2.9.9 wrapping', sys.argv[2])
    sys.exit(0)
if sys.argv[1] not in [ '2.9.9', '3.9.9' ]:
    print('wrong version', sys.argv[1], 'when wrapping', sys.argv[2])
    sys.exit(1)
subprocess.run(" ".join(sys.argv[2:]), shell=True)
