from heppy.framework.analyzer import Analyzer
from ROOT import TVector3
from heppy.papas.path import Helix
import math

class ImpactParameter(Analyzer):
    '''This analyzer puts an impact parameter for every charged particle
    as an attribute of its path : particle.path.IP
    Then, it computes W, the likelihood value for the jet to contain beauty,
    using a likelihood ratio method for each particle in the jet.
    Above a given value for W, the jet is b-tagged'''
        
    def process(self, event):
        assumed_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        def func_b(IP):
            return 1
        def func_u(IP):
            return 1
        for jet in jets:
            jet.W = 0
            for id, ptcs in jet.constituents.iteritems():
                if id in [22,130]:
                    continue
                for ptc in ptcs :
                    if ptc._charge == 0 :
                        continue
                    ptc.path.compute_IP(assumed_vertex,jet)
                    u = func_u(ptc.path.IP)
                    b = func_b(ptc.path.IP)
                    ptc.path.like_b = math.log(1.0*b/u)
                    jet.W += ptc.path.like_b
            
