#!/usr/bin/env python

from heppy.framework.looper import Looper

if __name__ == '__main__':
    
    import pickle
    import sys
    import os
    import imp
    if len(sys.argv) == 2 :
        cfgFileName = sys.argv[1]
        pckfile = open( cfgFileName, 'r' )
        config = pickle.load( pckfile )
        comp = config.components[0]
        events_class = config.events_class
    elif len(sys.argv) == 3 :
        cfgFileName = sys.argv[1]
        file = open( cfgFileName, 'r' )
        cfg = imp.load_source( 'cfg', cfgFileName, file)
        compFileName = sys.argv[2]
        pckfile = open( compFileName, 'r' )
        comp = pickle.load( pckfile )
        cfg.config.components=[comp]
        events_class = cfg.config.events_class
    else:
        print 'usage: looper.py <configuration_file.py> [component.pickle]'
        sys.exit(1)
    looper = Looper( 'Loop', cfg.config,nPrint = 5)
    looper.loop()
    looper.write()
