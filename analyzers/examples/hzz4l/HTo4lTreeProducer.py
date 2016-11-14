from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class HTo4lTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(HTo4lTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        
        bookVariable(self.tree, 'weight')
        bookParticle(self.tree, 'zed1')
        bookParticle(self.tree, 'zed2')
        bookLepton(self.tree, 'zed1_lep1')
        bookLepton(self.tree, 'zed1_lep2')
        bookLepton(self.tree, 'zed2_lep1')
        bookLepton(self.tree, 'zed2_lep2')
        bookParticle(self.tree, 'higgs')

    def process(self, event):
        self.tree.reset()
        zeds = getattr(event, self.cfg_ana.zeds)
        zeds.sort(key=lambda x: abs(x.m()-91.))
        higgses = getattr(event, self.cfg_ana.higgses)

        fillVariable(self.tree, 'weight' , event.weight)

        if len(zeds) > 1:

            fillParticle(self.tree, 'zed1', zeds[0])
            fillParticle(self.tree, 'zed2', zeds[1])

            fillLepton(self.tree, 'zed1_lep1', zeds[0].legs[0])
            fillLepton(self.tree, 'zed1_lep2', zeds[0].legs[1])
            fillLepton(self.tree, 'zed2_lep1', zeds[1].legs[0])
            fillLepton(self.tree, 'zed2_lep2', zeds[1].legs[1])

        if len(higgses) > 0:  

            higgs = higgses[0]
            fillParticle(self.tree, 'higgs', higgs)

        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()

