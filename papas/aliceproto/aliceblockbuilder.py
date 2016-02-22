import unittest
import itertools
from PFfloodfill import FloodFill
from enum import Enum
#import sys
#Get the DAGtool
from distance import Distance
from DAG import Node, BreadthFirstSearchIterative,DAGFloodfill

 
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
    
    for node in Nodes2 :
        
        if Nodes1.find(node) :
            UpdateNode(Nodes1[node],Nodes2[node])

          
    
class Simulator(object):
    def __init__(self,event):
        self.event=event
       
        #add some partiles
        self.addECALCluster(101)
        self.addHCALCluster(202)
        self.addECALCluster(102)
        self.addECALCluster(103)
        self.addTrack(1)
        self.addTrack(2)
        self.addParticle(301,211) #charged hadron
        self.addParticle(302,211) #charged hadron
        self.addParticle(303,22)  #photon
        self.addLink(301,101)
        self.addLink(301,1)
        self.addLink(302,2)
        self.addLink(302,102)
        self.addLink(302,202)
        self.addLink(303,103)
        
        
              
    def addECALCluster(self, uniqueid) :
        clust=Cluster(uniqueid,PFType.ECAL)         # make a cluster
        self.event.ECALclusters[uniqueid]=clust     # add into the collection of clusters
        self.event.historyNodes[uniqueid]= Node(uniqueid)  #add into the collection of History Nodes
                 
    def addHCALCluster(self, uniqueid) :
        clust=Cluster(uniqueid,PFType.HCAL)
        self.event.HCALclusters[uniqueid]=clust
        self.event.historyNodes[uniqueid]= Node(uniqueid)
        
    def addTrack(self, uniqueid) :
        track=Track(uniqueid)
        self.event.tracks[uniqueid]= track
        self.event.historyNodes[uniqueid]= Node(uniqueid) 
        
    def addParticle(self, uniqueid,pdgid) :
        particle=Particle(uniqueid,pdgid)
        self.event.simParticles[uniqueid]= particle
        self.event.historyNodes[uniqueid]= Node(uniqueid) 
    
                
    def addLink(self, uniqueid1, uniqueid2) :
        self.event.historyNodes[uniqueid1].add_child(self.event.historyNodes[uniqueid2])
        
    
def isECAL (val):
    return val-val%100==100
    
def isHCAL (val):
    return val-val%100==200
    
def isTrack (val):
    return val-val%100==0

def isBlock (val):
    return val-val%100==400
        
def isSimParticle (val):
    return val-val%100==300

def isRecParticle (val):
    return val-val%100==600
         
        
class Reconstructor(object):
    def __init__(self,event):
        self.event = event 
        self.particlecount = 600 #used to create reconstructed particle uniqueid
        #find sets of connected nodes and make a block
        #event.makeEdgeNodes() #make a node for each track and cluster to be used for making edge info
        #event.makeEdges()     #calculate the edge distances        
        #self.makeBlocks()  
        self.reconstructParticles()
    
    def addNodes(self, nodedict,values) :
        for e1 in values :
            nodedict[e1.uniqueid]= Node(e1.uniqueid)            

          
    
    def reconstructParticles (self) :
        for block in self.event.blocks.itervalues() :
            self.makeParticlesFromBlock (block)    
    
    def makeParticlesFromBlock(self,block):
        #take a block and find its parents (clusters and tracks)
        parents=block.pfelements
        
        if  (len(parents)==1) & (isECAL(parents[0])) :
            self.makePhoton(parents)
            print "made photon"
            
           
        elif ( (len(parents)==2)  & (block.countECAL()==1 ) & (block.countTrack()==1)) :
                self.makeHadron(parents)
                print "made hadron" 
                
           #I am not sure if this is OK, what if a block contains two indep particles         
        elif  ((len(parents)==3)  & (block.countECAL()==1) & (block.countTrack()==1) & (block.countHCAL()==1)) :
                print "made hadron and photon"
                #might need to break down parents
                
                
                #proba not right but illustrates splitting of parents
                hparents=[]
                for elem in parents:
                    if (isHCAL(elem)) :
                        self.makePhoton({elem})
                    else :
                        hparents.append(elem)    
                    
    
                self.makeHadron(hparents)
                
            #makeChargedHadron(block.ECAls[0].getValue(),block.tracks[0].getValue())
        else :
            print "particle TODO"  
         
    def makePhoton(self,parents) :
        return self.addParticle(self.newUniqueID(), 22,parents)

    def makeHadron(self,parents) :
        return self.addParticle(self.newUniqueID(), 211,parents)

    def addParticle(self, uniqueid,pdgid,parents) :
        particle=recParticle(uniqueid,pdgid)
        self.event.recParticles[uniqueid]= particle
        particleNode=Node(uniqueid)
        self.event.historyNodes[uniqueid]= particleNode
        for parent in parents :
            self.event.historyNodes[parent].add_child(particleNode)
        
    def newUniqueID(self):
        uniqueid=self.particlecount
        self.particlecount+=1
        return uniqueid
    


