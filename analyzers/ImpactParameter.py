from heppy.framework.analyzer import Analyzer
from ROOT import TVector3, TFile, TH1F
from heppy.papas.path import Helix
import math

class ImpactParameter(Analyzer):
    '''This analyzer puts an impact parameter for every charged particle
    as an attribute of its path : particle.path.IP
    Then it computes W, the likelihood value for the jet to contain beauty,
    using a likelihood ratio method for each particle in the jet.'''
        
    def process(self, event):
        assumed_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        for jet in jets:
            b_LL = 0
            for id, ptcs in jet.constituents.iteritems():
                if id in [22,130]:
                    continue
                for ptc in ptcs :
                    if ptc._charge == 0 :
                        continue
                    ptc.path.compute_IP(assumed_vertex,jet)
                    if self.tag_jets:
                        ibin = self.ratio.FindBin(ptc.path.IP)
                        lhratio = self.ratio.GetBinContent(ibin)
                        ptc.path.like_b = math.log(lhratio)
                        b_LL += ptc.path.like_b
            jet.tags['b_LL'] = b_LL if self.tag_jets else None
        
        
    def beginLoop(self, setup):
        super(ImpactParameter, self).beginLoop(setup)
        if hasattr(self.cfg_ana, 'num') == False :
            #import pdb; pdb.set_trace()
            self.compute = False
            self.tag_jets = False
        else :
            if hasattr(self.cfg_ana, 'denom') == False :
                self.compute = False
                self.tag_jets = False
            else :
                self.tag_jets = True
                self.num_file = TFile.Open(self.cfg_ana.num[0],"read")
                self.num_hist = self.num_file.Get(self.cfg_ana.num[1])
                self.denom_file = TFile.Open(self.cfg_ana.denom[0],"read")
                self.denom_hist = self.denom_file.Get(self.cfg_ana.denom[1])
                self.ratio = TH1F("ratio","b over d",100,-0.001,0.001)
                self.ratio.Divide(self.num_hist,self.denom_hist)
                #import pdb; pdb.set_trace()
