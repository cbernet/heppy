from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import matchObjectCollection, deltaR

class JetAnalyzer(Analyzer):

    
    def process(self, event):
        jets = getattr(event, self.cfg_ana.jets)
        genjets = getattr(event, self.cfg_ana.genjets)
        pairs = matchObjectCollection(jets, genjets, 0.3**2)
        for jet in jets:
            jet.gen = pairs[jet]
            if jet.gen:
                jet.dR = deltaR(jet.theta(), jet.phi(),
                                jet.gen.theta(), jet.gen.phi())
                # print jet.dR, jet, jet.gen
