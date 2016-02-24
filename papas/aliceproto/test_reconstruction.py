import unittest
from DAG import Node, BreadthFirstSearchIterative,DAGFloodfill
from heppy.papas.aliceproto.Identifier import Identifier
from aliceblockbuilder import Edge
from aliceblockbuilder import BlockBuilder
from aliceblockbuilder import Event
from aliceblockbuilder import PFBlock as realPFBlock
from enum import Enum

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
        self.addLink(self.UID(301),self.UID(101))
        self.addLink(self.UID(301),self.UID(1))
        self.addLink(self.UID(302),self.UID(2))
        self.addLink(self.UID(302),self.UID(102))
        self.addLink(self.UID(302),self.UID(202))
        self.addLink(self.UID(303),self.UID(103))
              
    def addECALCluster(self, id) :
        clust=Cluster(id,'ecal_in')# make a cluster
        uniqueid=clust.uniqueid 
        self.event.ECALclusters[uniqueid]=clust     # add into the collection of clusters
        self.event.historyNodes[uniqueid]= Node(uniqueid)  #add into the collection of History Nodes
                 
    def addHCALCluster(self, id) :
        clust=Cluster(id,'hcal_in')
        uniqueid=clust.uniqueid 
        self.event.HCALclusters[uniqueid]=clust
        self.event.historyNodes[uniqueid]= Node(uniqueid)
        
    def addTrack(self, id) :
        track=Track(id)
        uniqueid=track.uniqueid 
        self.event.tracks[uniqueid]= track
        self.event.historyNodes[uniqueid]= Node(uniqueid) 
        
    def addParticle(self, id,pdgid) :
        particle=Particle(id,pdgid)
        uniqueid=particle.uniqueid
        self.event.simParticles[uniqueid]= particle
        self.event.historyNodes[uniqueid]= Node(uniqueid) 
    
    def UID(self,id): #Takes the test case short id and find the unique id
        for h in self.event.historyNodes :
            obj=self.getObject(h)
            if hasattr(obj, "id") :
                if obj.id ==id :
                    return obj.uniqueid 
        return 0
     
    def shortID(self,uniqueid): #Takes the test case short id and find the unique id
        for h in self.event.historyNodes :
            obj=self.getObject(h)
            if hasattr(obj, "id") :
                if obj.uniqueid ==uniqueid :
                    return obj.id 
        return 0               

    def addLink(self, uniqueid1, uniqueid2) :
        self.event.historyNodes[uniqueid1].add_child(self.event.historyNodes[uniqueid2])
        
    def getObject(self, e1) :
        type= Identifier.gettype(e1)
        if type==Identifier.PFOBJECTTYPE.TRACK :
            return self.event.tracks[e1]       
        elif type==Identifier.PFOBJECTTYPE.ECALCLUSTER :      
            return self.event.ECALclusters[e1] 
        elif type==Identifier.PFOBJECTTYPE.HCALCLUSTER :            
            return self.event.HCALclusters[e1]            
        elif type==Identifier.PFOBJECTTYPE.PARTICLE :
            return self.event.simParticles[e1]   
        elif type==Identifier.PFOBJECTTYPE.RECPARTICLE :
            return self.event.recParticles[e1]               
        elif type==Identifier.PFOBJECTTYPE.BLOCK :
            return self.event.blocks[e1]               
        else :
            assert(False)    
    
                 
        
class Reconstructor(object):
    def __init__(self,event):
        self.event = event 
        self.particlecount = 600 #used to create reconstructed particle uniqueid
         
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
        
        
        #print block.countECAL(), block.countTrack(),block.countHCAL()
        
        if  (len(parents)==1) & (Identifier.isECAL(parents[0])) :
            self.makePhoton(parents)
            print "made photon"
            
           
        elif ( (len(parents)==2)  & (block.countECAL()==1 ) & (block.countTrack()==1)) :
                self.makeHadron(parents)
                print "made hadron" 
                
        elif  ((len(parents)==3)  & (block.countECAL()==1) & (block.countTrack()==1) & (block.countHCAL()==1)) :
                print "made hadron and photon"
                
                #probably not right but illustrates splitting of parents
                hparents=[] # will contain parents for the Hadron
                for elem in parents:
                    if (Identifier.isHCAL(elem)) :
                        self.makePhoton({elem})
                    else :
                        hparents.append(elem)    
                    
                self.makeHadron(hparents)
    
        else :
            print "particle TODO"  
         
    def makePhoton(self,parents) :
        return self.addParticle(self.newID(), 22,parents)

    def makeHadron(self,parents) :
        return self.addParticle(self.newID(), 211,parents)

    def addParticle(self, id,pdgid,parents) :
        particle=recParticle(id,pdgid)
        self.event.recParticles[particle.uniqueid]= particle
        particleNode=Node(particle.uniqueid)
        self.event.historyNodes[particle.uniqueid]= particleNode
        for parent in parents :
            self.event.historyNodes[parent].add_child(particleNode)
        
    def newID(self):
        id=self.particlecount
        self.particlecount+=1
        return id