class BlockBuilder(object):
    def __init__(self,tracks, ecal, hcal):
        self.tracks=tracks
        self.ecal=ecal
        self.hcal=hcal
        self.edgeNodes=dict()
        self.historyNodes=dict()
        self.blocks = dict()
        self.edgedata=dict() 
        
        self.makeHistoryNodes(tracks)    
        self.makeHistoryNodes(ecal)
        self.makeHistoryNodes(hcal)
        
        self.makeEdgeNodes()
        self.makeEdges()
        self.makeBlocks()  
        
    
    
    #maybe not in right place yet
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

    def getObject(self, e1) :
        if e1[0]==0:
            return self.tracks[e1]       
        if e1[0]==1:
            return self.ecal[e1] 
        elif e1[0]==2:
            return self.hcal[e1] 
        else :
            assert(false)
           
    def addEdge(self,e1,e2) :
        obj1=self.getObject(e1)
        obj2=self.getObject(e2)
        
        edge=Edge(obj1,obj2,e1[1],e2[1])
        self.edgedata[edge.key] = edge
        if  edge.linked: #TODO this is not quite right as the link is not directed but we are using a directed graph
                # This could mean that there are loops in the DAG
            self.edgeNodes[e1].add_child(self.edgeNodes[e2])

#def addNodes(self, nodedict,values) :
  #      for e1 in values :
   #         nodedict[e1.uniqueid]= Node(e1.uniqueid)        
    
    def addNodes(self, nodedict,objectdict) :
        for label, thing in objectdict.iteritems() :
            nodedict[label]= Node(label)      
        
    def makeBlocks (self) :
        uniqueid=400
        for b in DAGFloodfill(self.edgeNodes).blocks :
            recHistoryElems= [] 
            #NB the nodes that are found by FloodFill are the edgeNodes
            # we acually want the blocks to contain the History nodes (but with same uniqueid)
            #So, find the corresponding history nodes
            for e in b :
                recHistoryElems.append(e.getValue())
                #recHistoryElems[e.getValue()] = e.getValue() #not sure about this          

            #now we can make the block
            block=PFBlock(recHistoryElems, uniqueid, self.edgedata) #pass the edgedata and extract the needed edge links for this block          
            
            #put the block in the dict of blocks            
            self.blocks[uniqueid] =  block        
            
            #Linkthe block into the historyNodes
            self.setBlockLinks(block)
            uniqueid+=1           
    
    
        
    def newUniqueID(self):
        uniqueid=self.particlecount
        self.particlecount+=1
        return uniqueid
    
    def setBlockLinks(self,block):
        #make a node for the block
        blocknode=Node(block.uniqueid)
        self.historyNodes[block.uniqueid]=blocknode
        for elemid in block.pfelements:
            self.historyNodes[elemid].add_child(blocknode)

  
#alice todo
ruler=Distance()    
       
class Edge(object): #edge information 
    # end nodes, distance and whether they are linked
    def __init__(self, e1, e2,id1,id2):
        self.e1=e1
        self.e2=e2
        #these two will need some unravelling as need to go from the id to the actual cluster or tracks in order to get the distance
        #self.type=self.GetType(e1,e2)
        link_type, link_ok, distance = ruler(e1, e2)
        self.distance=distance
        self.link_type=link_type
        self.linked= link_ok
        self.key=Edge.makekey(id1,id2) 
        print id1, id2, self.key
      
    def GetType(self,e1,e2):
        type=PFDISTANCEtype(e1.type.value +e2.type.value)
        return(type)
    
    @staticmethod    
    def makekey(id1,id2):
        return hash(tuple(sorted([id1,id2])))
    
       
    
class PFBlock(object):
# Stores a set of nodes that are connected
# together with the edge data for each possible edge
# call edgevec edgedata
    def __init__(self, elements,uniqueid,alledges):
        
        self.pfelements = elements
        self.size = len(elements)
        self.edgedata = dict() #make a dictionary
        self.uniqueid=uniqueid #not too sophisticated
        
        
        for e1, e2 in itertools.combinations(elements,2):
            key=Edge.makekey(e1[1],e2[1])
            self.edgedata[key] =alledges[key]
        print("finished block")       
   
    def countECAL(self):
        count=0
        for elem in self.pfelements:
            count+=isECAL(elem)
        return count
    
    def countTrack(self):
            count=0
            for elem in self.pfelements:
                count+=isTrack(elem)
            return count    
        
    def countHCAL(self):
            count=0
            for elem in self.pfelements:
                count+=isHCAL(elem)
            return count     
        
