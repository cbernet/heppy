from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector, TVector3
from rootobj import RootObj
import math

class Resonance(Particle, RootObj):
    """Resonance decaying to two or more particles (legs).
    
    A leg is a particle-like object with the following methods:
    - q(): returns charge
    - p4(): returns 4-momentum TLorentzVector
    - e(): returns energy
    """
    
    def __init__(self, legs, pid, status=3):
        self.legs = legs
        tlv = TLorentzVector()
        charge = 0
        for leg in legs:
            charge += leg.q()
            tlv += leg.p4()
        super(Resonance, self).__init__(pid, charge, tlv, status)

    def boost(self, boost_vector):
        '''Boost the resonance and its legs to another lorentz frame.
        
        See the ROOT documentation for the definition of the boost vector.
        If you have a p4, you can get it by doing p4.BoostVector()
        '''
        self._tlv.Boost(boost_vector)
        for leg in self.legs:
            leg._tlv.Boost(boost_vector)
        
        
            
class Resonance2(Resonance):
    '''Resonance decaying to two legs.'''

    def __init__(self, leg1, leg2, pid, status=3):
        '''leg1 and leg2 are the first and second legs, respectively.
        no sorting is done internally.
        pid is the pdg id of the resonance.
        '''
        super(Resonance2, self).__init__([leg1, leg2], pid, status)

    def leg1(self):
        '''return first leg'''
        return self.legs[0]

    def leg2(self):
        '''return second leg'''
        return self.legs[1]

    def acollinearity(self):
        '''return the angle between the two legs, in radians'''
        return self.leg1().p3().Angle(self.leg2().p3()) * 180 / math.pi
    
    def acoplanarity(self, axis=None):
        '''return the angle between the lepton plane and the provided axis.
        
        If axis is None, using the z axis.
        '''
        if axis is None:
            axis = TVector3(0, 0, 1)
        p1 = self.leg1().p3()
        p2 = self.leg2().p3()
        normal = p1.Cross(p2).Unit()
        angle = abs(normal.Angle(axis) - math.pi / 2.)
        return angle * 180 / math.pi

    def cross(self):
        '''Patrick's acoplanarity variable
        '''
        p1 = self.leg1().p3()
        p2 = self.leg2().p3()
        cross = p1.Unit().Cross(p2.Unit())
        cross = abs(cross.z())
        cross = math.asin(cross) 
        return cross * 180 / math.pi

