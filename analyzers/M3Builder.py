from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance 

import pprint 
import itertools


class M3Builder(Analyzer):
    
    def process(self, event):
        jets = getattr(event, self.cfg_ana.jets)
        jets = [jet for jet in jets if self.cfg_ana.filter_func(jet)]
        m3 = None
        pt3max=0
        seljets=None
        if len(jets)>=3:
            for l in list(itertools.permutations(jets,3)):
                pt3=(l[0].p4()+l[1].p4()+l[2].p4()).Pt()
                if pt3>pt3max:
                    ptmax=pt3
                    #seljets=[l[0],l[1],l[2]]
                    seljets=l

            top_pdgid = 6
            m3 = Resonance(seljets, top_pdgid)
        setattr(event, self.instance_label, m3)



