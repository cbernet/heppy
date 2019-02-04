'''Analyzer accessing data from text input.'''

from heppy.framework.analyzer import Analyzer

class TextAnalyzer(Analyzer):
    '''Test analyzer accessing data from text input.
  
    Example::
    
      random = cfg.Analyzer(
        TextAnalyzer
      )
    '''
    
    def process(self, event):
        '''Process the event.
        
        Each attribute in event.input (the text input data)
        is copied to event
        '''
        event.x1 = event.input.x1
        event.x2 = event.input.x2
        