class Cluster(object):
    def __init__(self, uniqueid, type):
        self.uniqueid=uniqueid
        self.type=type
        
class Track(object):
    def __init__(self, uniqueid):
        self.uniqueid=uniqueid
        self.type=PFType.TRACK

class Particle(object):
    def __init__(self, uniqueid,pdgid):
        self.uniqueid=uniqueid
        self.pdgid=pdgid
        self.type=PFType.PARTICLE
        
class recParticle(Particle):
    def __init__(self, uniqueid,pdgid):
        self.uniqueid=uniqueid
        self.pdgid=pdgid
        self.type=PFType.RECPARTICLE

class PFType(Enum):
    NONE = 0
    TRACK = 1
    ECAL = 2
    HCAL = 4
    PARTICLE=8
    RECPARTICLE=16
    
class PFDISTANCEtype(Enum):
    NONE = 0
    TRACK_TRACK = 2
    TRACK_ECAL = 3
    ECAL_ECAL = 4
    TRACK_HCAL=5
    ECAL_HCAL = 6
    HCAL_HCAL=8
           
    
def DistanceItem(el1, el2):
    return (abs(el1%100 -el2%100))
         
        
class TestFloodFill(unittest.TestCase):
    
        
    def test_1(self):
        
        event = Event()
        sim = Simulator(event)
        pfblocker=BlockBuilder(event.tracks, event.ECALclusters,event.HCALclusters )
        event.blocks=pfblocker.blocks
        event.historyNodes=pfblocker.historyNodes
        rec = Reconstructor(event)

        
        # What is connected to HCAL 202 node?
        #  (1) via historyNodes
        #  (2) via reconstructed RecHistoryNode
        #  (3) via reconstructed node links
        nodeid=202
        
        #(1)
        ids=[]
        BFS = BreadthFirstSearchIterative(event.historyNodes[nodeid],"undirected")
        for n in BFS.result :
            ids.append(n.getValue())
        ids =sorted(ids)
        self.assertEqual(sorted(ids), [2, 102,202,401,601,602])
        
        x=None
        for id in ids:
            if isBlock(id) :
                x=event.blocks[id]
                print "Block " + str(id)
        ids=[]        
    
        for n in x.pfelements:
            print (n)
            ids.append(n)
        self.assertEqual(ids, [2,102,202])
        
        
        #(2) No longer needed
        #ids=[]
        #BFS = BreadthFirstSearchIterative(event.recHistoryNodes[nodeid],"undirected")
        #for n in BFS.result :
            #ids.append(n.getValue())
        #self.assertEqual(ids, [202,401,2,102])   
        
        #(3)
        ids=[]
        BFS = BreadthFirstSearchIterative(pfblocker.edgeNodes[nodeid],"undirected")
        for n in BFS.result :
            ids.append(n.getValue())
        self.assertEqual(ids, [202,2,102])
        
        # Give me all blocks with  one track:
        blockids=[]
        for b in event.blocks.itervalues() :
            if b.countTrack()==1 : 
                blockids.append(b.uniqueid)
                print "Block with 1 TRACK: " + str(b.uniqueid);
        
        # Give me all simulation particles attached to each reconstructed particle
        for rp in event.recParticles :
            BFS = BreadthFirstSearchIterative(event.historyNodes[rp],"parents")
            print "Rec particle: ", event.recParticles[rp].pdgid, " from "            
            for n in BFS.result :
                if (isSimParticle(n.getValue())) :
                    ids.append(n.getValue())
                    print "      sim particle: ", event.simParticles[n.getValue()].pdgid 
                
        # Give me all rec particles attached to each sim particle
       # for rp in event.simParticles :
       #     BFS = BreadthFirstSearchIterative(event.historyNodes[rp],"children")
       #     print
       #     print "Sim particle: ", event.simParticles[rp].pdgid, " gives "            
       #     for n in BFS.result :
       ##         #print n
       ##         if (isRecParticle(n.getValue())) :
       #             ids.append(n.getValue())
       #             print "     rec particle: ", event.recParticles[n.getValue()].pdgid 

                
                
                
        print("end")
        
if __name__ == '__main__':        
    unittest.main()



