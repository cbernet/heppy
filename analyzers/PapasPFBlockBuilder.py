from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.aliceblockbuilder import BlockBuilder
from heppy.papas.pfalgo.distance  import Distance

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
            return self.event.ECALclusters[e1] 
        elif type == Identifier.PFOBJECTTYPE.HCALCLUSTER :            
            return self.event.HCALclusters[e1]            
        elif type == Identifier.PFOBJECTTYPE.PARTICLE :
            return self.event.sim_particles[e1]   
        elif type == Identifier.PFOBJECTTYPE.RECPARTICLE :
            return self.event.reconstructed_particles[e1]               
        elif type == Identifier.PFOBJECTTYPE.BLOCK :
            return self.event.blocks[e1]               
        else :
            assert(False)   

    


    


class PapasPFBlockBuilder(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        ecal = event.ECALclusters
        hcal = event.HCALclusters
        tracks = event.tracks
        
        distance = Distance()
        get_object = GetObject(event)
        
        blockbuilder = BlockBuilder( tracks, ecal, hcal, distance, get_object)
        print blockbuilder
            
        event.blocks = blockbuilder.blocks
        
