'''Remove particles from a collection.'''

from heppy.framework.analyzer import Analyzer
import copy
import itertools


class Subtractor(Analyzer):
    '''Remove particles from a collection
        
    Example:: 

        from heppy.analyzers.Subtractor import Subtractor
        merge_particles = cfg.Analyzer(
            Subtractor,
            inputA = 'jets',
            inputB = 'leptons',
            output = 'jets_minus_leptons', 
        )
        
    @param inputA: input collection of particles
    @param inputB: particles to be removed
    @param output: output collection (inputA - inputB).
      The particles are properly sorted, and no copy is done.  
    '''

    def process(self, event):
        '''Process the event.
        
        The event must contain:
         - self.cfg_ana.inputA
         - self.cfg_ana.inputB
         
        This method creates:
         - event.<self.cfg_ana.output>
        '''
        inputA = getattr(event, self.cfg_ana.inputA)
        inputB = getattr(event, self.cfg_ana.inputB)
        
        output = [ ptc for ptc in inputA if ptc not in inputB]
        
        if hasattr(self.cfg_ana, 'sort_key'):
            output.sort(key=self.cfg_ana.sort_key, reverse=True)
        setattr(event, self.cfg_ana.output, output)
