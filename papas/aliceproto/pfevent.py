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
        if hasattr(event,"papas_sim_particles"): #todo think about naming
            self.sim_particles= event.papas_sim_particles 
        if hasattr(event,"reconstructed_particles"): #todo think about naming
            self.reconstructed_particles= event.reconstructed_particles                         
    
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
    
    def __init__(self, history_nodes,pfevent):
        self.history_nodes=history_nodes
        self.pfevent=pfevent
        
    def summary_of_links(self, id):
    
        BFS = BreadthFirstSearch(self.history_nodes[id],"undirected")
        print "history connected to node:", id
        
        tracks=[]
        ecals=[]
        hcals=[]
        sim_particles=[]
        rec_particles=[]
        for n in BFS.result :
            z=n.get_value()
            descrip=self.pfevent.get_object(z).__str__()
            if (Identifier.is_particle(z)) :
                sim_particles.append(descrip)
            if (Identifier.is_track(z)) :
                tracks.append(descrip)         
            if (Identifier.is_ecal(z)) :
                ecals.append(descrip)  
            if (Identifier.is_hcal(z)) :
                hcals.append(descrip)         
            if (Identifier.is_rec_particle(z)) :
                rec_particles.append(descrip)               
        
        print "sim particles", sim_particles
        print "       tracks", tracks
        print "        ecals", ecals
        print "        hcals", hcals
        print "rec particles", rec_particles
        
        #print "reconstructed particles"