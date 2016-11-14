'''Test analyzer creating a simple root tree.'''

from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from ROOT import TFile

class SimpleTreeProducer(Analyzer):
    '''Test analyzer creating a simple root tree.
    
    Example::
    
        tree = cfg.Analyzer(
          SimpleTreeProducer,
          tree_name = 'events',
          tree_title = 'A simple test tree'
        )
    
    The TTree is written to the file C{simple_tree.root} in the analyzer directory.
    
    @param tree_name: Name of the tree (Key in the output root file).
    @param tree_title: Title of the tree.
    '''
    def beginLoop(self, setup):
        super(SimpleTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'simple_tree.root']),
                              'recreate')
        self.tree = Tree( self.cfg_ana.tree_name,
                          self.cfg_ana.tree_title )
        self.tree.var('test_variable')
        self.tree.var('test_variable_random')

    def process(self, event):
        '''Process the event.
        
        The input data must contain a variable called "var1",
        which is the case of the L{test tree<heppy.utils.testtree>}. 
        
        The event must contain:
         - var_random, which is the case if the L{RandomAnalyzer<heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer>}
         has processed the event. 
         
        '''
        self.tree.fill('test_variable', event.input.var1)
        self.tree.fill('test_variable_random', event.var_random)
        self.tree.tree.Fill()

    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
