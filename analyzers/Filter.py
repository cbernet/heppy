from heppy.framework.analyzer import Analyzer
import collections

class Filter(Analyzer):
    '''Filter objects from the input_objects collection 
    and store them in the output collection 

    Example: 

    from heppy.analyzers.Filter import Filter
    leptons_true = cfg.Analyzer(
      Filter,
      'sel_leptons',
      output = 'leptons_true',
      input_objects = 'particles',
      filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]
    )

    * input_objects : the input collection.
        if a dictionary, the filtering function is applied to the dictionary values,
        and not to the keys.

    * output : the output collection 

    * filter_func : a function object. 
    You may define a function in the usual way in your configuration file, 
    or use a lambda statement as done above. 
    This lambda statement is the definition of a function. It means: 
    given ptc, return ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]. 
    In other words, return True if the particle has an energy larger than 10 GeV, 
    and a pdgid equal to +-11 (electrons) or +-13 (muons).
    '''

    def process(self, event):
        input_collection = getattr(event, self.cfg_ana.input_objects)
        output_collection = None
        if isinstance(input_collection, collections.Mapping):
            output_collection = dict( [(key, val) for key, val in input_collection.iteritems()
                                       if self.cfg_ana.filter_func(val)] ) 
        else:
            output_collection = [obj for obj in input_collection \
                                 if self.cfg_ana.filter_func(obj)]
        setattr(event, self.cfg_ana.output, output_collection)
