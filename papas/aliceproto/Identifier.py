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
    def makeID(item, type) :
        x=id(item)
        value=  type <<40
        return value | x
   
    @staticmethod      
    def getUniqueID( ident) :
        return ident & 0b1111111111111111111111111111111111111111
    
    @staticmethod  
    def gettype ( ident) :
        return ident >> 40
    
    @staticmethod  
    def is_ecal ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def is_hcal ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.HCALCLUSTER  


    @staticmethod  
    def is_track ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.TRACK 
    
    @staticmethod  
    def isBlock ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.BLOCK     
    
    @staticmethod  
    def isRecParticle ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.RECPARTICLE 
    
    @staticmethod  
    def isParticle ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.PARTICLE     
    
    @staticmethod
    def type_short_code(ident) :
        typelist=".EHT......" #the enum value will index into this and return E is it is ECAL etc
        return typelist[Identifier.gettype(ident)]    