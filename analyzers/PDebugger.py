from heppy.framework.analyzer import Analyzer
import logging
import heppy.utils.pdebug as pdebugging
from heppy.papas.data.pfevent import PFEvent



class PDebugger(Analyzer):
    ''' Module to output physics debug output
    '''
    def __init__(self, *args, **kwargs):
        super(PDebugger, self).__init__(*args, **kwargs) 
        #bnot working as expected
        pdebugging.pdebugger.setLevel(self.cfg_ana.debug_level)
        pdebugging.set_stream(level=self.cfg_ana.console_level)
        pdebugging.set_file(self.cfg_ana.debug_file)
        pdebugging.pdebugger.info('blah')
        
        pass
        
    def process(self, event):
        pdebugging.pdebugger.info(str('Event: {}'.format(event.iEv)))
        pass         