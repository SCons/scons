import sys

print(f"In {sys.argv[0]}")

if __name__ == '__main__':
    if '--version' in sys.argv:
        with open("data", "rb") as f:
            sys.stdout.buffer.write(f.read())
