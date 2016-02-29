from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle as Recoil

from ROOT import TLorentzVector

mass = {23: 91, 25: 125}

class RecoilBuilder(Analyzer):
    
    def process(self, event):
        sqrts = self.cfg_ana.sqrts
        to_remove = getattr(event, self.cfg_ana.to_remove) 
        recoil_p4 = TLorentzVector(0, 0, 0, sqrts)
        for ptc in to_remove:
            recoil_p4 -= ptc.p4()
        recoil = Recoil(0, 0, recoil_p4, 1) 
        setattr(event, self.cfg_ana.output, recoil)
                
