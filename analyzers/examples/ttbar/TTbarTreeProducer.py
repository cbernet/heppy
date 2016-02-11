from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class TTbarTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TTbarTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        bookParticle(self.tree, 'jet1')
        bookParticle(self.tree, 'jet2')
        bookParticle(self.tree, 'jet3')
        bookParticle(self.tree, 'm3')
        bookMet(self.tree, 'met')
        bookLepton(self.tree, 'lepton')
        
    def process(self, event):
        self.tree.reset()
        leptons = getattr(event, self.cfg_ana.leptons)
        if len(leptons)==0:
            return # NOT FILLING THE TREE IF NO LEPTON
        fillLepton(self.tree, 'lepton', leptons[0])
        jets = getattr(event, self.cfg_ana.jets)
        for ijet, jet in enumerate(jets):
            if ijet==3:
                break
            fillParticle(self.tree, 'jet{ijet}'.format(ijet=ijet+1), jet)
        m3 = getattr(event, self.cfg_ana.m3)
        if m3: 
            fillParticle(self.tree, 'm3', m3)
        met = getattr(event, self.cfg_ana.met)
        fillMet(self.tree, 'met', met)
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
