from heppy.particles.jet import Jet as BaseJet

import math

class Jet(BaseJet):
    def __init__(self, tlv):
        super(Jet, self).__init__()
        self._tlv = tlv

        
