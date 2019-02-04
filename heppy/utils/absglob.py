import glob as gglob
import os

def glob(pattern):
    return [os.path.abspath(fname) for fname in gglob.glob(pattern)]

if __name__ == "__main__":
    import sys

    print glob(sys.argv[1])
