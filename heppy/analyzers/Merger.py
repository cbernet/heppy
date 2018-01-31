'''Merges collections of particle-like objects into a single collection.'''

from heppy.framework.analyzer import Analyzer
import copy
import itertools


class Merger(Analyzer):
    '''Merges collections of particle-like objects into a single collection
    
    Example::
    
        from heppy.particles.p4 import P4
        from heppy.analyzers.Merger import Merger
        merge_particles = cfg.Analyzer(
          Merger,
          instance_label = 'leptons', 
          inputs = ['electrons','muons'],
          output = 'leptons',
          sort_key = P4.sort_key
        )
        
    The objects from the input collections are not copied. 
            
    @param inputs: names of the collections to be merged 
    @param output: name of the output collection
    @param sort_key: (Optional) sort key for the output collection.
      If P4.sort_key is provided, particles are properly sorted by decreasing
      E or pT depending on the type of collider defined in the configuration
      file, see L{heppy.configuration.Collider}.
    '''
    
    def process(self, event):
        '''Process event
        
        The event must contain
         - all input collections defined in self.cfg_ana.inputs
         
        Creates:
         - output collection event.<self.cfg_ana.output>
        '''
        inputs = [getattr(event, name) for name in self.cfg_ana.inputs]
        output = list(ptc for ptc in itertools.chain(*inputs))
        if hasattr(self.cfg_ana, 'sort_key'):
            output.sort(key=self.cfg_ana.sort_key,
                        reverse=True)
        setattr(event, self.cfg_ana.output, output)
        
        
        
  
