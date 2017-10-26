import sys
import imp

config = None
display_config = None

def load_config(heppy_cfg_path):
    '''@return: configuration object from heppy config file'''
    global config
    global display_config
    cfgfile = open(heppy_cfg_path)
    cfgmod = imp.load_source('config', heppy_cfg_path, cfgfile)
    config = cfgmod.config
    cfgfile.close()
    display_config = cfgmod.display
    return config

def next():
    process(loop.iEvent+1)

def process(ievent):
    loop.process(ievent)
    print loop.event
    if display_config:
        loop.analyzer(display_config.name).display.draw()
    
if __name__ == "__main__":
    
    import os
    import imp
    
    from optparse import OptionParser
    from heppy.framework.looper import Looper
    
    parser = OptionParser()
    parser.usage = """
    %prog [options] <heppy_config> 
    Start heppy in interactive mode
    """
    parser.add_option("-e", "--event",
                      dest="event",
                      type="int",
                      help="index of first event to process (default 0)",
                      default=None)
    parser.add_option("-n", "--nevent",
                      dest="nevents",
                      type="int",
                      help="number of events to process (default none: see -i)",
                      default=None)
    
    (options,args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error('incorrect number of arguments')
        
    cfgfilename = args[0]    
    config = load_config(cfgfilename)
    
    nevents = sys.maxint
    if options.nevents is not None and options.event is not None:
        raise ValueError('provide either the -i or the -n option, but not both')
    elif options.nevents is None and options.event is None:
        options.event = 0
    elif options.nevents is not None:
        nevents = options.nevents
    
    if options.event is not None:
        ievent = options.event
        display_config.do_display = True           
    else:
        display_config.do_display = False       
        

    loop = Looper( 'looper', config,
                   nEvents=nevents,
                   nPrint=sys.maxint,
                   timeReport=False)

    if options.event is not None: 
        process(ievent)
    else:
        loop.loop()
        loop.write()
