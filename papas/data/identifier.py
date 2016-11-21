
'''Unique Identifer'''
import struct
from itertools import count
from heppy.utils.pdebug import pdebugger

class Identifier(long):
    '''The Identifier is a uniqueid that contains encoded information about an element
    
    Given an identifier, we can determine whether the element is for example an ecal_cluster
    and then retrieve the cluster from a cluster dict.

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
    value (small to large)
    uniqueid
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
        '''Creates a unique id
        @param type: defined by enumeration PFOBJECTTYPE eg ECALCLUSTER
        @param subtype:single letter subtype code eg 'm' for merged
        @param value: a float reprenting energy or momentum etc
        '''
    
        assert(value >= 0) #actually I would like it to work with negative numbers but need to change float to bit conversions
        x = cls._id.next()
        #shift all the parts and join together	
        typeshift = type << 61
        valueshift = Identifier._float_to_bits(value) << 21
        subtypeshift = ord(subtype.lower()) << 53
        uid = subtypeshift | valueshift | typeshift | x

        #verify		
        assert (Identifier.get_unique_id(uid) == x )
        if value != 0:
            assert(abs(Identifier.get_value(uid) - value) < abs(value) * 10 ** -6)
        assert (Identifier.get_type(uid) == type)
        assert (Identifier.get_subtype(uid) == subtype)
        if x >= 2**(21 -1):
            raise ValueError('identifer unique counter id has exceeded maximum value allowed')
        return uid

    @staticmethod      
    def get_unique_id( ident):
        '''Takes an identifier and returns the unique counter component of it
        @param: unique identifier'''
        return ident & 0b111111111111111111111

    @staticmethod  
    def get_type ( ident):
        '''returns the PFOBJECTTYPE type of the identifier eg ECALCLUSTER
        @param ident: unique identifier'''        
        return ident >> 61 & 0b111

    @staticmethod  
    def get_subtype ( ident):
        '''returns the subtype of the identifier eg 'm'
                @param: unique identifier
            intended to be single char
            Some possible existing uses
            eg 
             'g' generated
             'r' reconstructed
             'u' unspecified
             't' true
             's' simulated (particles)
                 smeared (tracks ecals hcals)
                 split (blocks)
        '''
        return chr( (ident >> 53 & 0b11111111))

    @staticmethod  
    def get_value (ident):
        '''returns the float value encoded in the identifier 
        @param ident: unique identifier'''         
        bitvalue = ident >> 21 & 0b11111111111111111111111111111111
        return Identifier._bits_to_float(bitvalue)

    @staticmethod  
    def is_ecal ( ident):
        '''boolean test of whether it is an ecal
        @param ident: unique identifier'''         
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def is_hcal ( ident):
        '''boolean test of whether it is an hcal
        @param ident: unique identifier'''   
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.HCALCLUSTER  

    @staticmethod  
    def is_track ( ident):
        '''boolean test of whether it is a track
        @param ident: unique identifier'''   
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.TRACK 

    @staticmethod  
  
    def is_block ( ident):
        '''boolean test of whether it is a block
        @param ident: unique identifier'''         
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.BLOCK     

    @staticmethod  
    def is_particle ( ident):
        '''boolean test of whether it is an ecal
        @param ident: unique identifier'''   
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.PARTICLE 

    @staticmethod
    def type_letter(ident): #character/letter for this type
        '''returns a single letter representation of the PFOBJECTTYPE type eg 'p' for particle
        @param ident: unique identifier'''     
        typelist=".ehtpb..." #the enum value (0 to 8) will index into this and return E is it is ECAL etc
        return typelist[Identifier.get_type(ident)]    

    @staticmethod
    def type_and_subtype(ident):
        '''returns a two  letter representation of the type/ subtype eg 'pr' for reconstructed particle
        @param ident: unique identifier
        '''        
        return  Identifier.type_letter(ident) + Identifier.get_subtype(ident) 

    @staticmethod
    def pretty(ident):
        '''returns a pretty string representation of the identifier with the two letter typ_and_subtype and the uniqueid
           @param ident: unique identifier
        '''          
        return  Identifier.type_and_subtype(ident) + str(Identifier.get_unique_id(ident))

    @staticmethod
    def _float_to_bits (floatvalue):  #standard float packing
        '''takes a float and returns a bit representation
        @param floatvalue: float'''
        s = struct.pack('>f', floatvalue)
        return struct.unpack('>l', s)[0]  # 32bit representation

    @staticmethod
    def _bits_to_float (bitvalue):
        '''takes a bit vlaue and returns a float representation
        @param bitvalue: bitvalue'''
        s = struct.pack('>l', bitvalue)
        return struct.unpack('>f', s)[0]	
    
    @classmethod
    def reset(cls):
        ''' Resets the internal Identifier counter to 1
        '''
        cls._id=count(1)
        pdebugger.info("reset ID")
        return

if __name__ == '__main__':

    uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 1.23456)
    id1 = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 12.782) 
   
    assert (Identifier.pretty(id1) == 'st2')
    ids = []
    for i in range(0,100):
        uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 2**(-i) )
        ids.append(uid)
    ids = sorted(ids, reverse = True)
    for uid in ids:
        print Identifier.pretty(uid) + ": " + str(Identifier.get_value(uid))
    pass
