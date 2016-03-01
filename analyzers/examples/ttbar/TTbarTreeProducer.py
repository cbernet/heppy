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
        bookParticle(self.tree, 'jet4')
        bookParticle(self.tree, 'm3')
        bookMet(self.tree, 'met')
        bookLepton(self.tree, 'muon')
        bookLepton(self.tree, 'electron')

    def process(self, event):
        self.tree.reset()
        muons = getattr(event, self.cfg_ana.muons)        
        electrons = getattr(event, self.cfg_ana.electrons)

        if len(muons)==0 and len(electrons)==0:
            return # NOT FILLING THE TREE IF NO

        if len(muons)==1 and len(electrons)==0:
            fillLepton(self.tree, 'muon', muons[0])

        elif len(electrons)==1 and len(muons)==0:
            fillLepton(self.tree, 'electron', electrons[0])

        else:
            return # NOT FILLING THE TREE IF MORE THAN 1 LEPTON

        jets = getattr(event, self.cfg_ana.jets_30)
        if len(jets)<3:
            return # NOT FILLING THE TREE IF LESS THAN 4 JETS
        for ijet, jet in enumerate(jets):
            if ijet==4:
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
        
