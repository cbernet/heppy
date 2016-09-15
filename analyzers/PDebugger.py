from heppy.framework.analyzer import Analyzer
import heppy.utils.pdebug as pdebugging
from heppy.utils.pdebug import pdebugger
from heppy.papas.data.pfevent import PFEvent


class PDebugger(Analyzer):
    ''' Module to output physics debug output
    '''
    def __init__(self, *args, **kwargs):
        super(PDebugger, self).__init__(*args, **kwargs) 
        if hasattr(self.cfg_ana, 'console_level') ==True :
            pass
            pdebugging.set_streamlevel(self.cfg_ana.console_level)       
        if hasattr(self.cfg_ana, 'debug_file') ==True :
            pass
            pdebugging.set_file(self.cfg_ana.debug_file) #optional writes to file
        
        pdebugger.setLevel(self.cfg_ana.debug_level) # turns on or off output
       
        pdebugger.info("inits")
        pass
        
    def process(self, event):
        pdebugger.info(str('Event: {}'.format(event.iEv)))
        pass         