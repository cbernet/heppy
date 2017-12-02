'''Select objects'''

from heppy.framework.analyzer import Analyzer
import collections

class Selector(Analyzer):
    '''Select objects from the input_objects collection 
    and store them in the output collection. The objects are not copied
    in the process. 

    Example::
        leptons = cfg.Analyzer(
          Selector,
          'sel_leptons',
          output = 'leptons',
          input_objects = 'rec_particles',
          filter_func = lambda ptc: ptc.e()> 5. and abs(ptc.pdgid()) in [11, 13],
          nmax = 2
          )

    @param input_objects: the input collection.
        If a dictionary, the filtering function is applied to the dictionary values,
        and not to the keys.

    @param output: the output collection.

    @param filter_func: a function object.
    
    @param nmax: up to nmax objects verifying filter_func are kept (optional).
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
        if hasattr(self.cfg_ana, 'nmax'):
            output_collection = output_collection[:self.cfg_ana.nmax]
        setattr(event, self.cfg_ana.output, output_collection)
