from heppy.particles.jet import Jet as BaseJet
from pod import POD

from ROOT import TLorentzVector
import math

class Jet(BaseJet, POD):
    
    def __init__(self, fccobj):
        super(Jet, self).__init__(fccobj)
        self._tlv = TLorentzVector()
        p4 = fccobj.core().p4
        self._tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        

