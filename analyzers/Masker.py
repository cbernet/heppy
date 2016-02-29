from heppy.framework.analyzer import Analyzer

class Masker(Analyzer):
    '''Masks objects in input collection by objects in mask collection, 
    and returns the results in output collection. 

    Example: 

    from heppy.analyzers.Masker import Masker
    particles_not_zed = cfg.Analyzer(
      Masker,
      output = 'particles_not_zed',
      input = 'gen_particles_stable',
      mask = 'zeds',
    )
    '''
    def process(self, event):
        inputs = getattr(event, self.cfg_ana.input)
        masks = getattr(event, self.cfg_ana.mask)
        output = [obj for obj in inputs if obj not in masks]
        setattr(event, self.cfg_ana.output, output)
