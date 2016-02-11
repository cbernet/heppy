from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle 

import pprint 
import itertools

mass = {23: 91, 25: 125}

class Resonance(Particle):
    def __init__(self, leg1, leg2, pdgid, status=3): 
        self.leg1 = leg1 
        self.leg2 = leg2 
        self._tlv = leg1.p4() + leg2.p4()
        self._charge = leg1.q() + leg2.q()
        self._pid = pdgid
        self._status = status

class ParticlesForJets(Analyzer):
    
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        output = []
        for ptc in particles: 
            # print ptc
            accept = True
            for colname in self.cfg_ana.resonances:
                resonances = getattr(event, colname)
                for resonance in resonances: 
                    if ptc is resonance.leg1 or ptc is resonance.leg2:
                        # print 'remove', ptc
                        accept = False
            if accept: 
                output.append(ptc)
        setattr(event, self.instance_label, output)


                
