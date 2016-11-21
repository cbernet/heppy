'''Computes the transverse mass (ANALYZER UNDER REVIEW)'''

from heppy.framework.analyzer import Analyzer
import math

class MTW(Analyzer):
    '''Computes the transverse mass.
    
    TODO: review the interface: a single collection of leptons must be provided
    self.cfg_ana.leptons 
    '''
    
    def process(self, event):
        ele = getattr(event, self.cfg_ana.electron)
        mu = getattr(event, self.cfg_ana.muon)

        lepton = ele[0] if len(ele)==1 else mu[0]  # this logic is bad

        met = getattr(event, self.cfg_ana.met)
        mtw = math.sqrt(2.*lepton.pt()*met.pt()*(1-math.cos(lepton.phi() - met.phi() )))
        
        setattr(event, self.instance_label, mtw)

