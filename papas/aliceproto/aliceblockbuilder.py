
import itertools
from PFfloodfill import FloodFill
#import sys
#Get the DAGtool

from DAG import Node, BreadthFirstSearchIterative,DAGFloodfill
from heppy.papas.aliceproto.Identifier import Identifier
from heppy.papas.pfalgo.distance import Distance
 
  
class PFBlock(object):
# Stores a set of nodes that are connected
# together with the edge data for each possible edge con
    def __init__(self, elements,alledges):
        
        self.pfelements = elements
        self.size = len(elements)
        self.edgedata = dict() #make a dictionary
        self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.BLOCK) 
              
        for id1, id2 in itertools.combinations(elements,2):
            key=Edge.makekey(id1,id2)
            self.edgedata[key] =alledges[key]
        print("finished block")       
   
    def countECAL(self):
        count=0
        for elem in self.pfelements:
            count+=Identifier.isECAL(elem)
        return count
    
    def countTrack(self):
            count=0
            for elem in self.pfelements:
                count+=Identifier.isTrack(elem)
            return count    
        
    def countHCAL(self):
            count=0
            for elem in self.pfelements:
                count+=Identifier.isHCAL(elem)
            return count     
        
    def __str__(self):
        return 'COLIN: implement str'

'''
COLIN: how to represent a block? 

block : block id 

elements: 
  T1: track1 printout 
  E1: ecal1 printout 
  ..

links: 
       T1    E1 
  T1   x     dist
  E2         x
  ..

'''

    
      
class Edge(object): #edge information 
    # end nodes, distance and whether they are linked
    ruler = None
    
    def __init__(self, obj1,obj2,id1, id2): #bit clunky
        # make Edge independent of obj1, obj2.
        # set ruler to BlockBuilder instead and measure distance before
        # creating the edge. Edge is just a data holder. 
        self.id1=id1
        self.id2=id2
        #these two will need some unravelling as need to go from the id to the actual cluster or tracks in order to get the distance
        #self.type=self.GetType(e1,e2)
     
       #This is a bodge (sorry) wanted to be able to change the ruler for the test case
       #but has an issue with using the Distance class as the Edge.ruler (nor sure why but I imagine there is a cleaner solution)
        if Edge.ruler==None :
            link_type, link_ok, distance = ruler(obj1,obj2) # for Distance
        else :
            link_type, link_ok, distance = Edge.ruler(obj1,obj2) # eg for DistanceItem for test_reconstructor (need to make into a class like Distance)
        self.distance=distance
        self.link_type=link_type
        self.linked= link_ok
        self.key=Edge.makekey(id1,id2) 
  
    def __str__(self):
        '''
        maybe 
        edge : track id1, ecal id2, distance
        '''
        return 'COLIN : implement str'

    @staticmethod    
    def makekey(id1,id2):
        return hash(tuple(sorted([id1,id2])))

    @staticmethod
    def setRuler(rule) :
        Edge.ruler=staticmethod(rule)
    

        
