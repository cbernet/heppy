'''Demonstrates how to log event variables.'''

from heppy.framework.analyzer import Analyzer

class Printer(Analyzer):
    '''Demonstrates how to log event variables.
    '''
    def beginLoop(self, setup):
        super(Printer, self).beginLoop(setup)
        
    def process(self, event):
        '''Process the event.
        
        The input data must contain a variable called "var1",
        which is the case of the L{test tree<heppy.utils.testtree>}. 
        '''
        self.logger.info(
            "event {iEv}, var1 {var1}".format(
                iEv = event.iEv, var1 = event.input.var1
            ))
                             
        
