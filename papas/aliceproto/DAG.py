import pprint
import unittest 
from collections import deque

'''PolyTree with full visitor pattern and breadth first traversal algorithms

The PolyTree is directed and acyclic. Each node may have several children. 
Each node may have several parents. The polytree may have multiple roots ( a node without a parent)
It has no loops when directed, but may have loops when traversed in an undirected way

Traversals
1: deal with all nodes at the same level and then with all children of these nodes etc (breadth-first search or BFS)
2: deal with all children and finally with the node (depth-first search of DFS)  

A visitor pattern is used to allow the algorithms to be separated from the object 
on which it operates and without modifying the objects structures (eg a visited flag can be 
owned by the algorithm)

The visitor pattern also allows the visit method to dynamically depend on both  the object and the visitor
'''


class Node(object):
    '''
    Implements a polytree: 
    each node has an arbitrary number of children and parents
    There are no loops in the directed polytree
    But there may be loops in the undirected polytree
    '''
    
    def __init__(self, value):
        '''constructor. 
        value can be anything, even a complex object. 
        '''
        self.value = value   # wrapped object
        self.children = []
        self.parents = []
        self.undirectedlinks = [] #the union of the parents and children (other implementations possible)
        

    def getValue(self):
        return self.value
    
    def accept(self, visitor):
        visitor.visit(self)
             
    def add_child(self, child):
        '''set the children'''
        self.children.append(child)
        child.add_parent(self)
        self.undirectedlinks.append(child)

    def add_parent(self, parent):
        '''set the parents'''
        self.parents.append(parent)
        self.undirectedlinks.append(parent)

    def get_linked_nodes(self, type):  #ask colin, I imagine there is a more elegant Python way to do this
        if (type is "children"):
            return self.children
        if(type is "parents"):
            return self.parents
        if(type is "undirected"):
            return self.undirectedlinks

    def __repr__(self):
        '''unique string representation'''
        
        return str('node: {val} {children}'.format(
            val = self.value,
            children=self.children
            ) )



class BreadthFirstSearch(object):
    
    def __init__(self,root, linktype):
        '''Perform the breadth first recursive search of the nodes'''
        self.result=[]
        self.visited=dict()
        self.bfs_recursive([root],linktype)
        
    def visit(self, node):
        if self.visited.get(node, False):
            return
        self.result.append( node.getValue() )
        self.visited[node]=True
             
    def bfs_recursive(self,nodes, linktype ):
        '''Breadth first recursive implementation
        each recursion is one level down the tree
        linktype can be "children", "parents","undirected" '''
        linknodes=[]
        if len(nodes) is 0:
            return 
        
        for node in nodes: # collect a list of all the next level of nodes
            if (self.visited.get(node, False)):  
                continue              
            linknodes.extend(node.get_linked_nodes(linktype))        
        for node in nodes: #add these nodes onto list and mark as visited
            if (self.visited.get(node, False)):  
                continue            
            node.accept(self)
        
        self.bfs_recursive(linknodes,  linktype)

          
class BreadthFirstSearchIterative(object):
    
    def __init__(self,root, linktype):
        '''Perform the breadth first iterative search of the nodes'''
        self.visited={}
        self.result=[]
        self.bfs_iterative(root,linktype)       

    def visit(self, node):
        if self.visited.get(node, False):
            return
        self.result.append( node )
        self.visited[node]=True
        

        
    def bfs_iterative(self,node, linktype ):
        '''Breadth first iterative implementation
        using a deque to order the nodes 
        linktype can be "children", "parents","undirected" '''
            
        # Create a deque for the Breadth First Search
        todo = deque()
        todo.append( node)
        
        while len(todo):
            node = todo.popleft()
            if self.visited.get(node,False): #check if already processed
                continue
            node.accept(self)
            for linknode in node.get_linked_nodes(linktype):
                if self.visited.get(linknode,False): #check if already processed
                    continue
                todo.append( linknode)  
                
                
class DAGFloodfill(object):
    
    def __init__(self,elements,first_label=1):
        '''Use Breadth first search to find connected groups'''
        self.visited={}
        self.label = first_label
        self.visited = dict()
        self.blocks = []
        for uid, node in elements.iteritems():
                if self.visited.get(node, False): #already done so skip the rest
                    continue
                
                #find connected nodes
                bfs=BreadthFirstSearchIterative(node,"undirected")
                
                # set all connected elements to have a visited flag =true
                for n in bfs.result :
                    self.visited.update({n: True})
                #add into the set of blocks
                self.blocks.append( bfs.result)
                self.label += 1
        
        
      
            

class TreeTestCase( unittest.TestCase ):

    def setUp(self):
        '''
        called before every test. 
        0 and 8 are root/head nodes
    
    
        8
         \
          \
           9
            \
             \
              4  
             /  
            /  
           1--5--7
          / \
         /   \
        0--2  6
         \   /
          \ /
           3

    '''
    # building all nodes
        self.nodes = dict( (i, Node(i) ) for i in range(10) )
    
        self.nodes[0].add_child(self.nodes[1])
        self.nodes[0].add_child(self.nodes[2])
        self.nodes[0].add_child(self.nodes[3])
        self.nodes[1].add_child(self.nodes[4])
        self.nodes[1].add_child(self.nodes[5])
        self.nodes[1].add_child(self.nodes[6])
        self.nodes[5].add_child(self.nodes[7])
        self.nodes[8].add_child(self.nodes[9])
        self.nodes[9].add_child(self.nodes[4])
        self.nodes[3].add_child(self.nodes[6])
    
               
        
    def test_BFS_visitor_pattern_iterative_undirected(self):
        BFS = BreadthFirstSearchIterative(self.nodes[0],"undirected")
        # the result is equal to [0, 1, 2, 3, 4, 5, 6, 9, 7, 8]
        self.assertEqual(BFS.result, [0, 1, 2, 3, 4, 5, 6, 9, 7, 8] )
        
    def test_BFS_visitor_pattern_children(self):
        BFS = BreadthFirstSearch(self.nodes[0],"children")
          # the result is equal to [0, 1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(BFS.result, range(8) )

    def test_BFS_visitor_pattern_undirected(self):
            
        BFS = BreadthFirstSearch(self.nodes[0],"undirected")
        # the result is equal to [0, 1, 2, 3, 4, 5, 6, 9, 7, 8]
        self.assertEqual(BFS.result, [0, 1, 2, 3, 4, 5, 6, 9, 7, 8] )
    
   
if __name__ == '__main__':
    unittest.main()
