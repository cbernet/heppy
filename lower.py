import sys
import os

files = sys.argv[1:]
for path in files:
    dir, fnam = os.path.split(path)
    lfnam = ''.join([fnam[0].lower(), fnam[1:]])
    lpath = '/'.join([dir, lfnam])
    os.rename(path, lpath)
