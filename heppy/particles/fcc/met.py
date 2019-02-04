from heppy.particles.met import MET as BaseMET
from ROOT import TLorentzVector

class Met(BaseMET):
    
    def __init__(self, fccmet):
        self.fccmet = fccmet
        self._sum_et = fccmet.scalarSum()
        self._tlv = TLorentzVector()
        self._tlv.SetPtEtaPhiM(fccmet.magnitude(), 0.,fccmet.phi(),0. )
        self._charge = 0. 
