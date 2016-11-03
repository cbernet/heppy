from heppy.framework.analyzer import Analyzer
import copy
import itertools


class Subtractor(Analyzer):
    '''Create a collection containing particles in inputA that are not contained in inputB.  
        
        Example: 

        from heppy.analyzers.Subtractor import Subtractor
        merge_particles = cfg.Analyzer(
            Subtractor,
            instance_label = 'jets_minus_leptons', 
            inputA = 'jets',
            inputB = 'leptons',
            output = 'jets_minus_leptons', 
        )
        '''

    def process(self, event):
        inputA = getattr(event, self.cfg_ana.inputA)
        inputB = getattr(event, self.cfg_ana.inputB)
        
        output = [ ptc for ptc in inputA if ptc not in inputB]
        
        if hasattr(self.cfg_ana, 'sort_key'):
            output.sort(key=self.cfg_ana.sort_key, reverse=True)
        setattr(event, self.cfg_ana.output, output)
