from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        self.taggers = 'b'
        bookJet(self.tree, 'jet1', self.taggers)
        bookJet(self.tree, 'jet2', self.taggers)
        bookJet(self.tree, 'jet3', self.taggers)
        bookJet(self.tree, 'jet4', self.taggers)
        bookLepton(self.tree, 'lepton')
        bookParticle(self.tree, 'misenergy')
        bookParticle(self.tree, 'higgs')
        bookParticle(self.tree, 'zed')
       
    def process(self, event):
        self.tree.reset()
        misenergy = getattr(event, self.cfg_ana.misenergy)
        fillParticle(self.tree, 'misenergy', misenergy )        
        jets = getattr(event, self.cfg_ana.jets)
        for ijet, jet in enumerate(jets):
            if ijet==4:
                break
            fillJet(self.tree, 'jet{ijet}'.format(ijet=ijet+1), jet, self.taggers)
        higgs = getattr(event, self.cfg_ana.higgs)
        if higgs:
            fillParticle(self.tree, 'higgs', higgs)
        zed = getattr(event, self.cfg_ana.zed)
        if zed:
            fillParticle(self.tree, 'zed', zed)
        
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        

