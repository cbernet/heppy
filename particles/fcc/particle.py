from heppy.particles.particle import Particle as BaseParticle
from vertex import Vertex
from ROOT import TLorentzVector
import math

class Particle(BaseParticle):
    
    def __init__(self, fccptc):
        self.fccptc = fccptc
        self._charge = fccptc.Core().Charge
        self._pid = fccptc.Core().Type
        self._status = fccptc.Core().Status
        start = fccptc.StartVertex()
        self._start_vertex = Vertex(start) if start.isAvailable() \
                             else None 
        end = fccptc.EndVertex()
        self._end_vertex = Vertex(end) if end.isAvailable() \
                           else None 
        self._tlv = TLorentzVector()
        p4 = fccptc.Core().P4
        self._tlv.SetXYZM(p4.Px, p4.Py, p4.Pz, p4.Mass)
        

