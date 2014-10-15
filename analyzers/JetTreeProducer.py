from framework.analyzer import Analyzer
from statistics.tree import Tree
from analyzers.ntuple import *

from ROOT import TFile

class JetTreeProducer(Analyzer):

    def beginLoop(self):
        super(JetTreeProducer, self).beginLoop()
        self.rootfile = TFile('/'.join([self.dirName,
                                        'jet_tree.root']),
                              'recreate')
        self.tree = Tree( self.cfg_ana.tree_name,
                          self.cfg_ana.tree_title )
        bookJet(self.tree, 'jet1')
        bookJet(self.tree, 'jet2')
        bookLepton(self.tree, 'lep1')
        
    def process(self, event):
        if( len(event.jets)>0 ):
            fillJet(self.tree, 'jet1', event.jets[0])
        if( len(event.jets)>1 ):
            fillJet(self.tree, 'jet2', event.jets[1])
        if( hasattr(event, 'leptons') and len(event.leptons)>0 ):
            fillLepton(self.tree, 'lep1', event.leptons[0])
        self.tree.tree.Fill()
        
        
    def write(self):
        self.rootfile.Write()
        self.rootfile.Close()
        
