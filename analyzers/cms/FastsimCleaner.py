from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import matchObjectCollection, deltaR

import collections

class FastsimCleaner(Analyzer):

    def beginLoop(self, setup):
        super(FastsimCleaner, self).beginLoop(setup)
      
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        nhs = [ptc for ptc in particles if abs(ptc.pdgid())==130]
        chs = [ptc for ptc in particles if abs(ptc.pdgid())==211]

        pairs = matchObjectCollection(chs, nhs, 1e-5**2)

        # import pdb; pdb.set_trace()
        for ptc in chs: 
            match = pairs[ptc]
            if match: 
                # print 'found one!'
                # import pdb; pdb.set_trace()
                particles.remove(match)

