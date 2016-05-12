from heppy.framework.analyzer import Analyzer
import copy



class Merger(Analyzer):
    '''Returns a new merged list from two input lists  
    
        
        Example: 
    
        from heppy.analyzers.Merger import Merger
        merge_particles = cfg.Analyzer(
            Merger,
            instance_label = 'merge_particles', 
            inputA = 'papas_PFreconstruction_particles_list',
            inputB = 'smeared_leptons',
            output = 'rec_particles', 
        )
    
        inputA:      list of things 
        inputB:      list of things
        output:      will end up containing merged list of the two above
        '''        
    def process(self, event):
        inputA = getattr(event, self.cfg_ana.inputA)
        inputB = getattr(event, self.cfg_ana.inputB)
        
        output = copy.copy(inputA)
        output.extend(inputB)
        setattr( event, self.cfg_ana.output, output)
        
        
        
  