'''Applies parametrized b tagging to a collection of jets.'''
from heppy.framework.analyzer import Analyzer

class ParametrizedBTagger(Analyzer):
    '''Applies parametrized b tagging to a collection of jets.
 
    Example::
    
        from heppy.analyzers.ParametrizedBTagger import ParametrizedBTagger
        from heppy.analyzers.roc import cms_roc
        cms_roc.set_working_point(0.7)
        btag = cfg.Analyzer(
            ParametrizedBTagger,
            input_jets='jets',
            roc=cms_roc
        )
    
    A working point is chosen on the ROC curve, and used to define
     - the b tagging efficiency (above, 70%)
     - the b mistagging probability for non-b jets
     
    And b tag is added to each L{jet<heppy.particles.jet.Jet>}, and can be
    accessed later on as C{jet.tags['b']}. The tag is set to True if the jet
    is identified as a b jet, and to False otherwise. 
    
    @param input_jets: input collection of jets. The jets must have been
      L{matched<heppy.analyzers.Matcher.Matcher>} to b quarks before this module.
    @param roc: L{ROC curve<heppy.analyzers.roc.ROC>}
    '''
    def process(self, event):
        '''Process the event.
        
        The event must contain:
         - the collection of jets to be tagged, matched to b quarks
         
        Modifies each jet, setting jet.tags['b'] to True or False
        '''
        jets = getattr(event, self.cfg_ana.input_jets)
        for jet in jets:
            is_bjet = False 
            if jet.match and \
               jet.match.match and \
               abs(jet.match.match.pdgid())== 5:
                is_bjet = True
            is_b_tagged = self.cfg_ana.roc.is_tagged(is_bjet)
            jet.tags['b'] = is_b_tagged
