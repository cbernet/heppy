from heppy.framework.analyzer import Analyzer
from ROOT import TFile, TH1F
from ROOT import TVector3, TLorentzVector
from heppy.papas.path import Helix
import math
from heppy.utils.deltar import deltaR

class ImpactParameter(Analyzer):
    '''This analyzer puts an impact parameter for every charged particle
    as an attribute of its path : particle.path.IP
    The significance is calculated, the calculus are a first order approximation,
    thus this may not be correct for large impact parameters (more than 3 mm)
    It also computes W, the likelihood value for the jet to contain beauty,
    using a likelihood ratio method for each particle in the jet.
    Computes TCHE and TCHP for the jet for b-tagging'''
        
    def process(self, event):
        assumed_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        enable_matter_scattering = self.cfg_ana.enable_matter_scattering
        for jet in jets:
            b_LL = 0
            ptcs_b_LL = []
            ptcs_pt = []
            ptcs_IP = []
            ptcs_IPxy = []
            ptcs_IPz = []
            ptcs_IP_signif = []
            ptcs_x_at_time_0 = []
            ptcs_y_at_time_0 = []
            ptcs_z_at_time_0 = []
            ptcs_dr = []
            for id, ptcs in jet.constituents.iteritems():
                if abs(id) in [22,130, 11]:
                    continue
                for ptc in ptcs :
                    if ptc._charge == 0 :
                        continue
                    ptc.path.compute_IP(assumed_vertex,jet)
                    
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
                    if hasattr(ptc.path, 'points') == True and 'beampipe_in' in ptc.path.points:
                        ptc.path.compute_theta_0()
                        ptc.path.compute_IP_signif(ptc.path.IP,
                                                   ptc.path.theta_0,
                                                   ptc.path.points['beampipe_in'])
                    else :
                        ptc.path.compute_IP_signif(ptc.path.IP, None, None)
                    
                    if ptc.path.p4.Perp() > 1 and (ptc.path.IPx**2 + ptc.path.IPy**2)**0.5 < 0.002 and ptc.path.IPz**2 < 0.17**2 :
                        
                        dr = deltaR(jet.eta(), jet.phi(), ptc.eta(), ptc.phi())
                        
                        ptcs_pt.append(ptc.path.p4.Perp())
                        ptcs_IP.append(ptc.path.IP)
                        ptcs_IPxy.append((ptc.path.IPx**2 + ptc.path.IPy**2)**0.5)
                        ptcs_IPz.append(ptc.path.IPz)
                        ptcs_IP_signif.append((ptc.path.IP_signif))
                        x, y, z = ptc.path.coord_at_time(0)
                        ptcs_x_at_time_0.append(x)
                        ptcs_y_at_time_0.append(y)
                        ptcs_z_at_time_0.append(z)
                        ptcs_dr.append(dr)
    
                ptcs_IP_signif_sorted = ptcs_IP_signif
                ptcs_IP_signif_sorted.sort(reverse=True)
            
            if len(ptcs_IP_signif) < 2:
                TCHE = -99
                TCHP = -99
                TCHE_IP = -99
                TCHP_IP = -99
                TCHE_x = -99
                TCHE_y = -99
                TCHE_z = -99
                TCHE_pt = -99
                TCHE_dr = -99
            if len(ptcs_IP_signif) == 2:
                TCHE = ptcs_IP_signif_sorted[1]
                TCHE_IP = ptcs_IP[ptcs_IP_signif.index(TCHE)]
                TCHE_x = ptcs_x_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_y = ptcs_y_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_z = ptcs_z_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_pt = ptcs_pt[ptcs_IP_signif.index(TCHE)]
                TCHE_dr = ptcs_dr[ptcs_IP_signif.index(TCHE)]
                TCHP = -99
                TCHP_IP = -99
                
            if len(ptcs_IP_signif) > 2:
                tche_index = 1
                
                #while ptcs_IP_signif_sorted[tche_index] > 30 and tche_index < len(ptcs_IP_signif_sorted)-2 :
                #    tche_index += 1
                
                TCHE = ptcs_IP_signif_sorted[tche_index]
                
                #while ptcs_pt[ptcs_IP_signif.index(TCHE)] < 1 and tche_index < len(ptcs_IP_signif_sorted)-2 :
                #    tche_index += 1
                #    TCHE = ptcs_IP_signif_sorted[tche_index]
                    
                #while ptcs_IPxy[ptcs_IP_signif.index(TCHE)] > 0.002 and tche_index < len(ptcs_IP_signif_sorted)-2 :
                #    tche_index += 1
                #    TCHE = ptcs_IP_signif_sorted[tche_index]
                    
                #while ptcs_IPz[ptcs_IP_signif.index(TCHE)]**2 > 0.17**2 and tche_index < len(ptcs_IP_signif_sorted)-2 :
                #    tche_index += 1
                #    TCHE = ptcs_IP_signif_sorted[tche_index]
                
                TCHE_IP = ptcs_IP[ptcs_IP_signif.index(TCHE)]
                TCHE_x = ptcs_x_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_y = ptcs_y_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_z = ptcs_z_at_time_0[ptcs_IP_signif.index(TCHE)]
                TCHE_pt = ptcs_pt[ptcs_IP_signif.index(TCHE)]
                TCHE_dr = ptcs_dr[ptcs_IP_signif.index(TCHE)]
                TCHP = ptcs_IP_signif_sorted[tche_index+1]
                TCHP_IP = ptcs_IP[ptcs_IP_signif.index(TCHP)]
                #while TCHE_x**2 + TCHE_y**2 - (0.05)**2 > 0 and TCHE_index < len(ptcs_IP_signif)-2:
                #    TCHE_index += 1
                #    TCHE = ptcs_IP_signif_sorted[TCHE_index]
                #    TCHE_x = ptcs_x_at_time_0[ptcs_IP_signif.index(TCHE)]
                #    TCHE_y = ptcs_y_at_time_0[ptcs_IP_signif.index(TCHE)]
                #if TCHE_x**2 + TCHE_y**2 - (0.05)**2 > 0:
                #    TCHE = -99
                #    TCHP = -99
                #    TCHE_IP = -99
                #    TCHP_IP = -99
                #    TCHE_x = -99
                #    TCHE_y = -99
                #   TCHE_z = -99
                #else:
                #    TCHE_IP = ptcs_IP[ptcs_IP_signif.index(TCHE)]
                #    TCHE_z = ptcs_z_at_time_0[ptcs_IP_signif.index(TCHE)]
                #    TCHP = ptcs_IP_signif_sorted[TCHE_index + 1]
                #    TCHP_IP = ptcs_IP[ptcs_IP_signif.index(TCHP)]
            #if TCHE > 30 and event.K0s == 0 and event.Kp == 0 and event.L0 == 0 and event.S0 == 0 and event.Sp == 0 and event.Sm == 0:
            #    import pdb; pdb.set_trace()
            
            jet.tags['b_LL'] = b_LL if self.tag_jets else None
            jet.tags['TCHE'] = TCHE
            jet.tags['TCHP'] = TCHP
            jet.tags['TCHE_IP'] = TCHE_IP
            jet.tags['TCHP_IP'] = TCHP_IP
            jet.tags['TCHE_x'] = TCHE_x
            jet.tags['TCHE_y'] = TCHE_y
            jet.tags['TCHE_z'] = TCHE_z
            jet.tags['TCHE_xy'] = (TCHE_x**2+TCHE_y**2)**0.5
            jet.tags['TCHE_pt'] = TCHE_pt
            jet.tags['TCHE_dr'] = TCHE_dr
            
            if hasattr(event, 'K0s') == True :
                jet.tags['K0s'] = event.K0s
            else :
                jet.tags['K0s'] = -99
            if hasattr(event, 'Kp') == True :
                jet.tags['Kp'] = event.Kp
            else :
                jet.tags['Kp'] = -99
            if hasattr(event, 'L0') == True :
                jet.tags['L0'] = event.L0
            else :
                jet.tags['L0'] = -99
            if hasattr(event, 'S0') == True :
                jet.tags['S0'] = event.S0
            else :
                jet.tags['S0'] = -99
            if hasattr(event, 'Sp') == True :
                jet.tags['Sp'] = event.Sp
            else :
                jet.tags['Sp'] = -99
            if hasattr(event, 'Sm') == True :
                jet.tags['Sm'] = event.Sm
            else :
                jet.tags['Sm'] = -99
            if hasattr(event, 'Muons') == True :
                jet.tags['Muons'] = event.Muons
            else :
                jet.tags['Muons'] = -99
        
        
    def beginLoop(self, setup):
        super(ImpactParameter, self).beginLoop(setup)
        if hasattr(self.cfg_ana, 'num') == False :
            self.tag_jets = False
            self.compute = False
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
