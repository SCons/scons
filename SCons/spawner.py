#!/usr/bin/env python
import sys
import pickle
import subprocess
import struct


INT_STRUCT = struct.Struct("L")


def main():
    while True:
        size_buf = sys.stdin.buffer.read(INT_STRUCT.size)
        if len(size_buf) == 0:
            break

        msg_size, = INT_STRUCT.unpack(size_buf)
        params = pickle.loads(sys.stdin.buffer.read(msg_size))
        proc = subprocess.Popen(params["args"], env=params["env"], close_fds=True)
        sys.stdout.buffer.write(INT_STRUCT.pack(proc.wait()))
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
