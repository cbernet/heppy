from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *
from heppy.particles.tlv.resonance import Resonance2 as Resonance

from ROOT import TFile

class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        self.tree.var('tau1', float)
        self.tree.var('tau2', float)
        self.tree.var('tau3', float)
        self.tree.var('tau32', float)
        self.tree.var('tau31', float)
        self.tree.var('tau21', float)

        bookParticle(self.tree, 'Jet')
        bookParticle(self.tree, 'softDroppedJet')
        bookParticle(self.tree, 'leadingSoftDroppedSubJet')
        bookParticle(self.tree, 'trailingSoftDroppedSubJet')

    def process(self, event):
        self.tree.reset()
        jets = getattr(event, self.cfg_ana.fatjets)
        
        # store leading (fat) jet observables
        if len(jets) > 0 and len(jets[0].subjetsSoftDrop) > 2:
            self.tree.fill('tau1' , jets[0].tau1 )
            self.tree.fill('tau2' , jets[0].tau2 )
            self.tree.fill('tau3' , jets[0].tau3 )
            self.tree.fill('tau31' , jets[0].tau3/jets[0].tau1 )
            self.tree.fill('tau32' , jets[0].tau3/jets[0].tau2 )
            self.tree.fill('tau21' , jets[0].tau2/jets[0].tau1 )

            fillParticle(self.tree, 'Jet', jets[0])
            
            # first subjet entry is the cleaned jet itself
            fillParticle(self.tree, 'softDroppedJet', jets[0].subjetsSoftDrop[0])
            fillParticle(self.tree, 'leadingSoftDroppedSubJet', jets[0].subjetsSoftDrop[1])
            fillParticle(self.tree, 'trailingSoftDroppedSubJet', jets[0].subjetsSoftDrop[2])
            
            self.tree.tree.Fill()

    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()

