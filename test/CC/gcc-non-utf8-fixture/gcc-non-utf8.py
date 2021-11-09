import sys

if __name__ == '__main__':
    if '--version' in sys.argv:
        with open("data", "rb") as f:
            sys.stdout.buffer.write(f.read())
