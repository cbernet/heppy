from heppy.papas.aliceproto.identifier import Identifier

class GetObject(object):
    '''GetObject used to add a function get_object to an Event class
    ''' 
    def __init__(self, event) :    
        self.event=event
    
    def __call__(self, e1):
        ''' given a uniqueid return the underlying obejct
        '''
        type =  Identifier.get_type(e1)
        if type == Identifier.PFOBJECTTYPE.TRACK :
            return self.event.tracks[e1]       
        elif type == Identifier.PFOBJECTTYPE.ECALCLUSTER :      
            return self.event.ecal_clusters[e1] 
        elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER :            
            return self.event.hcal_clusters[e1]            
        elif type == Identifier.PFOBJECTTYPE.PARTICLE :
            return self.event.sim_particles[e1]   
        elif type == Identifier.PFOBJECTTYPE.RECPARTICLE :
            return self.event.reconstructed_particles[e1]               
        elif type == Identifier.PFOBJECTTYPE.BLOCK :
            return self.event.blocks[e1]               
        else :
            assert(False)   

    
