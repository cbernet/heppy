from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class HiggsTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(HiggsTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( self.cfg_ana.tree_name,
                          self.cfg_ana.tree_title )
        bookZed(self.tree, 'ztomumu')
        bookZed(self.tree, 'higgstojj')
 

    def process(self, event):
        self.tree.reset()
        if len(event.ztomumu):
            fillZed(self.tree, 'ztomumu', event.ztomumu[0])
        if len(event.higgstojj):
            fillZed(self.tree, 'higgstojj', event.higgstojj[0])
        self.tree.tree.Fill()
        
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
