from ROOT import gSystem
#gSystem.Load("libfccphysics-papas")
gSystem.Load("libpapascpp")

from heppy.papas.data.identifier import Identifier
from heppy.papas.pfobjects  import Cluster as  ClusterPy
from ROOT.papas import Cluster as  ClusterCpp
from ROOT.papas import Track as  TrackCpp
from ROOT import std



class PFEventCpp(object):
    '''PFEvent is used to  allow addition of a function get_object to an Event class
       get_object() allows a cluster or track to be found from its id
       May want to merge this with the history class
       
       attributes:
          tracks is a dictionary : {id1:track1, id2:track2, ...}
          ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
          hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
          blocks = optional dictionary of blocks : {id1:block1, id2:block2, ...}
       
       usage: 
          pfevent=PFEvent(event, self.tracksname,  self.ecalsname,  self.hcalsname,  self.blocksname) 
          obj1 = pfevent.get_object(id1)
    ''' 
    def __init__(self, event,  tracksname = 'tracks', ecalsname = 'ecal_clusters',  hcalsname = 'hcal_clusters') : #,  blocksname = 'blocks',
                # sim_particlesname = "None",  rec_particlesname = "reconstructed_particles"):    
        '''arguments
             event: must contain
                  tracks dictionary : {id1:track1, id2:track2, ...}
                  ecal dictionary : {id1:ecal1, id2:ecal2, ...}
                  hcal dictionary : {id1:hcal1, id2:hcal2, ...}
                  
                  and these must be names according to ecalsname etc
                  blocks, sim_particles and rec_particles are optional
                  '''            
        self.tracks = getattr(event, tracksname)
        self.ecal_clusters = getattr(event, ecalsname)
        
        
        self.ecal_clusters_cpp =  std.unordered_map('papas::Id::Type', 'papas::Cluster')()
        for cluster in  getattr( event,  ecalsname).itervalues():
            clustercpp = ClusterCpp(cluster.energy, cluster.position,  cluster.size(),  cluster.uniqueid)  
            self.ecal_clusters_cpp[clustercpp.id()] = clustercpp            
        
        
        self.hcal_clusters_cpp =  std.unordered_map('papas::Id::Type', 'papas::Cluster')()
        for cluster in  getattr( event,  hcalsname).itervalues():
            clustercpp = ClusterCpp(cluster.energy, cluster.position,  cluster.size(),  cluster.uniqueid)  
            self.hcal_clusters_cpp[clustercpp.id()] = clustercpp            

        self.tracks_cpp =  std.unordered_map('papas::Id::Type', 'papas::Track')()
        for track in  getattr( event,  tracksname).itervalues():
            #path needs sorting
            trackcpp = TrackCpp(track.p3, track.charge,  0,  track.uniqueid)  
            self.tracks_cpp[trackcpp.id()] = trackcpp                

        print self.hcal_clusters_cpp.size()
        pass
        
        #self.hcal_clusters = getattr(event, hcalsname)
        
        #self.blocks = []
        #if hasattr(event, blocksname):
            #self.blocks =  getattr(event, blocksname)
        #if hasattr(event,sim_particlesname): 
            #self.sim_particles= getattr(event, sim_particlesname)
        #if hasattr(event,rec_particlesname): #todo think about naming
            #self.reconstructed_particles= getattr(event, rec_particlesname)                       
    
    
    #def get_object(self, uniqueid):
        #''' given a uniqueid return the underlying obejct
        #'''
        #type = Identifier.get_type(uniqueid)
        #if type == Identifier.PFOBJECTTYPE.TRACK:
            #return self.tracks[uniqueid]       
        #elif type == Identifier.PFOBJECTTYPE.ECALCLUSTER:      
            #return self.ecal_clusters[uniqueid] 
        #elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER:            
            #return self.hcal_clusters[uniqueid]            
        #elif type == Identifier.PFOBJECTTYPE.PARTICLE:
            #return self.sim_particles[uniqueid]   
        #elif type == Identifier.PFOBJECTTYPE.RECPARTICLE:
            #return self.reconstructed_particles[uniqueid]               
        #elif type == Identifier.PFOBJECTTYPE.BLOCK:
            #return self.blocks[uniqueid]               
        #else:
            #assert(False)   


