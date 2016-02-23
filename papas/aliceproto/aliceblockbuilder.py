
import itertools
from PFfloodfill import FloodFill
from enum import Enum
#import sys
#Get the DAGtool

from DAG import Node, BreadthFirstSearchIterative,DAGFloodfill
from heppy.papas.aliceproto.Identifier import Identifier
from heppy.papas.pfalgo.distance import Distance
 
class Event(object):
    def __init__(self):
        self.simParticles=dict()
        self.recParticles=dict()
        self.ECALclusters=dict()
        self.HCALclusters=dict()
        self.tracks=dict()           #tracks to be used in reconstruction
        self.historyNodes=dict()  #Nodes used in simulation/reconstruction (contain uniqueid)
        #self.recHistoryNodes=dict() #Nodes used in reconstruction (contain uniqueid)
        self.edgeNodes=dict()     #Contains Edge distances between nodes
        
        #dictionary with uniqueids
        self.blocks=dict()           #Blocks made in reconstuction
        #self.edgedata=dict() 
    

def MergeNodes (Nodes1 , Nodes2) :
    
    for label, node in Nodes2.iteritems() :
        found=False
        if Nodes1.find(label) :
            Nodes1[label].UpdateNode(node)

          

    


class BlockBuilder(object):
    def __init__(self,tracks, ecal, hcal,histNodes=dict(),ruler=None):
        self.tracks=tracks
        self.ecal=ecal
        self.hcal=hcal
        self.edgeNodes=dict()
        self.historyNodes=histNodes
        self.blocks = dict()
        self.edgedata=dict() 
        
        if len(self.historyNodes)==0 :
            self.makeHistoryNodes(tracks)    
            self.makeHistoryNodes(ecal)
            self.makeHistoryNodes(hcal)
        
        Edge.setRuler(ruler)
        self.makeEdgeNodes()
        self.makeEdges()
        self.makeBlocks()  
    
    def makeHistoryNodes(self, dictcollection) :
        for label, thing in dictcollection.iteritems() :
            self.historyNodes[label]=Node(label )       
        
    def makeHistoryNode(self, label) :
        self.historyNodes[label]=Node(label)
        
    def makeEdgeNodes(self) :
        #take all of the tracks and clusters and turn them into Nodes
        self.addNodes(self.edgeNodes,self.tracks) 
        self.addNodes(self.edgeNodes,self.ecal)        
        self.addNodes(self.edgeNodes,self.hcal) 
    
    def makeEdges(self) :
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
       
class Edge(object): #edge information 
    # end nodes, distance and whether they are linked
    ruler = None
    
    def __init__(self, obj1,obj2,id1, id2): #bit clunky
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
      
#    def GetType(self,e1,e2):
        #type=PFDISTANCEtype(e1.type.value +e2.type.value)
 #       return(type)
    
    @staticmethod    
    def makekey(id1,id2):
        return hash(tuple(sorted([id1,id2])))

    @staticmethod
    def setRuler(rule) :
        Edge.ruler=staticmethod(rule)
    
   
    
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
        




