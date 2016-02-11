from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance 

import pprint 
import itertools


class M3Builder(Analyzer):
    
    def process(self, event):
        jets = getattr(event, self.cfg_ana.jets)
        jets = [jet for jet in jets if self.cfg_ana.filter_func(jet)]
        m3 = None
        if len(jets)>=3:
            top_pdgid = 6
            m3 = Resonance(jets[:3], top_pdgid)
        setattr(event, self.instance_label, m3)