class BlockBuilder(object):
    '''What is the purpose of the class? 
    describe interface, and in particular what are the 
    important attributes that the user can find in this class
    give a usage example.

    builder = BlockBuilder(tracks, ecal, hcal)
    tell how to use the blocks (code fragment)

    review all methods : pythonic name e.g. make_history_node 
    think about what has to be private or exposed to the user
    same for attributes
    '''
    def __init__(self, tracks, ecal, hcal, histNodes=None, ruler=None):
        '''describe what the method is doing.. here ok because constructor
        describe what is expected for parameters, e.g. dictionary for tracks, ecal
        hcal.
        say also what method is returning.

        tracks is a dictionary : {id1:track1, id2:track2, ...}
        '''

 
        self.tracks=tracks
        self.ecal=ecal
        self.hcal=hcal

        # if the user does not specify an existing history tree,
        # start the tree with the identifiers of the provided tracks,
        # ecal and hcal clusters
        self.historyNodes = histNodes
        if self.historyNodes is None:
            self.historyNodes = dict(
                self._make_dict(tracks).items() + 
                self._make_dict(ecal).items() +
                self._make_dict(hcal).items() )

        # # build the block nodes (separate graph)
        # self.nodes = dict(
        #     self._make_dict(tracks).items() + 
        #     self._make_dict(ecal).items() +
        #     self._make_dict(hcal).items() )
        
        # # compute link properties between each pair of nodes
        # self.edges = dict()
        # for e1, e2 in itertools.combinations(self.nodes,2) :
        #     self.addEdge(e1,e2)        

        # # build blocks
        # self.makeBlocks()

        # # instead of what is below
            
        # edgeNodes -> nodes everywhere, also in method names  
        self.edgeNodes=dict()
        self.blocks = dict()
        # edges
        self.edgedata=dict() 
            
        Edge.setRuler(ruler)
        self.makeEdgeNodes() # -> make_nodes, pythonic name
        self.makeEdges()
        self.makeBlocks()


        
    def _make_dict(self, elems):  # this method is made private by the start _
        '''for a list of identifiers, return a dictionary
        {identifier: Node(identifier)}
        '''
        return dict( (idt, Node(idt)) for idt in elems )
    
    def makeHistoryNode(self, label) :
        '''remove? '''
        self.historyNodes[label]=Node(label)
        
    def makeEdgeNodes(self) :
        #think about using _make_dict in an explicit way 
        #take all of the tracks and clusters and turn them into Nodes
        self.addNodes(self.edgeNodes,self.tracks) 
        self.addNodes(self.edgeNodes,self.ecal)        
        self.addNodes(self.edgeNodes,self.hcal) 
    
    def makeEdges(self) :
        # put this lines in constructor.
        # only couple lines, only intended to be called once 
        for e1, e2 in itertools.combinations(self.edgeNodes,2) :
            self.addEdge(e1,e2)        
        
    def addEdge(self,id1,id2) :
        obj1=self.getObject(id1)
        obj2=self.getObject(id2)
        
        edge=Edge(obj1,obj2,id1,id2) #this is a bit clunky and can likely be improved
        self.edgedata[edge.key] = edge
        if  edge.linked: #TODO this is actually an undirected link - will work for undriected searches 
            self.edgeNodes[id1].add_child(self.edgeNodes[id2])


    def addNodes(self, nodedict,objectdict) :
        for label, thing in objectdict.iteritems() :
            nodedict[label]= Node(label)      
        
    def makeBlocks (self) :
        
        for b in DAGFloodfill(self.edgeNodes).blocks :
            recHistoryElems= [] 
            #NB the nodes that are found by FloodFill are the edgeNodes
            # we acually want the blocks to contain the History nodes (the ones with matching uniqueid)
            #So, find the corresponding history nodes
            for e in b :
                recHistoryElems.append(e.getValue())         

            #now we can make the block
            block=PFBlock(recHistoryElems,  self.edgedata) #pass the edgedata and extract the needed edge links for this block          
            
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] =  block        
            
            #Link the block into the historyNodes
            self.setBlockLinks(block)
                     
    
    def getObject(self, e1) :
        type= Identifier.gettype(e1)
        if type==Identifier.PFOBJECTTYPE.TRACK :
            return self.tracks[e1]       
        elif type==Identifier.PFOBJECTTYPE.ECALCLUSTER :
            return self.ecal[e1] 
        elif type==Identifier.PFOBJECTTYPE.HCALCLUSTER :
            return self.hcal[e1]            
        else :
            assert(False)    
    
    def setBlockLinks(self,block):
        #make a node for the block and add into the history Node
        blocknode=Node(block.uniqueid)
        self.historyNodes[block.uniqueid]=blocknode
        
        #now add in the links between the block elements and the block into the historyNodes
        for elemid in block.pfelements:
            self.historyNodes[elemid].add_child(blocknode)

  
#alice todo improve?
ruler = Distance()
 
