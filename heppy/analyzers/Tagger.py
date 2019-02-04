from heppy.framework.analyzer import Analyzer

class Tagger(Analyzer):
    '''sets entries in the tag dictionary of the input objects.
    
    Example::

        from heppy.analyzers.Tagger import Tagger
        jet_tagger = cfg.Analyzer(
            Tagger,
            input_objects='jets',
            tags = {
              nptcs10 : lambda x: x.constituents.n_particles()>=10,
              ncharged10 : lambda x: x.constituents.n_charged_hadrons()>10,
              is_photon : lambda x: x.constituents[22].e()/x.e()>0.95
            }
        )


    @param input_jets: input collection of objects. They must have a tags dictionary.
    @param roc: L{ROC curve<heppy.analyzers.roc.ROC>}
    '''
    
    def process(self, event):
        objects = getattr(event, self.cfg_ana.input_objects)
        tags = self.cfg_ana.tags
        for obj in objects:
            for tagname, func in tags.iteritems():
                obj.tags[tagname] = func(obj)
        
