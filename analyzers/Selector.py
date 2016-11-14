'''Select objects'''

from heppy.framework.analyzer import Analyzer
import collections

class Selector(Analyzer):
    '''Select objects from the input_objects collection 
    and store them in the output collection. The objects are not copied
    in the process. 

    Example:
    
    from heppy.analyzers.Selector import Selector
    def is_lepton(ptc):
      """Returns true if the particle energy is larger than 5 GeV
      and if its pdgid is +-11 (electrons) or +-13 (muons)
      return ptc.e()> 5. and abs(ptc.pdgid()) in [11, 13]

    leptons = cfg.Analyzer(
      Selector,
      'sel_leptons',
      output = 'leptons',
      input_objects = 'rec_particles',
      filter_func = is_lepton 
      )

    * input_objects : the input collection.
        If a dictionary, the filtering function is applied to the dictionary values,
        and not to the keys.

    * output : the output collection

    * filter_func : a function object.
    IMPORTANT NOTE: lambda statements should not be used, as they
    do not work in multiprocessing mode. looking for a solution...
    
    '''

    def process(self, event):
        '''event must contain
        
        * self.cfg_ana.input_objects: collection of objects to be selected
           These objects must be usable by the filtering function
           self.cfg_ana.filter_func.
        '''
        input_collection = getattr(event, self.cfg_ana.input_objects)
        output_collection = None
        if isinstance(input_collection, collections.Mapping):
            output_collection = dict( [(key, val) for key, val in input_collection.iteritems()
                                       if self.cfg_ana.filter_func(val)] ) 
        else:
            output_collection = [obj for obj in input_collection \
                                 if self.cfg_ana.filter_func(obj)]
        setattr(event, self.cfg_ana.output, output_collection)
