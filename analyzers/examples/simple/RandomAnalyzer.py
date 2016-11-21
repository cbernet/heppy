'''Test analyzer adding a random variable to the event.'''

from heppy.framework.analyzer import Analyzer

import heppy.statistics.rrandom as random

class RandomAnalyzer(Analyzer):
    '''Test analyzer adding a random variable to the event.
    
    The variable is called var_random and has a value drawn from a uniform distribution
    ranging between 0 and 1.
    
    Example::
    
      random = cfg.Analyzer(
        RandomAnalyzer
      )
    '''
    
    def process(self, event):
        '''Process the event.
        
        This method creates:
         - event.var_random: the random variable, between 0 and 1.
        '''
        event.var_random = random.uniform(0,1)
