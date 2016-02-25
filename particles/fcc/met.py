from heppy.particles.met import MET as BaseMET
from ROOT import TLorentzVector
import math

class Met(BaseMET):
    
    def __init__(self, fccmet):
        self.fccmet = fccmet
        self.met = fccmet.Magnitude()
        self.phi = fccmet.Phi()
        self.sum_et = fccmet.ScalarSum()
