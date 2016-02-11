from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector

class Resonance(Particle):
    """Resonance decaying to two or more particles (legs).
    
    A leg is a particle-like object with the following methods:
    - q(): returns charge
    - p4(): returns 4-momentum TLorentzVector
    - e(): returns energy
    """
    
    def __init__(self, legs, pid):
        self.legs = legs
        self._pid = pid
        self._charge = 0
        self._status = 3 
        self._tlv = TLorentzVector()
        for leg in legs:
            self._charge += leg.q()
            self._tlv += leg.p4()

            
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
