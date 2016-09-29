import struct
from itertools import count
from heppy.utils.pdebug import pdebugger

class Identifier(long):
    '''the Identififier is a uniqueid that contains encoded information about an element
           for example, given an identifier, we can determine that the element is an ecal_cluster
           and thus retrieve the cluster from a cluster dict.

        The Identifier class consists of a set of static methods that can be used
        to create and to dissect identifiers.

        The identifier is 64 bits wide and stores info as follows
    from left: bits 64 to 61 = PFOBJECTTYPE enumeration eg ECAL, HCAL, PARTICLE (max value = 7)
    bits 60 to 53 = subtype - a single char eg 'g'
                      bits 52 to 20 = encoded float value eg energy
                      bits 21 to 1 = unique id (max value = 2097152 -1)

    Note that sorting on id will result in sorting by:
    type
    subtype
    value
    uniqueid

    Custom sorting can be obtained using methods that access each of the subcomponents of Id

        usage:
           self.uniqueid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 1.23456) 
           if Identifier.is_track(self.uniqueid):
                ....

        '''    

    _id = count(1)


    class PFOBJECTTYPE:
        NONE = 0
        ECALCLUSTER = 1 #simplistic initial implementation (may need an enum for layer to be added)
        HCALCLUSTER = 2
        TRACK = 3
        PARTICLE = 4
        BLOCK = 5


    @classmethod    
    def make_id(cls, type, subtype='u', value = 0.):
        x = cls._id.next()
        #shift all the parts and join together	
        typeshift = type << 61

        Identifier.get_type(39)
        valueshift = Identifier._float_to_bits(value) << 21
        subtypeshift = ord(subtype.lower()) << 53
        id = subtypeshift | valueshift | typeshift | x

        #verify		
        assert (Identifier.get_unique_id(id) == x )
        if value > 0:
            assert(abs(Identifier.get_value(id) - value) < abs(value) * 10 ** -6)
        assert (Identifier.get_type(id) == type)
        assert (Identifier.get_subtype(id) == subtype)

        return id

    @staticmethod      
    def get_unique_id( ident):
        return ident & 0b111111111111111111111

    @staticmethod  
    def get_type ( ident):
        #return ident >> 32 & 0b111111
        return ident >> 61 & 0b111

    @staticmethod  
    def get_subtype ( ident):
        ''' intended to be single char
            Some possible existing uses
            eg 's' simulation or smeared
             'g' generated
             'r' reconstructed
             'u' unspecified
        '''
        return chr( (ident >> 53 & 0b11111111))

    @staticmethod  
    def get_value (ident):
        bitvalue = ident >> 21 & 0b11111111111111111111111111111111
        return Identifier._bits_to_float(bitvalue)

    @staticmethod  
    def is_ecal ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def is_hcal ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.HCALCLUSTER  

    @staticmethod  
    def is_track ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.TRACK 

    @staticmethod  
    def is_block ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.BLOCK     

    @staticmethod  
    def is_particle ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.PARTICLE 

    @staticmethod
    def type_short_code(ident):
        typelist=".ehtpb..." #the enum value (0 to 8) will index into this and return E is it is ECAL etc
        return typelist[Identifier.get_type(ident)]    

    @staticmethod
    def type_code(ident):
        ''' Returns code
                      e = ecal
                      h = hcal
                      t = track
                      p = particle
                      b = block
                '''        
        typelist=".ehtpb..." #the enum value (0 to 8) will index into this and return E is it is ECAL etc
        return Identifier.get_subtype(ident) + typelist[Identifier.get_type(ident)]   

        
        

    @staticmethod
    def pretty(ident):
        return Identifier.get_subtype(ident) + Identifier.type_short_code(ident) + str(Identifier.get_unique_id(ident))

    @staticmethod
    def _float_to_bits (floatvalue):  #standard float packing
        s = struct.pack('>f', floatvalue)
        return struct.unpack('>l', s)[0]  # 32bit representation

    @staticmethod
    def _bits_to_float (bitvalue):
        s = struct.pack('>l', bitvalue)
        return struct.unpack('>f', s)[0]	

    @classmethod
    def reset(cls):
        cls._id=count(1)
        pdebugger.info("reset ID")
        return


if __name__ == '__main__':

    id = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 1.23456) 
    print Identifier.get_subtype(id)
    print Identifier.get_type(id)
    id = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 12.782) 
    print Identifier.get_subtype(id)
    print Identifier.get_type(id)
    pass
