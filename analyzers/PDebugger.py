from heppy.framework.analyzer import Analyzer
import logging
import heppy.utils.pdebug as pdebugging
from heppy.papas.data.pfevent import PFEvent
import sys


class PDebugger(Analyzer):
    ''' Module to output physics debug output
    '''
    def __init__(self, *args, **kwargs):
        super(PDebugger, self).__init__(*args, **kwargs)

        #no output will occur unless one or both of the following is requested.

        #turn on output to stdout if requested
        if hasattr(self.cfg_ana, 'output_to_stdout') and self.cfg_ana.output_to_stdout:
                pdebugging.set_stream(sys.stdout,level=logging.INFO)
                pdebugging.pdebugger.setLevel(logging.INFO)

        #turn on output to file if requested
        if hasattr(self.cfg_ana, 'debug_filename'):
            pdebugging.set_file(self.cfg_ana.debug_filename)
            pdebugging.pdebugger.setLevel(logging.INFO)
        pass

    def process(self, event):
        pdebugging.pdebugger.info(str('Event: {}'.format(event.iEv)))
        pass 

