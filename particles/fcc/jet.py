from heppy.particles.jet import Jet as BaseJet
from vertex import Vertex
from ROOT import TLorentzVector
import math

class Jet(BaseJet):
    
    def __init__(self, fccjet):
        self.fccjet = fccjet
        self._tlv = TLorentzVector()
        p4 = fccjet.Core().P4
        self._tlv.SetXYZM(p4.Px, p4.Py, p4.Pz, p4.Mass)
        

