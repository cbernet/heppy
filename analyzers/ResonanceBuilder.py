from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance2 as Resonance

import pprint 
import itertools

masses = {23: 91, 25: 125}

class ResonanceBuilder(Analyzer):
    
    def process(self, event):
        # legs = event.gen_particles_stable
        legs = getattr(event, self.cfg_ana.leg_collection)
        legs = [leg for leg in legs if self.cfg_ana.filter_func(leg)]
        resonances = []
        for leg1, leg2 in itertools.combinations(legs,2):
            resonances.append( Resonance(leg1, leg2, self.cfg_ana.pdgid) )
        # sorting according to distance to nominal mass
        nominal_mass = mass[self.cfg_ana.pdgid]
        resonances.sort(key=lambda x: abs(x.m()-nominal_mass))
        setattr(event, self.instance_label, resonances)
