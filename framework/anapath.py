import os
import sys

try:
    root = os.environ["HEPPY"]
except KeyError:
    print """
anapath.py: Define the PYFCC environment variable.

This variable should contain the path to the root directory of the python
analysis framework.
    """
    sys.exit(1)
analyzer_path = ['/'.join( [root, 'analyzers'] )]

if __name__=='__main__':

    import pprint
    import sys

    pprint.pprint(sys.path)
    sys.path = analyzer_path + sys.path
    print
    pprint.pprint(sys.path)
