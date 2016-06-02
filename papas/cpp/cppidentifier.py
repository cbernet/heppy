from ROOT import gSystem
gSystem.Load("libfccphysics-papas")
#gSystem.Load("libpapascpp")
from ROOT.papas import Id


class Identifier(long):

## simplified class to provide a unique identifier for each object
## could also add more information into the identifier as needed

    #'''the Identififier is a uniqueid that contains encoded information about an element
            #for example, given an indentifier, we can determine that the element is an ecal_cluster
            #and retrieve the cluster from a cluster dict.

        #The Identifier class consists of a set of static methods that can be used
        #to create and to dissect identifiers.

        #The first(rightmost) 40 bits are used to contain the python unique objectid of the item
        #The bits to the left of this contain the objecttype eg ECALCLUSTER etc

        #usage:
            #self.uniqueid = Identifier.make_id(self,Identifier.PFOBJECTTYPE.BLOCK) 
            #if Identifier.is_track(self.uniqueid):
                #....

        #'''    
    class PFOBJECTTYPE:
        NONE = 0
        ECALCLUSTER = 1 #simplistic initial implementation (may need an enum for layer to be added)
        HCALCLUSTER = 2
        TRACK = 3
        PARTICLE = 4
        RECPARTICLE = 5
        BLOCK = 6

    @staticmethod    
    def make_id(item, type):
        return Id.makeId(type)

    @staticmethod      
    def get_unique_id(ident):
        return Id.uniqueId(ident)

    @staticmethod  
    def get_type(ident):
        return Id.itemType(ident)

    @staticmethod  
    def is_ecal(ident):
        return Id.isEcal(ident)  

    @staticmethod  
    def is_hcal(ident):
        return Id.isHcal(ident)  

    @staticmethod  
    def is_track(ident):
        return Id.isTrack(ident)   

    @staticmethod  
    def is_block (ident):
        return Id.isBlock(ident)      

    @staticmethod  
    def is_rec_particle(ident):
        return Id.isRecParticle(ident)    

    @staticmethod  
    def is_particle(ident):
        return Id.isParticle(ident)         

    @staticmethod
    def type_short_code(ident):
        return Id.typeShortCode(ident)   


