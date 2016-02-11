from heppy.framework.analyzer import Analyzer

from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector 

class MissingEnergyBuilder(Analyzer):
    
    def process(self, event):
        add = getattr(event, self.cfg_ana.particles_add)
        sub = getattr(event, self.cfg_ana.particles_sub)
        missingp4 = TLorentzVector()
        charge = 0
        sumpt = 0 
        for ptc in add:
            missingp4 += ptc
            charge += ptc.q()
        for ptc in sub: 
            missingp4 -= ptc
            charge -= ptc.q() 
        missing = Particle(0, charge, missingp4)
        setattr(event, self.instance_label, missing)
