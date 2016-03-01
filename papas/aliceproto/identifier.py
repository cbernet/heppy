# simplified class to provide a unique identifier for each object
# could also add more information into the identifier as needed
class Identifier(long) :
    class PFOBJECTTYPE:
        NONE=0
        ECALCLUSTER=1 #simplistic initial implementation (may need an enum for layer to be added)
        HCALCLUSTER=2
        TRACK=3
        PARTICLE=4
        RECPARTICLE=5
        BLOCK=6
    
    @staticmethod    
    def make_id(item, type) :
        x=id(item)
        value=  type <<40
        return value | x
   
    @staticmethod      
    def get_unique_id( ident) :
        return ident & 0b1111111111111111111111111111111111111111
    
    @staticmethod  
    def get_type ( ident) :
        return ident >> 40
    
    @staticmethod  
    def is_ecal ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def is_hcal ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.HCALCLUSTER  

    @staticmethod  
    def is_track ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.TRACK 
    
    @staticmethod  
    def isBlock ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.BLOCK     
    
    @staticmethod  
    def isRecParticle ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.RECPARTICLE 
    
    @staticmethod  
    def isParticle ( ident) :
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.PARTICLE     
    
    @staticmethod
    def type_short_code(ident) :
        typelist=".EHT......" #the enum value (0 to 8) will index into this and return E is it is ECAL etc
        return typelist[Identifier.get_type(ident)]    