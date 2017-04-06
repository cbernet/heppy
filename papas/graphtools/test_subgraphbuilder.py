from edge import Edge
from subgraphbuilder import SubgraphBuilder
import unittest 

class TestSubgraphBuilder( unittest.TestCase ):

    def setUp(self):
        '''
        called before every test. Makes this structure:
 
           1--3
          / 
         /   
        0--2  
         
        4--5
        

    '''
    # create some ids and edges
        '''
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance/link between two ids
        '''
        #subgroup 0
        self.ids = range(0, 7)
        self.edges = dict()
        edge = Edge(0, 1, True, 0)
        self.edges[edge.key] = edge
        edge = Edge(0, 2, True, 0)
        self.edges[edge.key] = edge
        edge = Edge(1, 3, True, 0)
        self.edges[edge.key] = edge        
        edge = Edge(0, 1, True, 0)
        self.edges[edge.key] = edge
        
        #subgroups 1
        edge = Edge(4, 5, True, 0)
        self.edges[edge.key] = edge
        edge = Edge(5, 6, True, 0)
        self.edges[edge.key] = edge        
        
    
    
    def test_graph(self):
        subgraphbuilder = SubgraphBuilder(self.ids, self.edges)
        subgraphs = subgraphbuilder.subgraphs
        #test we get back 2 subgroups
        self.assertEqual(len(subgraphs), 2 )
        
        #test the subgroups are the right sizes
        sortedsubgraphs = sorted(subgraphs, key = lambda x: len(x))
        self.assertEqual(len(sortedsubgraphs[1]), 4 )
        

if __name__ == '__main__':
    unittest.main()
