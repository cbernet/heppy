'''Fill a tree with jet and jet particle flow information'''

from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class JetTreeProducer(Analyzer):
    '''Fill a tree with jet and jet component information
    
    Example::
    
        from heppy.analyzers.JetTreeProducer import JetTreeProducer
        jet_tree = cfg.Analyzer(
            JetTreeProducer,
            tree_name = 'events',
            tree_title = 'jets',
            jets = 'gen_jets'
            )

    Variables in the tree, for the first two jets in the input jet
    collection.
     - jet p4
     - for each component (charged hadrons, neutral hadrons, photons, ...):
         - number of such particles of this type
         - sum pT of these particles
         - sum E of these particles
         
    If you want these quantities for the jets matched to your input jets,
    run a Matcher on these jets before the JetTreeProducer.
    See heppy.test.jet_tree_sequence_cff for more information
    
    @param tree_name: name of the tree in the output root file
    @param tree_title: title of the tree
    @jets: input jet collection
    '''

    def beginLoop(self, setup):
        '''create the output root file and book the tree.
        '''
        self.rootfile = TFile('/'.join([self.dirName,
                                        'jet_tree.root']),
                              'recreate')
        self.tree = Tree( self.cfg_ana.tree_name,
                          self.cfg_ana.tree_title )
        bookJet(self.tree, 'jet1')
        bookJet(self.tree, 'jet1_match')
        bookJet(self.tree, 'jet2')
        bookJet(self.tree, 'jet2_match')
        var(self.tree, 'event')
        var(self.tree, 'lumi')
        var(self.tree, 'run')
 

    def process(self, event):
        '''process the event.
        
        The event must contain:
         - self.cfg_ana.jets: the jet collection to be studied. 
        '''
        self.tree.reset()
        if hasattr(event, 'eventId'): 
            fill(self.tree, 'event', event.eventId)
            fill(self.tree, 'lumi', event.lumi)
            fill(self.tree, 'run', event.run)
        elif hasattr(event, 'iEv'):
            fill(self.tree, 'event', event.iEv)
        jets = getattr(event, self.cfg_ana.jets)
        if( len(jets)>0 ):
            jet = jets[0]
            comp211 = jet.constituents.get(211, None)
            if comp211: 
                if comp211.num==2:
                    import pdb; pdb.set_trace()
            fillJet(self.tree, 'jet1', jet)
            if hasattr(jet, 'match') and jet.match:
                fillJet(self.tree, 'jet1_match', jet.match)
                # if jet.e()/jet.match.e() > 2.:
                #     import pdb; pdb.set_trace()
        if( len(jets)>1 ):
            jet = jets[1]
            fillJet(self.tree, 'jet2', jet)
            if hasattr(jet, 'match') and jet.match:
                fillJet(self.tree, 'jet2_match', jet.match)
        self.tree.tree.Fill()
        
        
    def write(self, setup):
        '''write root file.
        '''
        self.rootfile.Close()
        
