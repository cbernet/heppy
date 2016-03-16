from heppy.papas.aliceproto.identifier import Identifier

class PFEvent(object):
    '''GetObject used to add a function get_object to an Event class
    ''' 
    def __init__(self, event) :    
        self.tracks=event.tracks
        self.ecal_clusters=event.ecal_clusters
        self.hcal_clusters=event.hcal_clusters
        self.blocks =[]
        if hasattr(event,"blocks") :
            self.blocks= event.blocks

        
    
    def get_object(self, uniqueid):
        ''' given a uniqueid return the underlying obejct
        '''
        type =  Identifier.get_type(uniqueid)
        if type == Identifier.PFOBJECTTYPE.TRACK :
            return self.tracks[uniqueid]       
        elif type == Identifier.PFOBJECTTYPE.ECALCLUSTER :      
            return self.ecal_clusters[uniqueid] 
        elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER :            
            return self.hcal_clusters[uniqueid]            
        elif type == Identifier.PFOBJECTTYPE.PARTICLE :
            return self.sim_particles[uniqueid]   
        elif type == Identifier.PFOBJECTTYPE.RECPARTICLE :
            return self.reconstructed_particles[uniqueid]               
        elif type == Identifier.PFOBJECTTYPE.BLOCK :
            return self.blocks[uniqueid]               
        else :
            assert(False)   
