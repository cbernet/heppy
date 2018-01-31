'''Deponstrates how to stop processing at a given event.'''

from heppy.framework.analyzer import Analyzer
from heppy.framework.exceptions import UserStop

class Stopper(Analyzer):
    '''Deponstrates how to stop processing at a given event.
    
    Example::
    
       stopper = cfg.Analyzer(
         Stopper,
         iEv = 10
       )
    
    This analyzer sends a L{UserStop<heppy.framework.exceptions.UserStop>} exception
    when the specified event is reached. The L{Looper<heppy.framework.looper.Looper>}
    then stops the processing of the events.
    
    Typically, such C{Stoppers} are used to stop the processing to investigate
    an event of interest interactively.
    
    @param iEv: event where to stop
    '''

    def process(self, event):
        '''Process the event.         
        '''
        if event.iEv == self.cfg_ana.iEv:
            raise UserStop('stopping at event {iEv}'.format(iEv=event.iEv))
                             
        
