from heppy.particles.particle import Particle as BaseParticle
from rootobj import RootObj

import math

class Particle(BaseParticle, RootObj):
    def __init__(self, pdgid, charge, tlv, status=1):
        super(Particle, self).__init__()
        self._pid = pdgid
        self._charge = charge
        self._tlv = tlv
        self._status = status
