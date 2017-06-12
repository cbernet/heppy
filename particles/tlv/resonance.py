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
    
    def __init__(self, legs, pid):
        self.legs = legs
        tlv = TLorentzVector()
        charge = 0
        for leg in legs:
            charge += leg.q()
            tlv += leg.p4()
        super(Resonance, self).__init__(pid, charge, tlv, status=3)

            
class Resonance2(Resonance):
    '''Resonance decaying to two legs.'''

    def __init__(self, leg1, leg2, pid):
        '''leg1 and leg2 are the first and second legs, respectively.
        no sorting is done internally.
        pid is the pdg id of the resonance.
        '''
        super(Resonance2, self).__init__([leg1, leg2], pid)

    def leg1(self):
        '''return first leg'''
        return self.legs[0]

    def leg2(self):
        '''return second leg'''
        return self.legs[1]

    def acollinearity(self):
        '''return the angle between the two legs, in radians'''
        return self.leg1().p3().Angle(self.leg2().p3())
    
    def acoplanarity(self, axis=None):
        '''return the angle between the lepton plane and the provided axis.
        
        If axis is None, using the z axis.
        '''
        # normal to lepton plane
        if axis is None:
            axis = TVector3(0, 0, 1)
        normal = self.leg1().p3().Cross(self.leg2().p3()).Unit()
        angle = normal.Angle(axis)
        while angle > math.pi / 2.:
            angle -= math.pi / 2.
        return angle
