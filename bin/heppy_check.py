#!/usr/bin/env python
# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

import sys
import re
import os
import pprint

def check_chunk(dirname):
    if not os.path.isdir(dirname):
        return -1
    if dirname.find('_Chunk') == -1:
        return -1
    logName  = '/'.join([dirname, 'log.txt'])
    if not os.path.isfile( logName ):
        print dirname, ': log.txt does not exist'
        return 0
    logFile = open(logName)
    nEvents = -1
    for line in logFile:
        try:
            nEvents = line.split('processed:')[1]
        except:
            pass
    if nEvents == -1:
        print dirname, 'cannot find number of processed events'
        return 0
    else:
        return 1    

if __name__ == '__main__':
    
    from optparse import OptionParser
    
    parser = OptionParser(usage='%prog <target_directories> [options]',
                          description='Check one or more chunck folders. Wildcard (*) can be used to specify multiple directories')
    
    parser.add_option("-b","--batch", dest="batch",
                      default=None,
                      help="batch command for resubmission"
                      )
    
    (options,args) = parser.parse_args()
    
    if len(args)==0:
        print 'provide at least one directory in argument. Use -h to display help'
    
    dirs = sys.argv[1:]
    
    badDirs = []
    
    for dirname in dirs:
        code = check_chunk(dirname)
        if code == 0:
            badDirs.append(dirname)
    
    print 'list of bad directories:'
    pprint.pprint(badDirs)
    
    if options.batch is not None:
        for dirname in badDirs:
            oldPwd = os.getcwd()
            os.chdir( dirname )
            cmd =  [options.batch, '-J', dirname, ' < batchScript.sh' ]
            print 'resubmitting in', os.getcwd()
            cmds = ' '.join( cmd )
            print cmds
            os.system( cmds )
            os.chdir( oldPwd )
            