class Cluster(object):
    def __init__(self, id, layer):
        if (layer=='ecal_in') :
            self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.ECALCLUSTER)
        elif (layer=='hcal_in') :
            self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.HCALCLUSTER)
        else:
            assert false
        self.layer=layer
        self.id=id
        
class Track(object):
    def __init__(self, id):
        self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.TRACK)
        self.id=id
        self.layer='tracker'

class Particle(object):
    def __init__(self, id,pdgid):
        self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.PARTICLE)
        self.pdgid=pdgid
        self.id=id
        #self.type=PFType.PARTICLE
        
class recParticle(Particle):
    def __init__(self, id,pdgid):
        self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.RECPARTICLE)
        self.pdgid=pdgid
        self.id=id
        #print id
        #self.type=PFType.RECPARTICLE



#class PFType(Enum):
    #NONE = 0
    #TRACK = 1
    #ECAL = 2
    #HCAL = 4
    #PARTICLE=8
    #RECPARTICLE=16
    
#class PFDISTANCEtype(Enum):
    #NONE = 0
    #TRACK_TRACK = 2
    #TRACK_ECAL = 3
    #ECAL_ECAL = 4
    #TRACK_HCAL=5
    #ECAL_HCAL = 6
    #HCAL_HCAL=8
           
    
def DistanceItem(obj1,obj2): #simple distance uses the short ids
    distance=abs(obj1.id%100 -obj2.id%100)
    return  None, distance==0, distance
         
        
class TestFloodFill(unittest.TestCase):
    
        
    def test_1(self):
        
        event = Event()
        sim = Simulator(event)
        
        pfblocker=BlockBuilder(event.tracks, event.ECALclusters,event.HCALclusters,event.historyNodes,ruler=DistanceItem)
        
        event.blocks=pfblocker.blocks
        event.historyNodes=pfblocker.historyNodes
       
        rec = Reconstructor(event)

        
        # What is connected to HCAL 202 node?
        #  (1) via historyNodes
        #  (2) via reconstructed node links
        #  (3) Give me all blocks with  one track:
        #  (4) Give me all simulation particles attached to each reconstructed particle
        nodeid=202
        nodeuid=sim.UID(nodeid)
        
        #(1) what is connected to the the HCAL CLUSTER
        ids=[]
        BFS = BreadthFirstSearchIterative(event.historyNodes[nodeuid],"undirected")
        for n in BFS.result :
            ids.append(n.getValue())
         
        #1b WHAT BLOCK Does it belong to   
        x=None
        for id in ids:
            if Identifier.isBlock(id) :
                x=event.blocks[id]
                print "Block " + str(id) 
                
        #1c what else is in this block        
        pids=[] 
        for n in x.pfelements:
                    print (n)
                    pids.append(n)            
        #check that the block contains the expected list of suspects
        ids =sorted(ids)[0:4] # don't include the block or rec particles as its tricky to check as order of particle manufacture varies
        expectedids=sorted([sim.UID(2), sim.UID(102),sim.UID(202),sim.UID(302)])
        self.assertEqual(ids,expectedids )
    
            
        
        #(2) use edge nodes to see what is connected
        ids=[]
        BFS = BreadthFirstSearchIterative(pfblocker.edgeNodes[nodeuid],"undirected")
        for n in BFS.result :
            ids.append(n.getValue())
        expectedids=sorted([sim.UID(2), sim.UID(102),sim.UID(202)])   
        self.assertEqual(sorted(ids), expectedids)
        
        #(3) Give me all blocks with  one track:
        blockids=[]
        for b in event.blocks.itervalues() :
            if b.countTrack()==1 : 
                blockids.append(b.uniqueid)
                print "Block with 1 TRACK: " + str(b.uniqueid);
        
        #(4) Give me all simulation particles attached to each reconstructed particle
        for rp in event.recParticles :
            BFS = BreadthFirstSearchIterative(event.historyNodes[rp],"parents")
            print "Rec particle: ", event.recParticles[rp].pdgid, " from "            
            for n in BFS.result :
                if (Identifier.isParticle(n.getValue())) :
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
