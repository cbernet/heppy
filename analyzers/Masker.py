'''Masks objects in a collection'''

from heppy.framework.analyzer import Analyzer

class Masker(Analyzer):
    '''Masks objects in a collection.
    
    Example::

        from heppy.analyzers.Masker import Masker
        particles_not_zed = cfg.Analyzer(
          Masker,
          input = 'gen_particles_stable',
          output = 'particles_not_zed',
          mask = 'zed_legs',
        )

    This analyzer creates a new collection containing the objects
    that are in the input collection and that are not in the mask collection.
    The objects are not copied. 
    
    @param input: input collection  
    @param mask: masking collection
    @param output: output collection (created)
    '''
    
    def process(self, event):
        '''process event
        
        The event must contain:
         - self.cfg_ana.input: the input collection
         - self.cfg_ana.mask: the masking collection
         
        The method creates:
         - event.<self.cfg_ana.output>
        '''
        inputs = getattr(event, self.cfg_ana.input)
        masks = getattr(event, self.cfg_ana.mask)
        output = [obj for obj in inputs if obj not in masks]
        setattr(event, self.cfg_ana.output, output)
