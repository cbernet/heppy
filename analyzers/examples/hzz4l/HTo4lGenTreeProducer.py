from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class HTo4lGenTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(HTo4lGenTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        self.tree.var('weight', float)

        bookParticle(self.tree, 'lep1vsPt')
        bookParticle(self.tree, 'lep2vsPt')
        bookParticle(self.tree, 'lep3vsPt')
        bookParticle(self.tree, 'lep4vsPt')

        bookParticle(self.tree, 'lep1vsEta')
        bookParticle(self.tree, 'lep2vsEta')
        bookParticle(self.tree, 'lep3vsEta')
        bookParticle(self.tree, 'lep4vsEta')


    def process(self, event):
        self.tree.reset()
        gen_leptons = getattr(event, self.cfg_ana.leptons)

        self.tree.fill('weight' , event.weight )
        
        if len(gen_leptons) >= 4:

            gen_leptons.sort(key=lambda x: x.pt(), reverse=True)

            fillParticle(self.tree, 'lep1vsPt', gen_leptons[0])
            fillParticle(self.tree, 'lep2vsPt', gen_leptons[1])
            fillParticle(self.tree, 'lep3vsPt', gen_leptons[2])
            fillParticle(self.tree, 'lep4vsPt', gen_leptons[3])

            gen_leptons.sort(key=lambda x: abs(x.eta()))

            fillParticle(self.tree, 'lep1vsEta', gen_leptons[0])
            fillParticle(self.tree, 'lep2vsEta', gen_leptons[1])
            fillParticle(self.tree, 'lep3vsEta', gen_leptons[2])
            fillParticle(self.tree, 'lep4vsEta', gen_leptons[3])

        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()

