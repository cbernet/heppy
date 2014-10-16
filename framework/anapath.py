import os
import re
import glob

pythonpath = os.environ['PYTHONPATH']

analyzer_path = []
for path in pythonpath.split(':'):
    anadirs = glob.glob( '/'.join([path, '*', 'analyzers']) )
    analyzer_path.extend(anadirs)

if __name__ == '__main__':
    print analyzer_path    
    
