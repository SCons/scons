#!/usr/bin/env python
import sys
import pickle
import subprocess


def main():
    while True:
        try:
            params = pickle.load(sys.stdin.buffer)
        except EOFError:
            break
        proc = subprocess.Popen(params["args"], env=params["env"], close_fds=True)
        pickle.dump(proc.wait(), sys.stdout.buffer)
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
