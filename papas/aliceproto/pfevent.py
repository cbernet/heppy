from heppy.papas.aliceproto.identifier import Identifier



class PFEvent(object):
    '''PFEvent is used to  allow addition of a function get_object to an Event class
       get_object() allows a cluster or track to be found from its id
         
       
       attributes:
          tracks is a dictionary : {id1:track1, id2:track2, ...}
          ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
          hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
          blocks = optional dictionary of blocks : {id1:block1, id2:block2, ...}
       
       usage: 
          pfevent = PFEvent(event)
          obj1 = pfevent.get_object(id1)
    ''' 
    def __init__(self, event):    
        '''arguments
             event: must contain
                  tracks dictionary : {id1:track1, id2:track2, ...}
                  ecal dictionary : {id1:ecal1, id2:ecal2, ...}
                  hcal dictionary : {id1:hcal1, id2:hcal2, ...}
                  '''            
        self.tracks = event.tracks
        self.ecal_clusters = event.ecal_clusters
        self.hcal_clusters = event.hcal_clusters
        self.blocks = []
        if hasattr(event,"blocks"):
            self.blocks= event.blocks

    
    def get_object(self, uniqueid):
        ''' given a uniqueid return the underlying obejct
        '''
        type = Identifier.get_type(uniqueid)
        if type == Identifier.PFOBJECTTYPE.TRACK:
            return self.tracks[uniqueid]       
        elif type == Identifier.PFOBJECTTYPE.ECALCLUSTER:      
            return self.ecal_clusters[uniqueid] 
        elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER:            
            return self.hcal_clusters[uniqueid]            
        elif type == Identifier.PFOBJECTTYPE.PARTICLE:
            return self.sim_particles[uniqueid]   
        elif type == Identifier.PFOBJECTTYPE.RECPARTICLE:
            return self.reconstructed_particles[uniqueid]               
        elif type == Identifier.PFOBJECTTYPE.BLOCK:
            return self.blocks[uniqueid]               
        else:
            assert(False)   


from heppy.papas.aliceproto.DAG import Node, BreadthFirstSearch
class History(object):
    
    def __init__(self, history_nodes):
        self.history_nodes=history_nodes
        
    def summary_of_links(self, id):
    
        BFS = BreadthFirstSearch(self.history_nodes[id],"undirected")
        print "history connected to node:", id
        particles=[]
        tracks=[]
        ecals=[]
        hcals=[]
        recparticles=[]
        recon_particles=[]
        for n in BFS.result :
            z=n.get_value()
            if (Identifier.is_particle(z)) :
                particles.append(z)
            if (Identifier.is_track(z)) :
                tracks.append(z)         
            if (Identifier.is_ecal(z)) :
                ecals.append(z)  
            if (Identifier.is_hcal(z)) :
                hcals.append(z)         
            if (Identifier.is_rec_particle(z)) :
                recon_particles.append(z)               
        
        print "raw particles", particles
        print "   tracks", tracks
        print "   ecals", ecals
        print "   hcals", hcals
        print "reconstructed particles", recon_particles
        
        #print "reconstructed particles"