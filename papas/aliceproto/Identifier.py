# simplified class to provide a unique identifier for each object
# could also add more information into the identifier as needed
class Identifier(long) :
    class PFOBJECTTYPE:
        NONE=0
        ECALCLUSTER=1
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
    def isECAL ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def isHCAL ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.HCALCLUSTER  


    @staticmethod  
    def isTrack ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.TRACK 
    
    @staticmethod  
    def isBlock ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.BLOCK     
    
    @staticmethod  
    def isRecParticle ( ident) :
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.RECPARTICLE 
    @staticmethod  
    def isParticle ( ident) :
        print Identifier.gettype(ident)
        return Identifier.gettype(ident)  ==Identifier.PFOBJECTTYPE.PARTICLE     