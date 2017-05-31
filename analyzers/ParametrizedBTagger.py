'''Applies parametrized b tagging to a collection of jets.'''
from heppy.framework.analyzer import Analyzer
from heppy.papas.data.historyhelper import HistoryHelper
from heppy.analyzers.ChargedHadronsFromB import is_ptc_from_b
from heppy.particles.genbrowser import GenBrowser

def is_matched_to_b(jet):
    '''returns true if jet.match is a b quark.
    matching must be done before.
    does not work because of low matching efficiency? 
    '''
    is_bjet = False 
    if jet.match and \
       abs(jet.match.pdgid())== 5:
        is_bjet = True    
    return is_bjet


def is_from_b(jet, event, fraction):
    '''returns true if more than a fraction of the jet energy
    is from a b.'''
    history = HistoryHelper(event.papasevent)
    if not hasattr(event, 'genbrowser'):
        event.genbrowser = GenBrowser(event.gen_particles,
                                      event.gen_vertices)       
    sum_e_from_b = 0
    charged_ptcs = jet.constituents[211]
    print '*' * 50
    print jet
    for ptc in charged_ptcs:
        print ptc
        simids = history.get_linked_collection(ptc.uniqueid, 'ps')
        for simid in simids:
            simptc = event.papasevent.get_object(simid)
            if is_ptc_from_b(event, simptc.gen_ptc, event.genbrowser):
                print 'from b'
                print simptc
                sum_e_from_b += simptc.e()
            else:
                print 'NOT from b'
        print '*'
    print sum_e_from_b / jet.e()
    return True
    


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
            is_bjet = is_from_b(jet, event, fraction=0.5)
            is_b_tagged = self.cfg_ana.roc.is_tagged(is_bjet)
            jet.tags['b'] = is_b_tagged
            jet.tags['bmatch'] = is_bjet
