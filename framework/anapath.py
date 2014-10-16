import os
import re

pythonpath = os.environ['PYTHONPATH']

pattern = re.compile('(.*heppy.*)/(.*)')

analyzer_path = []
for path in pythonpath.split(':'):
    match = pattern.match(path)
    if match is not None:
        apath = match.group(1)
        anapath = '/'.join([apath, 'analyzers'])
        analyzer_path.append(anapath)

if __name__ == '__main__':
    print analyzer_path    
    
