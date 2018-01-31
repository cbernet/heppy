'''Particle matcher.
'''
from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import matchObjectCollection, deltaR

import collections

class ResonanceMatcher(Analyzer):
    '''Matches L{resonances<heppy.particles.tlv.resonance>}.
    
    Example::
    
      from heppy.analyzers.ResonanceMatcher import ResonanceMatcher
      match = cfg.Analyzer(
        ResonanceMatcher,
        resonances='zeds',
        match_resonances='sel_zeds', 
        nmatch=2
        )
        
    @param resonances: The collection of L{resonances<heppy.particles.tlv.resonance>}
     to be matched
    
    @param match_resonances: The collection of L{resonances<heppy.particles.tlv.resonance>}
     to match to
     
    @param nmatch: Number of legs to be matched [1 or 2]. If 1, resonances are
     considered to be matched if they have one leg in common. If 2, if they
     have two legs in common.
     
    Example test configuration file in L{test_analysis_ee_ZZ_resmatch<heppy.test.test_analysis_ee_ZZ_resmatch>}
    '''
    
    def process(self, event):
        resonances = getattr(event, self.cfg_ana.resonances)
        match_resonances = getattr(event, self.cfg_ana.match_resonances)
        for resonance in resonances:
            resonance.matches = []
            for match_resonance in match_resonances:
                if self.cfg_ana.nmatch == 1:                    
                    for leg in resonance.legs:
                        if leg in match_resonance.legs:
                            resonance.matches.append(match_resonance)
                            break
                elif self.cfg_ana.nmatch == 2:
                    if sorted(resonance.legs) == sorted(match_resonance.legs):
                        resonance.matches.append(match_resonance)
                else:
                    raise ValueError('Resonance matcher can only match on 1 or 2 legs')
