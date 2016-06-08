from heppy.framework.analyzer import Analyzer
from ROOT import TVector3, TFile, TH1F
from heppy.papas.path import Helix
import math

class ImpactParameter(Analyzer):
    '''This analyzer puts an impact parameter for every charged particle
    as an attribute of its path : particle.path.IP
    The significance is calculated, the calculus are a first order approximation,
    thus this may not be correct for large impact parameters (more than 3 mm)
    It also computes W, the likelihood value for the jet to contain beauty,
    using a likelihood ratio method for each particle in the jet.'''
        
    def process(self, event):
        assumed_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        for jet in jets:
            b_LL = 0
            ptcs_b_LL = []
            ptcs_IP = []
            ptcs_IP_signif = []
            for id, ptcs in jet.constituents.iteritems():
                if id in [22,130]:
                    continue
                for ptc in ptcs :
                    if ptc._charge == 0 :
                        continue
                    ptc.path.compute_IP(assumed_vertex,jet)
                    ptcs_IP.append(ptc.path.IP)
                    
                    if self.tag_jets:
                        ibin = self.ratio.FindBin(ptc.path.IP)
                        lhratio = self.ratio.GetBinContent(ibin)
                        if not lhratio == 0:
                            ptc.path.like_b = math.log(lhratio)
                        if lhratio == 0:
                            ptc.path.like_b = 0
                        ptcs_b_LL.append(ptc.path.like_b)
                        b_LL += ptc.path.like_b
                        
                    ptc_IP_signif = 0
                    if hasattr(ptc.path, 'points') == True :
                        if 'beampipe_in' in ptc.path.points:
                            ptc.path.compute_theta_0()
                            ptc.path.compute_IP_signif(ptc.path.IP,
                                                       ptc.path.theta_0,
                                                       ptc.path.points['beampipe_in'])
                            ptc_IP_signif = ptc.path.IP_signif
                    ptcs_IP_signif.append(abs(ptc_IP_signif))
                
            ptcs_IP_signif.sort(reverse=True)
            if len(ptcs_IP_signif) < 2:
                TCHE = -99
                TCHP = -99
            if len(ptcs_IP_signif) == 2:
                TCHE = ptcs_IP_signif[1]
                TCHP = -99
            if len(ptcs_IP_signif) > 2:
                TCHE = ptcs_IP_signif[1]
                TCHP = ptcs_IP_signif[2]
            
            jet.tags['b_LL'] = b_LL if self.tag_jets else None
            jet.tags['TCHE'] = TCHE
            jet.tags['TCHP'] = TCHP
        
        
    def beginLoop(self, setup):
        super(ImpactParameter, self).beginLoop(setup)
        if hasattr(self.cfg_ana, 'num') == False :
            if hasattr(self.cfg_ana, 'ratio') == False :
                #import pdb; pdb.set_trace()
                self.compute = False
                self.tag_jets = False
            else :
                self.tag_jets = True
                self.ratio_file = TFile.Open(self.cfg_ana.ratio[0],"read")
                self.ratio = self.ratio_file.Get(self.cfg_ana.ratio[1])
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
