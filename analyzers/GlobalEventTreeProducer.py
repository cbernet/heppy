'''Fill tree for global event quantities.'''

from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class GlobalEventTreeProducer(Analyzer):
    '''Manages an ouput tree for global event quantities.
    
    variables in the tree: 
     - sum_all: sum p4 of all particles
     - sum_all_gen: sum p4 of all stable generated particles
    
    other global event quantities can be added as needed
    '''

    def beginLoop(self, setup):
        '''create the output root file and book the tree.
        '''
        super(GlobalEventTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        bookJet(self.tree, 'sum_all')
        bookJet(self.tree, 'sum_all_gen')
      
    def process(self, event):
        '''process event
        
        event must contain:
         - self.cfg_ana.sum_all: collection of all particles.
         - self.cfg_ana.sum_all_gen: collection of all gen particles.
         
        '''
        self.tree.reset()
        sum_all = getattr(event, self.cfg_ana.sum_all)
        sum_all_gen = getattr(event, self.cfg_ana.sum_all_gen)
        fillJet(self.tree, 'sum_all', sum_all)
        fillJet(self.tree, 'sum_all_gen', sum_all_gen)
        self.tree.tree.Fill()
        
    def write(self, setup):
        '''write root file.
        '''
        self.rootfile.Write()
        self.rootfile.Close()
        
