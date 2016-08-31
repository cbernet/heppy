from heppy.papas.data.identifier import Identifier



class PFEvent(object):
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
    def __init__(self, event ):    
        '''arguments
             event: must contain
                  tracks dictionary : {id1:track1, id2:track2, ...}
                  ecal dictionary : {id1:ecal1, id2:ecal2, ...}
                  hcal dictionary : {id1:hcal1, id2:hcal2, ...}
                  
                  and these must be names according to ecalsname etc
                  blocks, sim_particles and rec_particles are optional
                  '''            
        self.event= event       
    
    def get_object(self, uniqueid):
        ''' given a uniqueid return the underlying obejct
        '''
        type = Identifier.get_type(uniqueid)
        if type == Identifier.PFOBJECTTYPE.TRACK:
            if uniqueid in self.event.tracks :
                return self.event.tracks[uniqueid] 
            elif uniqueid in self.event.gen_tracks :
                return self.event.gen_tracks[uniqueid] 
            else:
                        assert(False)            
        elif type == Identifier.PFOBJECTTYPE.ECALCLUSTER:      
            if uniqueid in self.event.ecal_clusters:            
                return self.event.ecal_clusters[uniqueid] 
            elif uniqueid in self.event.smeared_ecals:            
                return self.event.smeared_ecals[uniqueid]             
            elif uniqueid in self.event.gen_ecals:            
                return self.event.gen_ecals[uniqueid] 
            else:
                        assert(False)            
        elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER:            
            if uniqueid in self.event.hcal_clusters:            
                return self.event.hcal_clusters[uniqueid] 
            elif uniqueid in self.event.smeared_hcals:            
                return self.event.smeared_hcals[uniqueid]             
            elif uniqueid in self.event.gen_hcals:            
                return self.event.gen_hcals[uniqueid] 
            else:
                        assert(False)            
        elif type == Identifier.PFOBJECTTYPE.PARTICLE:
            return self.event.gen_stable_particles[uniqueid] 
        elif type == Identifier.PFOBJECTTYPE.SIMPARTICLE:
            return self.event.sim_particles[uniqueid]          
        elif type == Identifier.PFOBJECTTYPE.RECPARTICLE:
            return self.event.rec_particles[uniqueid]               
        elif type == Identifier.PFOBJECTTYPE.BLOCK:
            return self.event.blocks[uniqueid]               
        else:
            assert(False)   


